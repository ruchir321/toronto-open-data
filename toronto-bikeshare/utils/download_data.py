import requests
import json
# Toronto Open Data is stored in a CKAN instance. It's APIs are documented here:
# https://docs.ckan.org/en/latest/api/

# To hit our API, you'll be making requests to:

def download_data(params: dict, download_file: str) -> None:
    base_url = "https://ckan0.cf.opendata.inter.prod-toronto.ca"
    url = base_url + "/api/3/action/package_show"
    params = { "id": "bike-share-toronto"}
    package = requests.get(url, params = params).json()
    base_url = "https://tor.publicbikesystem.net/ube/gbfs/v1/en/"

    json_feeds = ["system_information", "station_information", "station_status", "system_pricing_plans"]
    

    for feed in json_feeds:
        url = base_url + feed
        resource_dump_data = requests.get(url).json()
        download_path = download_file + f"/{feed}.json" 
        with open(download_path, 'w', encoding='utf-8') as f:
            json.dump(resource_dump_data, f, ensure_ascii=False, indent=4)
    
    
    # # To get resource data:
    # for idx, resource in enumerate(package["result"]["resources"]):

    #     # for datastore_active resources:
    #     if resource["datastore_active"]:

    #         # To get all records in CSV format:
    #         url = base_url + "/datastore/dump/" + resource["id"]
    #         resource_dump_data = requests.get(url).text

    #         # To selectively pull records and attribute-level metadata:
    #         url = base_url + "/api/3/action/datastore_search"
    #         p = { "id": resource["id"] }
    #         resource_search_data = requests.get(url, params = p).json()["result"]
    #         # This API call has many parameters. They're documented here:
    #         # https://docs.ckan.org/en/latest/maintaining/datastore.html

    #     # To get metadata for non datastore_active resources:
    #     if not resource["datastore_active"]:
    #         url = base_url + "/api/3/action/resource_show?id=" + resource["id"]
    #         resource_metadata = requests.get(url).json()
    #         # From here, you can use the "url" attribute to download this file
    #         url = resource_metadata['result']['url']
    #         if resource_metadata['result']['format'] == 'JSON':
    #             resource_feed = requests.get(url).json()
    #             # print(resource_feed['data']['en']['feeds']['url'].keys())
    #             url_list = resource_feed['data']['en']['feeds']
    #             for url in url_list:
    #                 # print(url['url'])
    #                 feed_url = url['url']
    #                 # download only station_information, station_status, system_pricing_plans
    #                 resource_dump_data = requests.get(url).json()


    # with open(download_file, 'w') as file:
    #     file.write(resource_dump_data)
