import requests
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import os
import zipfile
import io

# URLs
NEIGHBOURHOODS_URL = "https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/fc443770-ef0a-4025-9c2c-2cb558bfab00/resource/5e7c8234-f805-43a8-9a6e-f96b3db20984/download/neighbourhoods-4326.zip"
DINESAFE_URL = "https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/b6b4f3fb-2e2c-47e7-931d-b87d22806948/resource/e9df9d33-727e-4758-9a84-67ebefec1453/download/dinesafe.json"

# Files
NEIGHBOURHOODS_FILE = "../data/neighbourhoods.zip"
DINESAFE_FILE = "../data/dinesafe.json"

def download_file(url, filename):
    # Always download to ensure we have a valid file
    print(f"Downloading {filename}...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded {filename}.")
    else:
        print(f"Failed to download {filename}. Status code: {response.status_code}")

def analyze():
    # Download data
    download_file(NEIGHBOURHOODS_URL, NEIGHBOURHOODS_FILE)
    download_file(DINESAFE_URL, DINESAFE_FILE)

    # Define Harborfront Bounding Box (Approximate)
    # South of Gardiner (approx 43.645), between Bathurst and Yonge/Jarvis
    min_lat = 43.630
    max_lat = 43.648 # Lowered from 43.655 to exclude Queen St/King St
    min_lon = -79.410
    max_lon = -79.360

    print(f"Filtering for Harborfront (Lat: {min_lat}-{max_lat}, Lon: {min_lon}-{max_lon})...")

    # Load DineSafe
    print("Loading DineSafe...")
    df_dinesafe = pd.read_json(DINESAFE_FILE)
    
    # Create GeoDataFrame from DineSafe
    # DineSafe has 'Latitude' and 'Longitude'
    # Drop rows with NaN lat/lon
    df_dinesafe = df_dinesafe.dropna(subset=['Latitude', 'Longitude'])
    
    geometry = [Point(xy) for xy in zip(df_dinesafe['Longitude'], df_dinesafe['Latitude'])]
    gdf_dinesafe = gpd.GeoDataFrame(df_dinesafe, geometry=geometry, crs="EPSG:4326")

    # Spatial Filter using Bounding Box
    gdf_harborfront = gdf_dinesafe.cx[min_lon:max_lon, min_lat:max_lat]
    print(f"Found {len(gdf_harborfront)} establishments in Harborfront area.")

    # Identify Vegetarian/Vegan
    veg_keywords = ["Vegetarian", "Vegan", "Plant", "Green"]
    veg_restaurants = gdf_harborfront[
        gdf_harborfront['Establishment Name'].str.contains('|'.join(veg_keywords), case=False, na=False) |
        gdf_harborfront['Establishment Type'].str.contains('|'.join(veg_keywords), case=False, na=False)
    ]

    # Identify Grocery Stores
    grocery_keywords = ["Grocery", "Supermarket", "Market", "Loblaws", "Sobeys", "Metro", "Rabba", "Longos", "Farm Boy", "No Frills", "FreshCo"]
    grocery_stores = gdf_harborfront[
        gdf_harborfront['Establishment Name'].str.contains('|'.join(grocery_keywords), case=False, na=False) |
        gdf_harborfront['Establishment Type'].str.contains("Supermarket", case=False, na=False) |
        gdf_harborfront['Establishment Type'].str.contains("Food Store", case=False, na=False)
    ]
    
    # Identify Cheap Grocery Stores
    cheap_keywords = ["No Frills", "FreshCo", "Food Basics", "Walmart", "Giant Tiger"]
    cheap_grocery = grocery_stores[
        grocery_stores['Establishment Name'].str.contains('|'.join(cheap_keywords), case=False, na=False)
    ]

    # Generate Report
    with open("harborfront_food_options.md", "w") as f:
        f.write("# Harborfront Food Options\n\n")
        
        f.write("## Vegetarian & Vegan Friendly Restaurants\n")
        if not veg_restaurants.empty:
            f.write(veg_restaurants[['Establishment Name', 'Establishment Address', 'Establishment Type']].to_markdown(index=False))
        else:
            f.write("No specific vegetarian/vegan named restaurants found in this area.\n")
        f.write("\n\n")
        
        f.write("## Cheap Grocery Stores\n")
        if not cheap_grocery.empty:
            f.write(cheap_grocery[['Establishment Name', 'Establishment Address', 'Establishment Type']].to_markdown(index=False))
        else:
            f.write("No specific budget grocery chains (No Frills, FreshCo, etc.) found in the immediate Harborfront area.\n")
        f.write("\n\n")

        f.write("## All Grocery Options\n")
        if not grocery_stores.empty:
            f.write(grocery_stores[['Establishment Name', 'Establishment Address', 'Establishment Type']].to_markdown(index=False))
        else:
            f.write("No grocery stores found.\n")
            
    print("Report generated: harborfront_food_options.md")

if __name__ == "__main__":
    analyze()
