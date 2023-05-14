import geopandas as gp
import pandas as pd
import osmnx as ox
from networkx import MultiDiGraph
from typing import Optional
from geopandas import GeoDataFrame
from networkx import MultiDiGraph
from shapely import MultiPoint
from meetup.logging import logInfo, logWarning
from collections.abc import Iterable
from meetup.caching import RunCache


def clean_user_locations(userLocations: pd.DataFrame) -> pd.DataFrame:
    """
    Takes a standardized input DataFrame and cleans it. Currently just means dealing with repeat user_ids in the dataset by
    taking their median.

    :param DataFrame userLocations: the DataFrame of user locations to clearn
    """
    users_with_duplicates = (
        (userLocations.groupby("user_id").count() > 1).sum().latitude
    )
    if users_with_duplicates > 0:
        logWarning(
            f"""Found [bold white]{users_with_duplicates}[/bold white] users who had multiple entries in the input file. 
        Taking their starting location to be the centroid of their reported locations"""
        )
    return userLocations.groupby("user_id").median().reset_index()


def load_user_locations(
    filePath: str,
    latCol: Optional[str] = "latitude",
    lngCol: Optional[str] = "longitude",
    userIdCol: Optional[str] = "user_id",
) -> gp.GeoDataFrame:
    """
    Loads the user location file, checks to see that it contains the required columns and standardizes column names.
    Also transforms the dataframe to a local CRS

    :param str filePath: The path to the input file
    :param str latCol: The column in the file that represents the latitude
    :param str lngCol: The column in the file that represents the longitude
    :param str userIdCol: The column in the file that represents the unique user id

    :return GeoDataFrame: The loaded and standardized dataframe.
    """
    userLocations = pd.read_csv(filePath)
    assert (
        userIdCol in userLocations.columns
    ), f"The supplied user_id column: {userIdCol} is not present in the supplied input file"
    assert (
        latCol in userLocations.columns
    ), f"The supplied latitude column: {latCol} is not present in the supplied input file"
    assert (
        lngCol in userLocations.columns
    ), f"The supplied longitude column: {lngCol} is not present in the supplied input file"
    userLocations.rename(
        columns={lngCol: "longitude", latCol: "latitude", userIdCol: "user_id"},
        inplace=True,
    )

    userLocations = clean_user_locations(userLocations)

    userLocations = gp.GeoDataFrame(
        userLocations,
        geometry=gp.points_from_xy(userLocations[lngCol], userLocations[latCol]),
        crs="epsg:4326",
    )

    logInfo(f"Found {userLocations.shape[0]} users!")

    # Guess the local crs and transfrorm to it
    crs = userLocations.estimate_utm_crs()
    userLocations.to_crs(crs, inplace=True)
    return userLocations


def snap_points_to_street_network(
    points: gp.GeoDataFrame, network: MultiDiGraph
) -> gp.GeoDataFrame:
    """
    Takes a GeoSeries of points and snaps then to the provided network

    :param GeoDataFrame points: The GeoSeries to be snapped
    :param MultiDiGraph network: The network to snap them to

    :return GeoSeries: The snapped points.
    """
    nodeIds = ox.nearest_nodes(network, points.geometry.x, points.geometry.y)

    if not isinstance(nodeIds, Iterable):
        raise Exception("osmx returned wrong type for nearest nodes")

    nodes = [network.nodes[nodeId] for nodeId in nodeIds]
    snappedPoints = gp.points_from_xy(
        [node["x"] for node in nodes], [node["y"] for node in nodes]
    )
    return gp.GeoDataFrame(points[["label"]], geometry=snappedPoints, crs=points.crs)


def generate_group_centroids(clusteredUsers: gp.GeoDataFrame) -> gp.GeoDataFrame:
    """
    Takes a DataFrame of points with labels and generates the centroid for each label

    :param GeoDataFrame clusteredUsers: The DataFrame containing the labeled points to find the centroids of

    :return GeoSeries: The centroids of each group.
    """
    centroids = GeoDataFrame(
        clusteredUsers.groupby("label")
        .geometry.apply(lambda points: MultiPoint(points.values).centroid)
        .reset_index()
    )
    return centroids.set_crs(clusteredUsers.crs)


def find_landmarks_near_centroids(centroids: gp.GeoDataFrame) -> gp.GeoDataFrame:
    return gp.GeoDataFrame(centroids, crs=centroids.crs)


def get_network_graph(
    bounds: tuple[float, float, float, float], mode="bike", crs="epsg:4326"
) -> MultiDiGraph:
    """
    dowloads and caches the network graph for a bounded region

    :param [number] bounds: the bounds in format []
    """
    logInfo(f"Getting bike network for region {bounds}")
    network = RunCache.get_network("cycle_network")
    if network is None:
        network = ox.graph_from_bbox(
            bounds[3], bounds[1], bounds[2], bounds[0], network_type=mode
        )
        network = ox.project_graph(network, crs)
        RunCache.set_network("cycle_network", network)
    return network


def generate_cluster_convex_hull(
    df: GeoDataFrame, groupBy: str = "label", geometryCol: str = "geometry"
):
    """
    Helper method to generate a convex hull around groups in the supplied GeoDataFrame

    :param GeoDataFrame df: The GeoDataFrame containing the geometries to group and convex hull
    :param str groupBy: The key to use in the groupby query
    :param str geometryCol: The geometry column to use
    """
    hulls = df.groupby(groupBy).apply(
        lambda group: gp.GeoSeries(MultiPoint(list(group[geometryCol])).convex_hull)
    )
    hulls = hulls.rename(columns={0: geometryCol})
    return gp.GeoDataFrame(hulls, crs=df.crs)
