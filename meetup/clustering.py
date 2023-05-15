import math
import pandas as pd
import geopandas as gp
import numpy as np
from typing import Optional
from .geo import (
    generate_group_centroids,
    get_network_graph,
    snap_points_to_street_network,
)
from .logging import logInfo, logWarning
from .caching import RunCache
from enum import Enum
from sklearn.neighbors import KDTree

from sklearn.cluster import KMeans, AffinityPropagation


class MeetingPointMethod(str, Enum):
    """
    Enum representing different strategies for generating a meeting point
    CENTROID : Simply take the centroid of the group
    CENTROID_SNAPED_TO_STREET: Calculate the centroid but then use the bike network graph to ensure that it's at a street intersection
    LANDMARK: Try to find landmarks close the centroid to use as the meeting spot
    """

    CENTROID = ("centroid",)
    CENTROID_SNAPED_TO_STREET = "centroid_snapped_to_street"


def cluster(clusterAlgo, df: gp.GeoDataFrame) -> gp.GeoDataFrame:
    """
    Apply the provided clustering algoritum and return a dataframe with the generated labels

    param clusterAlgo: The algorithum used to cluster the points. Must have a fit function (as in scipy) and expose a labels_ property after the fit
    param GeoDataFrame df: The DataFrame to cluster
    return GeoDataFrame: The input DataFrame with the clustering labels attached
    """

    assert getattr(
        clusterAlgo, "fit", None
    ), "clusterAlgo should be a valid clustering algoritum like KMeans or AffinityPropagation"
    assert callable(
        getattr(clusterAlgo, "fit", None)
    ), "clusterAlgo should be a valid clustering algoritum like KMeans or AffinityPropagation"

    clusters = clusterAlgo.fit(np.array(list(zip(df.geometry.x, df.geometry.y))))
    return gp.GeoDataFrame(df.assign(label=clusters.labels_))


def merge_clusters(df: gp.GeoDataFrame, minOccupancy: int):
    """
    Identifies clusters which are bellow the minimum occupancy threshold and tries to merge
    them with neighboring clusters.

    param GeoDataFrame df: The DataFrame to perform meges on
    return GeoDataFrame: The resulting DataFrame with the clusters merged
    """

    # Get a list of clusters that dont meet our min occupancy limit
    clusterValueCounts = df.label.value_counts()
    clustersToMerge = clusterValueCounts[clusterValueCounts < minOccupancy].index

    # Generate the centroids for the clusters
    clusterCentroids = generate_group_centroids(df).set_index("label")
    centroidCoords = [[geom.x, geom.y] for geom in clusterCentroids.geometry]

    # Build a KDTree using the cluster centroids
    tree = KDTree(centroidCoords)

    # Build a lookup to easily map between the tree indexes and the labels
    treeToFrameLookup = dict(
        zip(range(len(centroidCoords)), list(clusterCentroids.index))
    )

    # Keep track of the clusters we have merged already this iteration so we can exclude them from
    # future merge attempts

    clustersNotToConsider = []

    # Keep track of the mappings of mergers
    mergers = {}

    for clusterLabelToMerge in clustersToMerge:
        if clusterLabelToMerge in clustersNotToConsider:
            continue

        clusterCentroid = centroidCoords[
            list(clusterCentroids.index).index(clusterLabelToMerge)
        ]
        _, potentialMerges = tree.query([clusterCentroid], min(4, clusterCentroids.shape[0]))
        potentialMergerLabels = [
            treeToFrameLookup[index] for index in potentialMerges[0]
        ]

        # Filter the poetnital mergers to exclude self and things that have already been merged this turn
        potentialMergerLabels = [
            label
            for label in potentialMergerLabels
            if label != clusterLabelToMerge and not label in clustersNotToConsider
        ]

        if len(potentialMergerLabels) == 0:
            continue

        # Get the sizes of the potental mergers
        potentialMergerSizes = clusterValueCounts.loc[potentialMergerLabels]
        # Select the smallest
        smallestAvaliableCluster = potentialMergerSizes.idxmin()

        # Use this as the merge target
        mergers[clusterLabelToMerge] = smallestAvaliableCluster

        # Record both the current cluster and the merge in the exclusing list
        clustersNotToConsider.append(clusterLabelToMerge)
        clustersNotToConsider.append(smallestAvaliableCluster)

    # Perform the merges
    df["label"] = df["label"].apply(
        lambda label: mergers[label] if label in mergers else label
    )
    return df


