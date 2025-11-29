import streamlit as st
import pandas as pd
import folium
from folium.plugins import Fullscreen
from streamlit_folium import st_folium
from data_loader import load_and_process_data, categorize_establishment

# Constants
HOME_COORDS = [43.639, -79.388] # Approx for 350 Queens Quay West
HOME_ADDRESS = "350 Queens Quay West"

# Page Config
st.set_page_config(page_title="Harborfront Food Options", layout="wide")

@st.cache_data
def get_data():
    return load_and_process_data()

def main():
    st.title("Harborfront Neighborhood Food Options")
    
    df = get_data()
    
    if df.empty:
        st.warning("No data found.")
        return

    # Apply categorization
    df['Category'] = df.apply(categorize_establishment, axis=1)
    
    # Filter for relevant categories
    relevant_cats = ["Vegetarian/Vegan Friendly", "Cheap Grocery", "Grocery Store"]
    df_relevant = df[df['Category'].isin(relevant_cats)].copy()
    
    # Reset index to ensure selection works predictably
    df_relevant = df_relevant.reset_index(drop=True)

    # Layout: Map on top (large), Table below
    
    # Initialize Map Center
    map_center = HOME_COORDS
    map_zoom = 15
    
    # Placeholder for selection logic (will be processed after dataframe is rendered in standard script flow, 
    # but we need map params first. Streamlit reruns on selection, so we can check session state or just render table first?
    # Actually, st.data_editor/dataframe returns immediately. We usually put it before the map if we want to control the map, 
    # OR we use session state. 
    # Let's put the table in a sidebar or below? 
    # If below, we need to handle the rerun. 
    # Let's use a container for the map to render it *after* we know the selection? 
    # No, Streamlit renders top-down. 
    # If we want Table -> Map, Table should ideally be above or we use a callback? 
    # st.dataframe on_select triggers a rerun. On the rerun, we check the selection.
    
    # Let's put the table on the side (sidebar) or split columns?
    # User asked for "resize map to fit the screen", so map should be big.
    # Let's put the table below the map, but we need to read the selection from the *previous* run? 
    # No, st.dataframe returns the selection state.
    # If we place st.dataframe *before* the map in the code, we can use its output to set map center.
    
    col_list, col_map = st.columns([1, 2])
    
    with col_list:
        st.subheader("Establishments")
        st.caption("Select a row to highlight on map")
        
        # Display relevant columns
        display_cols = ['Establishment Name', 'Category', 'Establishment Address']
        
        selection = st.dataframe(
            df_relevant[display_cols],
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            height=600
        )
    
    selected_indices = selection.selection.rows
    highlight_coords = None
    
    if selected_indices:
        idx = selected_indices[0]
        selected_row = df_relevant.iloc[idx]
        map_center = [selected_row['Latitude'], selected_row['Longitude']]
        map_zoom = 18
        highlight_coords = map_center
        st.toast(f"Selected: {selected_row['Establishment Name']}")

    with col_map:
        # Map
        m = folium.Map(location=map_center, zoom_start=map_zoom)
        Fullscreen().add_to(m)
        
        # Home Marker
        folium.Marker(
            HOME_COORDS,
            tooltip="Home: 350 Queens Quay West",
            icon=folium.Icon(color="red", icon="home"),
            popup=HOME_ADDRESS
        ).add_to(m)
        
        # Venue Markers
        for idx, row in df_relevant.iterrows():
            cat = row['Category']
            color = "blue"
            if cat == "Vegetarian/Vegan Friendly":
                color = "green"
            elif cat == "Cheap Grocery":
                color = "darkblue"
            elif cat == "Grocery Store":
                color = "orange"
                
            # Highlight selected
            icon_type = "cutlery" if "Grocery" not in cat else "shopping-cart"
            if highlight_coords and row['Latitude'] == highlight_coords[0] and row['Longitude'] == highlight_coords[1]:
                color = "red"
                icon_type = "star"
                
            tooltip_text = f"{row['Establishment Name']} ({row['Establishment Type']})"
            
            folium.Marker(
                [row['Latitude'], row['Longitude']],
                tooltip=tooltip_text,
                popup=folium.Popup(f"<b>{row['Establishment Name']}</b><br>{row['Establishment Address']}<br>{cat}", max_width=300),
                icon=folium.Icon(color=color, icon=icon_type)
            ).add_to(m)
            
        st_folium(m, height=700, use_container_width=True)

if __name__ == "__main__":
    main()
