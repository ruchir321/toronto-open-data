import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time

def load_neighborhoods():
    print("Loading Neighborhoods...")
    gdf = gpd.read_file("../data/neighborhoods.geojson")
    # Ensure CRS is 4326
    if gdf.crs != "EPSG:4326":
        gdf = gdf.to_crs("EPSG:4326")
    
    # Clean AREA_NAME: Remove " (ID)" suffix
    # Example: "Agincourt North (129)" -> "Agincourt North"
    gdf['AREA_NAME'] = gdf['AREA_NAME'].str.replace(r" \(\d+\)$", "", regex=True)
    return gdf

def load_profiles(neighborhoods_gdf):
    print("Loading Neighborhood Profiles...")
    df = pd.read_csv("../data/neighborhood_profiles.csv")
    
    # Population
    pop_row = df[df['Characteristic'] == 'Population, 2016']
    
    # Arts Education
    arts_row = df[df['Characteristic'].str.contains("Visual and performing arts", na=False)]
    
    nb_names = neighborhoods_gdf['AREA_NAME'].tolist()
    
    processed_data = []
    
    for col in df.columns:
        # Check if column is a neighborhood name (exact match)
        if col in nb_names:
            pop = 0
            arts = 0
            
            try:
                val = pop_row[col].values[0]
                pop = float(str(val).replace(',', ''))
            except:
                pass
                
            try:
                # Sum all matching arts rows
                arts = arts_row[col].apply(lambda x: float(str(x).replace(',', '')) if pd.notnull(x) else 0).sum()
            except:
                pass
            
            processed_data.append({
                'Neighborhood': col,
                'Population': pop,
                'Arts_Education': arts
            })
            
    return pd.DataFrame(processed_data)

def load_economics():
    print("Loading Economics...")
    try:
        df = pd.read_excel("../data/wellbeing_economics.xlsx", sheet_name="RawData-Ref Period 2011", header=1)
        # Columns might be different. Let's print them if it fails.
        # Check if 'Neighbourhood' exists
        if 'Neighbourhood' not in df.columns:
            # Maybe it's 'Neighborhood' or something else.
            # Let's try to find a column that looks like neighborhood names.
            pass
            
        return df[['Neighbourhood', 'Local Employment', 'Businesses']]
    except Exception as e:
        print(f"Could not load Economics data properly: {e}")
        return pd.DataFrame(columns=['Neighbourhood', 'Local Employment', 'Businesses'])

def load_pedestrian(neighborhoods_gdf):
    print("Loading Pedestrian Volumes...")
    df = pd.read_excel("../data/pedestrian_volumes.xlsx")
    
    # Create GeoDataFrame
    geometry = [Point(xy) for xy in zip(df['Longitude'], df['Latitude'])]
    geo_df = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
    
    # Spatial Join
    joined = gpd.sjoin(geo_df, neighborhoods_gdf, how="inner", predicate="within")
    
    # Aggregate
    agg = joined.groupby('AREA_NAME')['8 Peak Hr Pedestrian Volume'].sum().reset_index()
    agg.rename(columns={'8 Peak Hr Pedestrian Volume': 'Pedestrian_Volume'}, inplace=True)
    return agg

def load_public_art(neighborhoods_gdf):
    print("Loading Public Art...")
    gdf = gpd.read_file("../data/public_art.geojson")
    if gdf.crs != "EPSG:4326":
        gdf = gdf.to_crs("EPSG:4326")
        
    # Spatial Join
    joined = gpd.sjoin(gdf, neighborhoods_gdf, how="inner", predicate="within")
    
    # Count
    agg = joined.groupby('AREA_NAME').size().reset_index(name='Public_Art_Count')
    return agg