def improve_clusters(
    df, minOccupancy: Optional[int], maxOccupancy: Optional[int], maxIters: int = 10
) -> gp.GeoDataFrame:
    """
    Itteratively try to get the clusters between the specified min and max Occupancy. Gives up after maxIters

    param GeoDataFrame df: The DataFrame of clusters to attempt to improve
    param Optional[int] minOccupancy: If specified, the minimum occupancy that each cluster should attempt to reach
    param Optional[int] maxOccupancy: If specified, the maximm occupancy that each cluster should attempt to reach
    param int maxIters: The maximum merge, split iterations to attempt before giving up

    return GeoDataFrame: The resulting DataFrame with the hopefully improved clusters

    """
    improvedClusters = df.copy()
    for iteration in range(0, maxIters):
        if maxOccupancy is not None:
            improvedClusters = split_clusters(improvedClusters, maxOccupancy)

        if minOccupancy is not None:
            improvedClusters = merge_clusters(improvedClusters, minOccupancy)

        cluster_counts = improvedClusters.label.value_counts()

        allClustersOverMinOccupancy = (
            True if minOccupancy is None else (cluster_counts >= minOccupancy).all()
        )
        allClustersUndexMaxOccupancy = (
            True if maxOccupancy is None else (cluster_counts <= maxOccupancy).all()
        )

        numberUnderThreshold = (cluster_counts < minOccupancy).sum()
        numberOverThreshold = (cluster_counts > maxOccupancy).sum()

        logInfo(
            f"After {iteration+1} iterations, we have {numberUnderThreshold} clusters smaller min and {numberOverThreshold} larger than max"
        )

        if allClustersOverMinOccupancy and allClustersUndexMaxOccupancy:
            logInfo("🎉 We succesfully managed to tame the groups!")
            return improvedClusters

    logWarning(
        f"😭 After {maxIters} tries, we where unable to get all groups within the given ranges. Either increase the number of iterations or relax parameters"
    )
    # After maxIters reached, give up and return the clusters as is
    return improvedClusters


def split_clusters(df, maxOccupancy: int = 40):
    """
    Split clusters which are above the occpancy threshold in to smaller clusters by internally clustering using KMeans
    We generate n new clusters where n is the ceiling of the current cluster count divided by the maximum occupancy

    param GeoDataFrame df: The input dataframe, it should have the following fields "label", "geometry"
    param int maxOccupancy: The maximum occupancy of each group. Defaults to 40
    """

    # Identify the clusters which are above the occupancy threshold
    cluster_value_counts = df.label.value_counts()
    clusters_to_split = cluster_value_counts[cluster_value_counts > 40].index
    split_clusters = df.copy()

    for cluster_label_to_split in clusters_to_split:
        target_cluster = df[df.label == cluster_label_to_split]
        # Calculate the number of clusters we will attempt to splut this cluster into. We try to
        # split the current cluster into n sub clusters close to the maxOccupancy
        target_no_splits = math.ceil(target_cluster.shape[0] / maxOccupancy)

        # Run the KMeans clustering on the target cluster
        sub_cluster = cluster(
            KMeans(n_clusters=target_no_splits, n_init="auto"), target_cluster
        )

        # We reasign the cluster labels starting with 1 greater than the maximun existing label number
        max_existing_label = split_clusters.label.max()
        sub_cluster.label = sub_cluster.label + max_existing_label + 1
        split_clusters = gp.GeoDataFrame(
            pd.concat(
                [
                    split_clusters[split_clusters.label != cluster_label_to_split],
                    sub_cluster,
                ],
                axis=0,
            )
        )

    # Finally we reindex the labels so that they are sequential
    unique_labels = split_clusters.label.drop_duplicates().sort_values().values
    label_remap = dict(zip(unique_labels, range(0, unique_labels.shape[0])))
    split_clusters.label = split_clusters.label.apply(
        lambda old_label: label_remap[old_label]
    )

    # Return the resulting clusters
    return split_clusters


