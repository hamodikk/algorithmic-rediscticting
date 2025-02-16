import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

# Load the Washington State counties shapefile
shapefile_path = "WA_County_Boundaries.shp"
geo_df = gpd.read_file(shapefile_path)

# Load the redistricted counties csv data
redistricted_data = pd.read_csv("redistricted_counties.csv")

# Standardize column names before merging
geo_df["JURISDIC_3"] = geo_df["JURISDIC_3"].str.lower().str.strip().str.replace(" county", "", regex=True)
redistricted_data["county"] = redistricted_data["county"].str.lower().str.strip().str.replace(" county", "", regex=True)

# Merge shape data with district assignments
geo_df = geo_df.merge(redistricted_data, left_on="JURISDIC_3", right_on="county", how="left")

# Manually assign King and Pierce counties to district 7 and 8
geo_df.loc[geo_df["JURISDIC_3"] == "king", "district"] = 7
geo_df.loc[geo_df["JURISDIC_3"] == "pierce", "district"] = 8

# Plot the redistricted map
fig, ax = plt.subplots(figsize=(10, 10))
geo_df.plot(column="district", cmap="tab10", linewidth=0.8, edgecolor="black", legend=True, ax=ax)
ax.set_title("Washington State Redistricting Plan")
plt.show()