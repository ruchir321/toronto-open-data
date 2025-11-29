import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px

# Set page config
st.set_page_config(page_title="Toronto Renewable Energy Dashboard", layout="wide")

# Title and Introduction
st.title("🌱 Toronto Renewable Energy Installations Dashboard")
st.markdown("""
This dashboard visualizes renewable energy installations on City-owned buildings in Toronto.
Data source: [City of Toronto Open Data](https://open.toronto.ca/dataset/renewable-energy-installations/)
""")

# Load Data
@st.cache_data
def load_data():
    try:
        # Load shapefile
        gdf = gpd.read_file("../data/renewable_energy_shp")
        return gdf
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

df = load_data()

if df is not None:
    # Data Cleaning & Preprocessing
    # Rename columns for clarity
    # Shapefile columns: R_LOCATION, R_TYPE, R_SIZE, R_YR_INSTA, LATITUDE, LONGITUDE, R_WARD
    
    df = df.rename(columns={
        'R_TYPE': 'Technology',
        'R_SIZE': 'Size_kW',
        'R_YR_INSTA': 'Installation_Year',
        'R_LOCATION': 'Address',
        'R_WARD': 'Ward',
        'LATITUDE': 'Latitude',
        'LONGITUDE': 'Longitude'
    })
    
    # Display raw data check (optional, for debugging)
    # st.write(df.head())

    # Standardize column names for easier access - Removed as rename handles it
    
    # Sidebar Filters
    st.sidebar.header("Filters")
    
    # Filter by Technology
    if 'Technology' in df.columns:
        technologies = df['Technology'].unique().tolist()
        selected_tech = st.sidebar.multiselect("Select Technology", technologies, default=technologies)
        df_filtered = df[df['Technology'].isin(selected_tech)]
    else:
        df_filtered = df
        st.warning("Column 'Technology' not found.")

    # Filter by Ward
    if 'Ward' in df.columns:
        wards = df['Ward'].unique().tolist()
        selected_ward = st.sidebar.multiselect("Select Ward", wards, default=wards)
        if selected_ward:
            df_filtered = df_filtered[df['Ward'].isin(selected_ward)]

    # Key Metrics
    col1, col2, col3 = st.columns(3)
    
    total_installations = len(df_filtered)
    col1.metric("Total Installations", total_installations)
    
    if 'Size_kW' in df_filtered.columns:
        # Ensure numeric
        df_filtered['Size_kW'] = pd.to_numeric(df_filtered['Size_kW'], errors='coerce').fillna(0)
        total_capacity = df_filtered['Size_kW'].sum()
        col2.metric("Total Capacity (kW)", f"{total_capacity:,.2f}")
    
    # Visualizations
    
    # 1. Installations by Technology
    st.subheader("Installations by Technology")
    if 'Technology' in df_filtered.columns:
        fig_tech = px.bar(df_filtered['Technology'].value_counts().reset_index(), 
                          x='Technology', y='count', 
                          labels={'Technology': 'Technology', 'count': 'Number of Installations'},
                          color='Technology',
                          title="Number of Installations by Technology")
        st.plotly_chart(fig_tech, use_container_width=True)

    # 2. Installations Over Time
    st.subheader("Installation Trends Over Time")
    if 'Installation_Year' in df_filtered.columns:
        # Clean year data
        df_year = df_filtered.dropna(subset=['Installation_Year'])
        df_year['Installation_Year'] = pd.to_numeric(df_year['Installation_Year'], errors='coerce')
        df_year = df_year.dropna(subset=['Installation_Year'])
        df_year = df_year[df_year['Installation_Year'] > 1900] # Filter out invalid years
        df_year = df_year.sort_values('Installation_Year')
        
        counts_by_year = df_year.groupby('Installation_Year').size().reset_index(name='Count')
        
        fig_year = px.line(counts_by_year, x='Installation_Year', y='Count', 
                           markers=True,
                           title="New Installations per Year")
        st.plotly_chart(fig_year, use_container_width=True)
    else:
        st.info("Installation Year data not available for trend analysis.")

    # 3. Map of Installations
    st.subheader("Map of Installations")
    if 'Latitude' in df_filtered.columns and 'Longitude' in df_filtered.columns:
        # Drop rows with missing coords
        df_map = df_filtered.dropna(subset=['Latitude', 'Longitude'])
        
        fig_map = px.scatter_mapbox(df_map, lat='Latitude', lon='Longitude', 
                                    hover_name='Address' if 'Address' in df_map.columns else None,
                                    hover_data=['Technology', 'Size_kW'],
                                    color='Technology',
                                    zoom=10, height=600)
        fig_map.update_layout(mapbox_style="open-street-map")
        fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.warning("Latitude/Longitude columns not found for mapping.")

    # Data Table
    st.subheader("Raw Data")
    st.dataframe(df_filtered.drop(columns='geometry', errors='ignore'))

else:
    st.warning("No data loaded.")