def generate_group_meeting_points(
    df: gp.GeoDataFrame, method: Optional[MeetingPointMethod]
) -> gp.GeoDataFrame:
    """
    Generates the meeting point for each group.
    param: GeoDataFrame df: A DataFrame with each users location and group assignment
    param: MeetingPointMethod method: Specify the method used to calculate the meeting point

    returns: A GeoDataFrame with the centroids for each label and any additional info (depends on method)
    """

    if method is None:
        method = MeetingPointMethod.CENTROID

    group_centroids = generate_group_centroids(df)

    match method:
        case MeetingPointMethod.CENTROID:
            logInfo("Generating meeting points for each group using their centroids")
            return group_centroids
        case MeetingPointMethod.CENTROID_SNAPED_TO_STREET:
            logInfo(
                "Generating meeting points for each group by snapping their centroids to the street network"
            )
            bounds = df.to_crs("epsg:4326").total_bounds
            network = get_network_graph(tuple(bounds), crs=df.crs)
            return snap_points_to_street_network(group_centroids, network)


def format_results(
    users: gp.GeoDataFrame, meetingPoints: gp.GeoDataFrame
) -> pd.DataFrame:
    """
    Formats the results to fit the requirments
    param: GeoDataFrame users: The list of users with their group assigments in the label column
    param: GeoDataFrame meetingPoints: A dataframe with each meeting point for each label

    returns: A pandas DataFrame with the required columns
    """

    latLngMeetingPoints = meetingPoints.to_crs("epsg:4326")
    latLngMeetingPoints = latLngMeetingPoints.assign(
        start_point_latitude=latLngMeetingPoints.geometry.y,
        start_point_longitude=latLngMeetingPoints.geometry.x,
    )

    groupAssignments = (
        users.groupby("label")
        .user_id.apply(
            lambda user_ids: ",".join([str(user_id) for user_id in user_ids])
        )
        .reset_index()
    )
    groupAssignments = groupAssignments.rename(
        columns={"user_id": "potential_group_members"}
    )

    result = (
        users[["user_id", "label"]]
        .merge(latLngMeetingPoints, on="label", how="left")
        .merge(groupAssignments, on="label", how="left")
    )
    result = result.rename(columns={"label": "start_point_id"}).drop("geometry", axis=1)
    return result


def run_clustering(
    df: gp.GeoDataFrame,
    minGroupOccupancy: Optional[int],
    maxGroupOccupancy: Optional[int],
    maxIters: Optional[int],
) -> gp.GeoDataFrame:
    """
    Runs the clustering algorithum on the cleaned data. This uses AffinityPropogation to produce a set of
    inital clusters and then iteratively tried to join and merge them to meet the minimum and maximum
    cluster criteria
    """

    # Step 1 : Use AffinityPropogation to generate inital proposal clusters, load from cache if possible

    inital_clusters = RunCache.get_cached_geo_data_frame("inital_clusters")

    if inital_clusters is None:
        logInfo(
            f"[bold yellow]🔬[/bold yellow] Attempting to generate groups. Depending on the number of users this might take a few mins"
        )
        inital_clusters = cluster(AffinityPropagation(damping=0.95, verbose=True), df)
        RunCache.cache_geo_data_frame("inital_clusters", inital_clusters)
    else:
        logInfo("Loaded inital clusters from cache")

    logInfo(
        f"Got inital groups. We found [bold white]{inital_clusters.label.max() +1 }[/bold white] of them."
    )

    # Step 2 : If bounds for the cluster sizes specified, iteratively try to improve the clusters based on min and max group occupancy
    if minGroupOccupancy is not None or maxGroupOccupancy is not None:
        iterations = maxIters if maxIters is not None else 10
        logInfo(f"Refining groups to try and get them within the specified range. Will run {iterations} times")
        reduced_clusters = improve_clusters(
            inital_clusters, minGroupOccupancy, maxGroupOccupancy, iterations 
        )
        return reduced_clusters

    return inital_clusters
