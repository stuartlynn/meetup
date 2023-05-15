from numpy.testing import assert_equal
from meetup.geo import generate_group_centroids, generate_cluster_convex_hull
import pandas as pd 
import geopandas as gp
from .helpers import square_cluster, circle_cluster

from math import isclose


def test_group_centroids():
    group1 = circle_cluster(10,10,5, 20,0)
    group2 = circle_cluster(20,20,5, 40,1)
    allPoints = gp.GeoDataFrame(pd.concat([group1,group2]))
    centroids  = generate_group_centroids(allPoints)

    assert_equal(centroids.shape[0], 2, "Should only have two centroids")
    assert "geometry" in centroids.columns, "Result should have geometry column"
    assert 0 in centroids.index, "0 label should be present"
    assert 1 in centroids.index, "0 label should be present"

    assert isclose(centroids.iloc[0].geometry.x, 10), "Cluster 1 should be centerd on 10, 10"
    assert isclose(centroids.iloc[0].geometry.y, 10), "Cluster 2 should be centered on 20, 20"

    assert isclose(centroids.iloc[1].geometry.x, 20), "Cluster 1 should be centerd on 10, 10"
    assert isclose(centroids.iloc[1].geometry.y, 20), "Cluster 2 should be centered on 20, 20"


def test_generate_convex_hulls():
    group1 = square_cluster(10,10,10,0)
    group2 = square_cluster(20,20,20,1)

    allPoints = gp.GeoDataFrame(pd.concat([group1,group2]))
    hulls= generate_cluster_convex_hull(allPoints)

    assert "geometry" in hulls.columns, "Result should have geometry column"
    assert 0 in hulls.index, "0 label should be present"
    assert 1 in hulls.index, "0 label should be present"

    assert_equal(hulls.shape[0], 2, "Should only have two centroids")
    assert isclose(hulls.iloc[0].geometry.length, 10*4)
    assert isclose(hulls.iloc[1].geometry.length, 20*4)

    print(hulls)
