import requests
import json

base_url = "https://ckan0.cf.opendata.inter.prod-toronto.ca"

## 1. LIST OF DATASETS
# package_list = "/api/3/action/package_list"
# url = base_url + package_list
# response = requests.get(url).json()
# print(f"There are {len(response["result"])} datasets available") # 531 datasets

group_list = "/api/3/action/group_list"
url = base_url + group_list
response = requests.get(url).json()
print(response)