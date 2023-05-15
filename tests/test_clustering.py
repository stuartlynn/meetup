from meetup.clustering import split_clusters, merge_clusters
from numpy.testing import assert_equal
from .helpers import blob_cluster
import pandas as pd 
import geopandas as gp

def test_split_clusters():
    cluster1 = blob_cluster(10, 10 ,10,0.02, 0)
    cluster2 = blob_cluster(10, 10 ,200,0.02, 1)
    allClusters = gp.GeoDataFrame(pd.concat([cluster1, cluster2]))
    splitClusters = split_clusters(allClusters, 100)
    
    assert_equal(splitClusters.label.max(), 2, "Should have 3 clusters after spliting")
    assert_equal(splitClusters[splitClusters.label== 0].shape[0], 10, "Cluster 0 should remain intact" )

def test_merge_clusters():
    cluster3 = blob_cluster(15, 10 ,200,0.02, 0)
    cluster1 = blob_cluster(10, 10 ,10,0.02, 1)
    cluster2 = blob_cluster(10, 15 ,40,0.02, 2)
    allClusters = gp.GeoDataFrame(pd.concat([cluster1, cluster2, cluster3]))
    splitClusters = merge_clusters(allClusters, 20)

    assert 0 in splitClusters.label.unique(), "Should have cluster 0 after spliting"
    assert 2 in splitClusters.label.unique(), "Should have cluster 2 after spliting"
    assert 1 not in splitClusters.label.unique(), "Should not have cluster 1 after spliting"
    assert_equal(splitClusters[splitClusters.label== 0].shape[0], 200, "Cluster 0 should remain intact" )
    assert_equal(splitClusters[splitClusters.label== 2].shape[0], 50, "Cluster 1 should have been absorbed in to cluster 2" )
    assert_equal(splitClusters[splitClusters.label== 1].shape[0], 0, "Cluster 1 should have been absorbed in to cluster 2" )



