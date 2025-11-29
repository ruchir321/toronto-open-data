import requests
import json

BASE_URL = "https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action"

def list_package_resources(package_id):
    url = f"{BASE_URL}/package_show"
    params = {"id": package_id}
    response = requests.get(url, params=params)
    data = response.json()
    
    if not data["success"]:
        print(f"Failed to fetch package {package_id}")
        return
        
    resources = data["result"]["resources"]
    print(f"Resources for package {package_id}:")
    for res in resources:
        print(f"Name: {res['name']}, ID: {res['id']}, Format: {res['format']}")

if __name__ == "__main__":
    # Neighbourhood Profiles
    list_package_resources("6e19a90f-971c-46b3-852c-0c48c436d1fc")
