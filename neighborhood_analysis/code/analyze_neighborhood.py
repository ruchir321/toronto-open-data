import os
import requests
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from shapely.ops import nearest_points

# Constants
DATA_DIR = "data"
OUTPUT_FILE = "neighborhood_report.md"
# College and Beverly coordinates (approximate)
TARGET_LAT = 43.656
TARGET_LON = -79.394
TARGET_POINT = Point(TARGET_LON, TARGET_LAT)
SEARCH_RADIUS_KM = 1.0

# Dataset URLs
DATASETS = {
    "parks": "https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/cbea3a67-9168-4c6d-8186-16ac1a795b5b/resource/a43dddd5-9457-4ac4-b7c1-e65d23ca5b09/download/parks-and-recreation-facilities-2952.geojson",
    "crimes": "https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/21db0f45-1828-4fa3-94de-db92f454314c/resource/3c3925de-3a85-476a-85ca-b3cdff91b47f/download/neighbourhood-crime-rates-4326.csv",
    "cycling": "https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/abbe5ee3-e249-4f86-a219-f0022eaddcc9/resource/023da9a2-8848-4e10-9cad-e7f9119cd874/download/cycling-network-4326.geojson",
    "neighbourhoods": "https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/fc443770-ef0a-4025-9c2c-2cb558bfab00/resource/0719053b-28b7-48ea-b863-068823a93aaa/download/neighbourhoods-4326.geojson",
    "places": "https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/965247c0-c72e-49b4-bb1a-879cf98e1a32/resource/d3e9668a-1c2b-4250-8aba-32a80bb2266d/download/places-of-interest-and-attractions-4326.geojson"
}

def download_data():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    paths = {}
    for name, url in DATASETS.items():
        filename = url.split("/")[-1]
        filepath = os.path.join(DATA_DIR, filename)
        paths[name] = filepath
        if not os.path.exists(filepath):
            print(f"Downloading {name}...")
            try:
                r = requests.get(url)
                r.raise_for_status()
                with open(filepath, "wb") as f:
                    f.write(r.content)
            except Exception as e:
                print(f"Failed to download {name}: {e}")
        else:
            print(f"{name} already exists.")
    return paths

def analyze_leisure(parks_path):
    print("Analyzing Leisure...")
    try:
        gdf = gpd.read_file(parks_path)
        # Ensure CRS is projected for distance calculation (e.g., EPSG:3857 for meters)
        gdf = gdf.to_crs(epsg=3857)
        target_projected = gpd.GeoSeries([TARGET_POINT], crs="EPSG:4326").to_crs(epsg=3857).iloc[0]
        
        # Buffer 1km
        buffer = target_projected.buffer(SEARCH_RADIUS_KM * 1000)
        nearby = gdf[gdf.geometry.intersects(buffer)]
        
        return nearby
    except Exception as e:
        print(f"Error analyzing leisure: {e}")
        return gpd.GeoDataFrame()

def analyze_crime(crime_path, neighborhood_name):
    print(f"Analyzing Crime for {neighborhood_name}...")
    try:
        df = pd.read_csv(crime_path)
        df['AREA_NAME_NORM'] = df['AREA_NAME'].str.lower().str.strip()
        target_norm = neighborhood_name.lower().strip()
        
        hood_data = df[df['AREA_NAME_NORM'] == target_norm]
        if hood_data.empty:
            hood_data = df[df['AREA_NAME_NORM'].str.contains(target_norm, regex=False)]
            
        if not hood_data.empty:
            row = hood_data.iloc[0]
            stats = {}
            for col in df.columns:
                if '2023' in col and col not in ['POPULATION_2024', 'AREA_NAME']: # The model hallucinated the column name "POPULATION_2023". The table actually has "POPULATION_2024"
                    stats[col] = row[col]
            return stats
        else:
            return {}
    except Exception as e:
        print(f"Error analyzing crime: {e}")
        return {}