def process_competitors(neighborhoods_gdf):
    print("Processing Competitors...")
    df = pd.read_csv("../data/business_licenses.csv")
    
    # Filter Active
    # Assuming no explicit status column, or checking Cancel Date is empty/future
    # Let's assume all in file are relevant, or check 'Cancel Date'
    if 'Cancel Date' in df.columns:
        df = df[df['Cancel Date'].isna()]
        
    # Filter Keywords
    keywords = ['ART', 'CRAFT', 'HOBBY', 'GALLERY', 'SUPPLY', 'PAINT', 'CANVAS', 'KNIT', 'SEW']
    # Filter by Category or Operating Name
    mask = df['Category'].str.upper().str.contains('|'.join(keywords), na=False) | \
           df['Operating Name'].str.upper().str.contains('|'.join(keywords), na=False) | \
           df['Endorsements'].str.upper().str.contains('|'.join(keywords), na=False)
           
    competitors = df[mask].copy()
    
    # Filter for Downtown FSAs to reduce geocoding load
    downtown_fsas = ['M5', 'M4Y', 'M4W', 'M4X', 'M6G', 'M6J', 'M5T', 'M5S', 'M5R', 'M5P', 'M5N', 'M5M', 'M5L', 'M5K', 'M5J', 'M5H', 'M5G', 'M5E', 'M5C', 'M5B', 'M5A']
    # Extract FSA from 'Licence Address Line 3'
    competitors['FSA'] = competitors['Licence Address Line 3'].astype(str).str[:3]
    competitors = competitors[competitors['FSA'].isin(downtown_fsas)]
    
    print(f"Found {len(competitors)} potential competitors in Downtown area.")
    
    # Geocode
    geolocator = Nominatim(user_agent="toronto_business_analysis")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    
    lats = []
    lons = []
    
    print("Geocoding addresses using pgeocode...")
    import pgeocode
    nomi = pgeocode.Nominatim('ca')
    
    lats = []
    lons = []
    
    for index, row in competitors.iterrows():
        # Use FSA (first 3 chars of postal code)
        pc = row['Licence Address Line 3']
        if isinstance(pc, str) and len(pc) >= 3:
            fsa = pc[:3]
            location = nomi.query_postal_code(fsa)
            
            if not pd.isna(location.latitude):
                lats.append(location.latitude)
                lons.append(location.longitude)
            else:
                lats.append(None)
                lons.append(None)
        else:
            lats.append(None)
            lons.append(None)
            
    competitors['Latitude'] = lats
    competitors['Longitude'] = lons
    
    # Drop failed geocodes
    competitors = competitors.dropna(subset=['Latitude', 'Longitude'])
    
    # Spatial Join
    geometry = [Point(xy) for xy in zip(competitors['Longitude'], competitors['Latitude'])]
    geo_df = gpd.GeoDataFrame(competitors, geometry=geometry, crs="EPSG:4326")
    
    joined = gpd.sjoin(geo_df, neighborhoods_gdf, how="inner", predicate="within")
    
    # Save competitors for map
    joined[['Operating Name', 'Licence Address Line 1', 'Category', 'AREA_NAME', 'Latitude', 'Longitude']].to_csv("../data/competitors_processed.csv", index=False)
    
    # Count
    agg = joined.groupby('AREA_NAME').size().reset_index(name='Competitor_Count')
    return agg

def main():
    # 1. Load Neighborhoods
    nb_gdf = load_neighborhoods()
    # Keep only relevant columns
    nb_gdf = nb_gdf[['AREA_NAME', 'geometry']]
    
    # 2. Load Data
    profiles = load_profiles(nb_gdf)
    economics = load_economics()
    pedestrian = load_pedestrian(nb_gdf)
    public_art = load_public_art(nb_gdf)
    competitors = process_competitors(nb_gdf)
    
    # 3. Merge
    # Start with GDF
    merged = nb_gdf.merge(profiles, left_on='AREA_NAME', right_on='Neighborhood', how='left')
    merged = merged.merge(economics, left_on='AREA_NAME', right_on='Neighbourhood', how='left')
    merged = merged.merge(pedestrian, on='AREA_NAME', how='left')
    merged = merged.merge(public_art, on='AREA_NAME', how='left')
    merged = merged.merge(competitors, on='AREA_NAME', how='left')
    
    # Fill NaNs
    cols_to_fill = ['Population', 'Arts_Education', 'Local Employment', 'Businesses', 'Pedestrian_Volume', 'Public_Art_Count', 'Competitor_Count']
    for col in cols_to_fill:
        if col in merged.columns:
            merged[col] = merged[col].fillna(0)
            
    # 4. Save
    merged.to_csv("../data/neighborhood_stats.csv", index=False)
    # Also save as GeoJSON for the app
    merged.to_file("../data/neighborhood_stats.geojson", driver='GeoJSON')
    
    print("Processing complete. Saved neighborhood_stats.csv and neighborhood_stats.geojson")

if __name__ == "__main__":
    main()
