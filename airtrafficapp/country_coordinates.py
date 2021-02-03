import geopandas as gpd
import pandas as pd

# Access built-in Natural Earth data via GeoPandas
world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))

# Get a list (dataframe) of country centroids
centroids = world.centroid
centroid_list = pd.concat([world.name, centroids], axis=1)
print(centroid_list.head())
# Plot the results
# base = world.plot(column="name", cmpa="Blues")
# centroids.plot(ax=base, marker="o", color="red", markersize=5)

