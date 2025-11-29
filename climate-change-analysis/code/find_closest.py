import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

# Coordinates for Kensington-Chinatown (approximate center)
# Latitude: 43.6538, Longitude: -79.3993
target_lat = 43.6538
target_lon = -79.3993

def find_closest_installation():
    try:
        # Load shapefile
        gdf = gpd.read_file("../data/renewable_energy_shp")
        
        # Create a GeoDataFrame for the target location
        target_point = Point(target_lon, target_lat)
        target_gdf = gpd.GeoDataFrame(geometry=[target_point], crs="EPSG:4326")
        
        # Ensure both are in the same CRS. 
        # The shapefile seems to be in WGS84 (EPSG:4326) based on the filename, 
        # but for accurate distance calculation in meters, we should project to UTM.
        # Toronto is in UTM Zone 17N (EPSG:32617).
        
        if gdf.crs is None:
            gdf.set_crs("EPSG:4326", inplace=True)
            
        gdf_projected = gdf.to_crs("EPSG:32617")
        target_projected = target_gdf.to_crs("EPSG:32617")
        
        # Calculate distance (in meters)
        # We calculate distance from the single target point to all points in gdf
        gdf_projected['distance_m'] = gdf_projected.geometry.distance(target_projected.geometry.iloc[0])
        
        # Filter for installations within 1.5 km (1500 meters)
        nearby = gdf_projected[gdf_projected['distance_m'] <= 1500].copy()
        
        if nearby.empty:
            print("No installations found within 1.5 km.")
            return

        # Clean Installation Year
        # R_YR_INSTA might be string or have invalid values
        nearby['R_YR_INSTA'] = pd.to_numeric(nearby['R_YR_INSTA'], errors='coerce')
        
        # Sort by Year (descending) and then Distance (ascending)
        # We want the LATEST installation. If ties, the closest one.
        nearby_sorted = nearby.sort_values(by=['R_YR_INSTA', 'distance_m'], ascending=[False, True])
        
        # Get the top result
        latest = nearby_sorted.iloc[0]
        
        print("-" * 30)
        print("Latest Renewable Energy Installation near Kensington-Chinatown")
        print("-" * 30)
        print(f"Location: {latest['R_LOCATION']}")
        print(f"Building: {latest['R_BUILDING']}")
        print(f"Technology: {latest['R_TYPE']}")
        print(f"Size: {latest['R_SIZE']} kW")
        print(f"Year Installed: {int(latest['R_YR_INSTA']) if pd.notna(latest['R_YR_INSTA']) else 'Unknown'}")
        print(f"Distance: {latest['distance_m']:.2f} meters")
        print("-" * 30)
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    find_closest_installation()
