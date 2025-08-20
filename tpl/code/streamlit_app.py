import streamlit as st
import pandas as pd
import plotly.express as px
import re
from datetime import datetime
import pydeck as pdk

st.set_page_config(layout="wide")

st.title("Toronto Public Library Analytics")

@st.cache_data
def load_data():
    branch_info = pd.read_csv("/home/ruchirich/Documents/repositories/toronto-open-data/tpl/data/library-branch-general-information.csv")
    circulation = pd.read_csv("/home/ruchirich/Documents/repositories/toronto-open-data/tpl/data/library-circulation.csv").drop(columns=["_id"])
    visits = pd.read_csv("/home/ruchirich/Documents/repositories/toronto-open-data/tpl/data/library-visits.csv").drop(columns=["_id"])
    registrations = pd.read_csv("/home/ruchirich/Documents/repositories/toronto-open-data/tpl/data/library-card-registrations.csv").drop(columns=["_id"])
    workstation_usage = pd.read_csv("/home/ruchirich/Documents/repositories/toronto-open-data/tpl/data/library-workstation-usage.csv").drop(columns=["_id"])
    events = pd.read_csv("/home/ruchirich/Documents/repositories/toronto-open-data/tpl/data/library-branch-programs-and-events-feed.csv").drop(columns=["_id"])

    # Merge dataframes
    usage_data = (circulation.merge(visits, on=["Year", "BranchCode"])
                  .merge(registrations, on=["Year", "BranchCode"])
                  .merge(workstation_usage, on=["Year", "BranchCode"]))

    full_data = usage_data.merge(branch_info, on="BranchCode")
    
    # Clean event descriptions
    events['description'] = events['description'].str.replace(r'<[^<>]*>', '', regex=True)
    
    return branch_info, full_data, events

branch_info, full_data, events = load_data()

st.header("Branch Information")
# Remove rows with missing Lat or Long
branch_info_map = branch_info.dropna(subset=['Lat', 'Long'])

# Define a layer for the map
layer = pdk.Layer(
    "ScatterplotLayer",
    branch_info_map,
    get_position=['Long', 'Lat'],
    get_color=[200, 30, 0, 160],
    get_radius=500,  # Adjust radius as needed
    pickable=True,
)

# Set the viewport location
view_state = pdk.ViewState(
    latitude=branch_info_map['Lat'].mean(),
    longitude=branch_info_map['Long'].mean(),
    zoom=10,
    pitch=50,
)

# Create the PyDeck chart
st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state=view_state,
    layers=[layer],
    tooltip={
        "html": "<b>Branch:</b> {BranchName}<br><b>Address:</b> {Address}<br><b>Phone:</b> {Telephone}",
        "type": "html",
    }
))

st.dataframe(branch_info)

st.header("Library Usage Trends")

# Overall Trends
st.subheader("Overall Trends Across All Branches")
yearly_summary = full_data.groupby("Year")[["Circulation", "Visits", "Registrations", "Sessions"]].sum().reset_index()

fig_yearly_circ = px.line(yearly_summary, x="Year", y="Circulation", title="Total Circulation Over Time")
st.plotly_chart(fig_yearly_circ)

fig_yearly_visits = px.line(yearly_summary, x="Year", y="Visits", title="Total Visits Over Time")
st.plotly_chart(fig_yearly_visits)

fig_yearly_reg = px.line(yearly_summary, x="Year", y="Registrations", title="Total Registrations Over Time")
st.plotly_chart(fig_yearly_reg)

fig_yearly_ws = px.line(yearly_summary, x="Year", y="Sessions", title="Total Workstation Sessions Over Time")
st.plotly_chart(fig_yearly_ws)

# Branch-specific Trends
st.subheader("Branch-specific Trends")
branch = st.selectbox("Select a Branch", branch_info["BranchName"].unique())

branch_data = full_data[full_data["BranchName"] == branch]

fig_branch_circ = px.line(branch_data, x="Year", y="Circulation", title=f"Circulation at {branch}")
st.plotly_chart(fig_branch_circ)

fig_branch_visits = px.line(branch_data, x="Year", y="Visits", title=f"Visits at {branch}")
st.plotly_chart(fig_branch_visits)

fig_branch_reg = px.line(branch_data, x="Year", y="Registrations", title=f"Registrations at {branch}")
st.plotly_chart(fig_branch_reg)

fig_branch_ws = px.line(branch_data, x="Year", y="Sessions", title=f"Workstation Sessions at {branch}")
st.plotly_chart(fig_branch_ws)

st.header("Program and Event Finder")

# Filters
col1, col2, col3, col4 = st.columns(4)
with col1:
    event_type = st.selectbox("Event Type", events["eventtype1"].unique())
with col2:
    age_group = st.selectbox("Age Group", events["agegroup1"].unique())
with col3:
    library = st.selectbox("Library", events["library"].unique())
with col4:
    search_term = st.text_input("Search")

# Date Filter
today = pd.to_datetime('today').normalize()
tomorrow = today + pd.DateOffset(days=1)
next_month = today + pd.DateOffset(months=1)

date_range = st.date_input(
    "Select a date range",
    (tomorrow, next_month),
    min_value=datetime(2024, 1, 1),
    max_value=datetime(2026, 12, 31),
    format="YYYY-MM-DD",
)


# Filter data
filtered_events = events.copy()
if event_type:
    filtered_events = filtered_events[filtered_events["eventtype1"] == event_type]
if age_group:
    filtered_events = filtered_events[filtered_events["agegroup1"] == age_group]
if library:
    filtered_events = filtered_events[filtered_events["library"] == library]
if search_term:
    filtered_events = filtered_events[filtered_events["title"].str.contains(search_term, case=False)]

if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_events = filtered_events[
        (pd.to_datetime(filtered_events["startdate"]) >= pd.to_datetime(start_date)) & 
        (pd.to_datetime(filtered_events["startdate"]) <= pd.to_datetime(end_date))
    ]

st.dataframe(filtered_events[["title", "startdate", "starttime", "library", "location", "description"]])
