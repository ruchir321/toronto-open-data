import os
import requests
import json

# Toronto Open Data is stored in a CKAN instance. Its APIs are documented here:
# https://docs.ckan.org/en/latest/api/

# To hit our API, you'll be making requests to:
base_url = "https://ckan0.cf.opendata.inter.prod-toronto.ca"

# Datasets are called "packages". Each package can contain many "resources".
# To retrieve the metadata for this package and its resources, use the package name in this page's URL:
url = base_url + "/api/3/action/package_show"
params = {"id": "toronto-signature-sites"}
package = requests.get(url, params=params).json()

# Ensure output directory exists
OUT_DIR = "toronto-signature-sites/data"
os.makedirs(OUT_DIR, exist_ok=True)

# To get resource data:
for idx, resource in enumerate(package["result"]["resources"]):
     try:
          # for datastore_active resources (usually large tables)
          if resource.get("datastore_active"):
               # To get all records in CSV format (dump endpoint usually returns CSV/text):
               dump_url = base_url + "/datastore/dump/" + resource["id"]
               resp = requests.get(dump_url)
               resp.raise_for_status()
               text = resp.text

               # Try to parse as JSON; if not valid JSON, save as CSV/text
               try:
                    parsed = json.loads(text)
                    out_path = os.path.join(OUT_DIR, f"resource_dump_{idx}.json")
                    with open(out_path, "w", encoding="utf-8") as f:
                         json.dump(parsed, f, ensure_ascii=False, indent=2)
               except json.JSONDecodeError:
                    out_path = os.path.join(OUT_DIR, f"resource_dump_{idx}.csv")
                    with open(out_path, "w", encoding="utf-8") as f:
                         f.write(text)

               print(f"Saved resource dump to {out_path}")

          # For non-datastore_active resources: metadata and file links
          else:
               meta_url = base_url + "/api/3/action/resource_show?id=" + resource["id"]
               resource_metadata = requests.get(meta_url).json()
               out_path = os.path.join(OUT_DIR, f"resource_metadata_{idx}.json")
               with open(out_path, "w", encoding="utf-8") as file:
                    # write the metadata JSON to the file
                    json.dump(resource_metadata, file, ensure_ascii=False, indent=2)
               print(f"Saved resource metadata to {out_path}")

     except Exception as e:
          print(f"Failed to save resource idx={idx} id={resource.get('id')}: {e}")
