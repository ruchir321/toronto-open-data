import requests

from pprint import pprint
# Toronto Open Data is stored in a CKAN instance. It's APIs are documented here:
# https://docs.ckan.org/en/latest/api/

# To hit our API, you'll be making requests to:


# def download_data(params: dict, download_file: str) -> None:
base_url = "https://ckan0.cf.opendata.inter.prod-toronto.ca"
url = base_url + "/api/3/action/package_show"
params = { "id": "z39-50-library-catalogue"}
package = requests.get(url, params = params).json()

# To get resource data:
for idx, resource in enumerate(package["result"]["resources"]):

    # for datastore_active resources:
    if resource["datastore_active"]:

        # To get all records in CSV format:
        url = base_url + "/datastore/dump/" + resource["id"]
        resource_dump_data = requests.get(url).text

        # To selectively pull records and attribute-level metadata:
        url = base_url + "/api/3/action/datastore_search"
        p = { "id": resource["id"] }
        resource_search_data = requests.get(url, params = p).json()["result"]
        # This API call has many parameters. They're documented here:
        # https://docs.ckan.org/en/latest/maintaining/datastore.html

    # To get metadata for non datastore_active resources:
    if not resource["datastore_active"]:
        url = base_url + "/api/3/action/resource_show?id=" + resource["id"]
        resource_metadata = requests.get(url).json()
        pprint(resource_metadata)
        # From here, you can use the "url" attribute to download this file

# with open('cat.txt', 'w') as file:
#     file.write(resource_dump_data)
