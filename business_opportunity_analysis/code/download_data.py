import requests
import os
import json

BASE_URL = "https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action"

def get_resource_id(package_id, resource_name_contains):
    url = f"{BASE_URL}/package_show"
    params = {"id": package_id}
    response = requests.get(url, params=params)
    data = response.json()
    
    if not data["success"]:
        print(f"Failed to fetch package {package_id}")
        return None
        
    resources = data["result"]["resources"]
    for res in resources:
        if resource_name_contains.lower() in res["name"].lower():
            return res["id"]
    
    print(f"Resource matching '{resource_name_contains}' not found in package {package_id}")
    return None

def download_resource(resource_id, file_name):
    url = f"{BASE_URL}/datastore_search"
    # For CSVs in datastore, we can try to get the download URL or just query it. 
    # But for files like Excel, we need the download URL.
    # Let's use resource_show to get the url.
    
    res_url = f"{BASE_URL}/resource_show?id={resource_id}"
    res_info = requests.get(res_url).json()
    
    if not res_info["success"]:
        print(f"Failed to get resource info for {resource_id}")
        return

    download_url = res_info["result"]["url"]
    print(f"Downloading {file_name} from {download_url}...")
    
    response = requests.get(download_url)
    with open(file_name, 'wb') as f:
        f.write(response.content)
    print(f"Saved {file_name}")

def main():
    # 1. Business Licenses (CSV)
    # Resource ID: 54bddc5e-92d9-4102-89c1-43e82f8f4d2d
    download_resource("54bddc5e-92d9-4102-89c1-43e82f8f4d2d", "../data/business_licenses.csv")

    # 2. Neighborhood Profiles (CSV) - 2016 140 Model
    # Resource ID: f07fe8f0-fa24-4d68-8cb4-326e280b0b05
    download_resource("f07fe8f0-fa24-4d68-8cb4-326e280b0b05", "../data/neighborhood_profiles.csv")

    # 3. Neighborhood Boundaries (GeoJSON) - 140 Model
    # Resource ID: 9994da8e-5d35-438b-bfc4-eef14d09e035
    download_resource("9994da8e-5d35-438b-bfc4-eef14d09e035", "../data/neighborhoods.geojson")

    # 4. Public Art (GeoJSON)
    # Resource ID: 24b60670-7ec3-4156-a02a-8b556ca50402
    download_resource("24b60670-7ec3-4156-a02a-8b556ca50402", "../data/public_art.geojson")

    # 5. Pedestrian Volumes (XLSX)
    # Resource ID: f52840c6-86f6-4db9-9eac-973b0bf9240e
    download_resource("f52840c6-86f6-4db9-9eac-973b0bf9240e", "../data/pedestrian_volumes.xlsx")

    # 6. Wellbeing Economics (XLSX)
    # Resource ID: 089daef7-b737-4e9f-a8db-2c0b35ddc232
    download_resource("089daef7-b737-4e9f-a8db-2c0b35ddc232", "../data/wellbeing_economics.xlsx")

if __name__ == "__main__":
    main()
