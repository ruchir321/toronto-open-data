import pandas as pd
import os
import requests

# Constants
DINESAFE_URL = "https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/b6b4f3fb-2e2c-47e7-931d-b87d22806948/resource/e9df9d33-727e-4758-9a84-67ebefec1453/download/dinesafe.json"
DINESAFE_FILE = "../data/dinesafe.json"

def load_and_process_data():
    # Download if not exists
    if not os.path.exists(DINESAFE_FILE):
        print("Downloading data...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
        }
        response = requests.get(DINESAFE_URL, headers=headers)
        if response.status_code == 200:
            with open(DINESAFE_FILE, 'wb') as f:
                f.write(response.content)
        else:
            print("Failed to download data.")
            return pd.DataFrame()

    # Load Data
    df = pd.read_json(DINESAFE_FILE)
    df = df.dropna(subset=['Latitude', 'Longitude'])
    
    # Filter for Harborfront Bounding Box
    # South of Gardiner (approx 43.645), between Bathurst and Yonge/Jarvis
    min_lat = 43.630
    max_lat = 43.648
    min_lon = -79.410
    max_lon = -79.360
    
    mask = (
        (df['Latitude'] >= min_lat) & (df['Latitude'] <= max_lat) &
        (df['Longitude'] >= min_lon) & (df['Longitude'] <= max_lon)
    )
    df_harborfront = df[mask].copy()
    
    initial_count = len(df_harborfront)
    
    # Deduplicate
    # Drop duplicates based on Name and Address
    df_harborfront = df_harborfront.drop_duplicates(subset=['Establishment Name', 'Establishment Address'])
    
    final_count = len(df_harborfront)
    print(f"Data loaded. Initial count: {initial_count}, Final count after deduplication: {final_count}")
    
    return df_harborfront

def categorize_establishment(row):
    name = str(row['Establishment Name']).lower()
    etype = str(row['Establishment Type']).lower()
    
    # Keywords
    veg_keywords = ["vegetarian", "vegan", "plant", "green"]
    grocery_keywords = ["grocery", "supermarket", "market", "loblaws", "sobeys", "metro", "rabba", "longos", "farm boy", "no frills", "freshco"]
    cheap_keywords = ["no frills", "freshco", "food basics", "walmart", "giant tiger"]
    
    is_veg = any(k in name for k in veg_keywords) or any(k in etype for k in veg_keywords)
    is_grocery = any(k in name for k in grocery_keywords) or "supermarket" in etype or "food store" in etype
    is_cheap = is_grocery and any(k in name for k in cheap_keywords)
    
    if is_veg:
        return "Vegetarian/Vegan Friendly"
    elif is_cheap:
        return "Cheap Grocery"
    elif is_grocery:
        return "Grocery Store"
    else:
        return "Other"
