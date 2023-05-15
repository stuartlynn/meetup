import math 
import geopandas as gp
from sklearn.datasets import make_blobs

def circle_cluster(centerX:float, centerY:float, radius:float, points:int, label:int):
    radi = [ 2.0*math.pi*i/points for i in  range(points)]
    x = [centerX + radius * math.sin(alpha) for alpha in radi]
    y = [centerY + radius * math.cos(alpha) for alpha in radi]
    return gp.GeoDataFrame({"label":[label]*points}, geometry = gp.points_from_xy(x,y),crs="epsg:4326")

def square_cluster(centerX:float, centerY:float, side:float, label:int):
    halfSide = side/2
    x=  [centerX -halfSide, centerX+halfSide, centerX+halfSide, centerX-halfSide]
    y=  [centerY -halfSide, centerY-halfSide, centerY+halfSide, centerY+halfSide]

    return gp.GeoDataFrame({"label":[label]*4}, geometry = gp.points_from_xy(x,y),crs="epsg:4326")


def blob_cluster(centerX:float, centerY:float, points:int, stdDev:float,label:int):
    points, _ = make_blobs(n_samples=points, n_features=2,centers=[[centerX,centerY]], cluster_std=stdDev)
    geometry = gp.points_from_xy(points[:,0], points[:,1])

    return gp.GeoDataFrame( geometry=geometry, crs="epsg:4326").assign(label=label) 

