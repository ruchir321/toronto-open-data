import os

cwd = os.getcwd()
print(cwd)


import json
import pandas as pd
from utils.download_data import download_data

# Datasets are called "packages". Each package can contain many "resources"
# To retrieve the metadata for this package and its resources, use the package name in this page's URL:
params = { "id": "bike-share-toronto"}
download_file = cwd+"/data/"

def create_csv_data():
    download_data(params, download_file)

    files = os.listdir("data")

    data_dict = {}
    for file in files:
        filepath = f"data/{file}"
        filename = file.split(sep=".")[0]
        with open(filepath, 'r') as f:
            data = f.read()
            data_dict[filename] = json.loads(data)['data']

    df_dict = {}
    for k, v in data_dict.items():
        if k == "system_information":
            df_dict[k] = pd.DataFrame(v)
        else:
            for _, val in v.items():
                df_dict[k] = pd.DataFrame(val)

    # # station_status
    # ## create column bike counts by types

    df_bike_type_counts = df_dict['station_status']['num_bikes_available_types'].apply(pd.Series)
    df_dict['station_status'] = pd.concat([df_dict['station_status'], df_bike_type_counts], axis=1).drop(columns=['num_bikes_available_types'])

    # # system_information
    # 
    # summary df, not used

    # # station_information

    srs = pd.Series(df_dict['station_information']['rental_methods'].value_counts())

    # ## `explode()`: expands the list into multiple rows.

    df_dict['station_information'] = pd.concat([df_dict['station_information'], df_dict['station_information']['rental_methods'].explode().str.get_dummies().groupby(level=0).max()], axis=1)
    df_dict['station_information'].set_index('station_id', inplace=True)
    df_dict['station_status'].set_index('station_id', inplace=True)
    
    df_stations = df_dict['station_information'].merge(df_dict['station_status'], on='station_id', how='inner').drop(columns=['is_charging_station_x', 'address', 'short_name'])
    df_stations.drop(columns='rental_methods', inplace=True)
    df_stations.to_csv('data/stations.csv')

    # # system_pricing_plans
    df_dict['system_pricing_plans'].to_csv('data/system_pricing_plans.csv')
