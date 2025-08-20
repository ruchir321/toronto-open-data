"""
streamlit demo
# My first app
Here's our first attempt at using data to create a table:
"""

from urllib.error import URLError
import streamlit as st
import pandas as pd
import altair as alt

DISPLAY_COLS = ['station_id', 'num_bikes_available', 'mechanical', 'ebike' ]

@st.cache_data
def get_data() -> pd.DataFrame:
    df = pd.read_csv("data/stations.csv")
    df = df[DISPLAY_COLS]
    return df

try:
    df = get_data()

    ids = df.station_id.values
    display_ids = ids[:20]

    # choose from top first 10 stations
    stations = st.multiselect(
         "Choose station ID:", ids, display_ids
    )

    if not stations:
        st.error("Please select at least one station.")
    
    else:
        data = df[df["station_id"].isin(display_ids)]
        st.dataframe(data.sort_index())
        
        # melt df for altair use
        data = pd.melt(
            frame=data,
            id_vars=['station_id'], # the remaining cols will be assigned to value_vars
            value_vars=['mechanical', 'ebike'],
            var_name="Bike Type",
            value_name="Count"
        )

        print(data.head())
        chart = (
            alt.Chart(data)
            .mark_bar()
            .encode(
                x='station_id:N',
                y='Count:Q',
                color=alt.Color('Bike Type:N', scale=alt.Scale(scheme='category10')),
                tooltip=['station_id', 'Bike Type', 'Count']
            )
        )

        st.altair_chart(chart, use_container_width=True)



except URLError as e:
    st.error(f"This demo requires internet access. Connection error: {e.reason}")

