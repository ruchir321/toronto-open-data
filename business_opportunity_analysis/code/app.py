import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import plotly.express as px
from sklearn.preprocessing import MinMaxScaler

st.set_page_config(page_title="Arts & Crafts Business Analysis", layout="wide")

# Load Data
@st.cache_data
def load_data():
    gdf = gpd.read_file("../data/neighborhood_stats.geojson")
    competitors = pd.read_csv("../data/competitors_processed.csv")
    return gdf, competitors

gdf, competitors = load_data()

st.title("🎨 Arts & Crafts Business Opportunity Analysis")
st.markdown("Find the best neighborhood in Toronto for your new business.")

# Sidebar - Weights
st.sidebar.header("Priorities")
w_footfall = st.sidebar.slider("Footfall Importance", 0.0, 1.0, 0.8)
w_community = st.sidebar.slider("Art Community Importance", 0.0, 1.0, 0.7)
w_competition = st.sidebar.slider("Avoid Competition", 0.0, 1.0, 0.5)
w_affordability = st.sidebar.slider("Affordability (Low Commercial Density)", 0.0, 1.0, 0.4)

# Normalize Metrics
scaler = MinMaxScaler()
metrics = ['Pedestrian_Volume', 'Arts_Education', 'Public_Art_Count', 'Competitor_Count', 'Businesses']

# Handle NaNs just in case
gdf[metrics] = gdf[metrics].fillna(0)

# Normalize
norm_df = pd.DataFrame(scaler.fit_transform(gdf[metrics]), columns=[f"{m}_norm" for m in metrics])
gdf = pd.concat([gdf, norm_df], axis=1)

# Calculate Score
# Community = Arts Education + Public Art
# Affordability Proxy = Inverse of Business Density (Less dense = likely cheaper/more available, or just less established high-rent zones)
# Actually, let's treat "Businesses" as "Commercial Activity". High activity = High Rent usually.
# So Affordability Score = 1 - Business_Density_Norm

gdf['Community_Score'] = (gdf['Arts_Education_norm'] + gdf['Public_Art_Count_norm']) / 2
gdf['Affordability_Score'] = 1 - gdf['Businesses_norm']

gdf['Final_Score'] = (
    (w_footfall * gdf['Pedestrian_Volume_norm']) +
    (w_community * gdf['Community_Score']) +
    (w_affordability * gdf['Affordability_Score']) - 
    (w_competition * gdf['Competitor_Count_norm'])
)

# Sort
top_neighborhoods = gdf.sort_values('Final_Score', ascending=False).head(10)

# Layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Interactive Map")
    
    # Base Map
    m = folium.Map(location=[43.6532, -79.3832], zoom_start=12)
    
    # Choropleth
    folium.Choropleth(
        geo_data=gdf,
        name="Opportunity Score",
        data=gdf,
        columns=["AREA_NAME", "Final_Score"],
        key_on="feature.properties.AREA_NAME",
        fill_color="YlGn",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Business Opportunity Score"
    ).add_to(m)
    
    # Competitors
    fg = folium.FeatureGroup(name="Competitors")
    for idx, row in competitors.iterrows():
        if pd.notnull(row['Latitude']) and pd.notnull(row['Longitude']):
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=f"{row['Operating Name']} ({row['Category']})",
                icon=folium.Icon(color="red", icon="info-sign")
            ).add_to(fg)
    fg.add_to(m)
    
    folium.LayerControl().add_to(m)
    st_folium(m, width=800, height=600)

with col2:
    st.subheader("Top Recommendations")
    st.dataframe(top_neighborhoods[['AREA_NAME', 'Final_Score', 'Pedestrian_Volume', 'Competitor_Count', 'Arts_Education']].style.format({"Final_Score": "{:.2f}"}))
    
    st.subheader("Metric Breakdown")
    selected_nb = st.selectbox("Select Neighborhood for Details", top_neighborhoods['AREA_NAME'])
    
    nb_data = gdf[gdf['AREA_NAME'] == selected_nb].iloc[0]
    
    # Spider Chart or Bar Chart
    chart_data = pd.DataFrame({
        'Metric': ['Footfall', 'Community', 'Affordability', 'Competition'],
        'Value': [
            nb_data['Pedestrian_Volume_norm'],
            nb_data['Community_Score'],
            nb_data['Affordability_Score'],
            nb_data['Competitor_Count_norm']
        ]
    })
    
    fig = px.line_polar(chart_data, r='Value', theta='Metric', line_close=True)
    fig.update_layout(title=f"Profile: {selected_nb}")
    st.plotly_chart(fig)

st.subheader("Competitor List")
st.dataframe(competitors[['Operating Name', 'Category', 'Licence Address Line 1', 'AREA_NAME']])
