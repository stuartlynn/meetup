import seaborn as sns
import matplotlib.pyplot as plt
import geopandas as gp
from meetup.geo import generate_cluster_convex_hull
from pathlib import Path


def generate_report(df, outFile: Path):
    plot_clusters(df)


def plot_clusters(df: gp.GeoDataFrame):
    cluster_counts = df.label.value_counts()
    colors = sns.color_palette(n_colors=cluster_counts.shape[0])
    convex_hulls = generate_cluster_convex_hull(df)
    _, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(20, 35))
    convex_hulls.plot(ax=ax1, facecolor="none")
    df.plot(ax=ax1, c=df.label.apply(lambda label: colors[label]), markersize=2)
    cluster_counts.hist(bins=20, ax=ax2)