def analyze_transit(cycling_path):
    print("Analyzing Transit...")
    try:
        gdf = gpd.read_file(cycling_path)
        gdf = gdf.to_crs(epsg=3857)
        target_projected = gpd.GeoSeries([TARGET_POINT], crs="EPSG:4326").to_crs(epsg=3857).iloc[0]
        
        buffer = target_projected.buffer(SEARCH_RADIUS_KM * 1000)
        nearby = gdf[gdf.geometry.intersects(buffer)]
        return nearby
    except Exception as e:
        print(f"Error analyzing transit: {e}")
        return gpd.GeoDataFrame()

def analyze_places(places_path):
    print("Analyzing Places of Interest...")
    try:
        gdf = gpd.read_file(places_path)
        gdf = gdf.to_crs(epsg=3857)
        target_projected = gpd.GeoSeries([TARGET_POINT], crs="EPSG:4326").to_crs(epsg=3857).iloc[0]
        
        buffer = target_projected.buffer(SEARCH_RADIUS_KM * 1000)
        nearby = gdf[gdf.geometry.intersects(buffer)]
        return nearby
    except Exception as e:
        print(f"Error analyzing places: {e}")
        return gpd.GeoDataFrame()

def identify_neighborhood(neighbourhoods_path):
    print("Identifying Neighborhood...")
    try:
        gdf = gpd.read_file(neighbourhoods_path)
        containing = gdf[gdf.contains(TARGET_POINT)]
        if not containing.empty:
            return containing.iloc[0]['AREA_NAME']
        return "Unknown"
    except Exception as e:
        print(f"Error identifying neighborhood: {e}")
        return "Unknown"

def generate_report(neighborhood_name, leisure_data, crime_data, transit_data, places_data):
    report = f"# Neighborhood Analysis: College and Beverly St\n\n"
    report += f"**Identified Neighborhood**: {neighborhood_name}\n\n"
    
    report += "## Leisure & Recreation (within 1km)\n"
    report += f"- **Total Facilities Found**: {len(leisure_data)}\n"
    if not leisure_data.empty:
        report += "\n### Highlights\n"
        # Use ASSET_NAME and AMENITIES
        if 'ASSET_NAME' in leisure_data.columns:
            # Iterate over rows
            for _, row in leisure_data.iterrows():
                name = row.get('ASSET_NAME', 'Unknown')
                amenities = row.get('AMENITIES', 'None')
                if amenities and amenities != 'None':
                    report += f"- **{name}**: {amenities}\n"
                else:
                    report += f"- {name}\n"

    report += "\n## Places of Interest (within 1km)\n"
    report += f"- **Total Places Found**: {len(places_data)}\n"
    if not places_data.empty:
        # Use NAME and CATEGORY
        if 'NAME' in places_data.columns:
             for _, place in places_data.iterrows():
                 name = place.get('NAME', 'Unknown')
                 category = place.get('CATEGORY', 'General')
                 report += f"- **{name}** ({category})\n"
    
    report += "\n## Crime & Safety (2023 Statistics)\n"
    if crime_data:
        report += f"Crime statistics for **{neighborhood_name}**:\n"
        for crime_type, count in crime_data.items():
            clean_name = crime_type.replace('_2023', '').replace('_', ' ').title()
            report += f"- {clean_name}: {count}\n"
    else:
        report += "No specific crime data found for this neighborhood.\n"

    report += "\n## Transit & Cycling\n"
    report += f"- **Cycling Routes Nearby**: {len(transit_data)}\n"
    if not transit_data.empty:
        if 'INFRA_HIGH' in transit_data.columns:
             counts = transit_data['INFRA_HIGH'].value_counts()
             for infra, count in counts.items():
                 report += f"- {infra}: {count} segments\n"

    with open(OUTPUT_FILE, "w") as f:
        f.write(report)
    print(f"Report generated at {OUTPUT_FILE}")

def main():
    paths = download_data()
    
    neighborhood_name = identify_neighborhood(paths['neighbourhoods'])
    leisure_data = analyze_leisure(paths['parks'])
    crime_data = analyze_crime(paths['crimes'], neighborhood_name)
    transit_data = analyze_transit(paths['cycling'])
    places_data = analyze_places(paths['places'])
    
    generate_report(neighborhood_name, leisure_data, crime_data, transit_data, places_data)

if __name__ == "__main__":
    main()
