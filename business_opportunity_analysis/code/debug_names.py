import pandas as pd
import geopandas as gpd

def debug():
    print("--- Neighborhoods GeoJSON ---")
    gdf = gpd.read_file("../data/neighborhoods.geojson")
    print(gdf['AREA_NAME'].head(10).tolist())
    
    print("\n--- Neighborhood Profiles CSV ---")
    df = pd.read_csv("../data/neighborhood_profiles.csv", nrows=5)
    print(df.columns.tolist()[:20]) # Print first 20 columns

if __name__ == "__main__":
    debug()
