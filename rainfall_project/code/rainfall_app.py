import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Set page config
st.set_page_config(page_title="Toronto Rainfall Analysis 2024", layout="wide")

# Constants
DATA_URL = "../data/precipitation-data-2024.csv"
RESOURCE_URL = "https://open.toronto.ca/dataset/rain-gauge-locations-and-precipitation/"

@st.cache_data
def load_data():
    """Loads and preprocesses the rainfall data."""
    try:
        # Load only necessary columns
        df = pd.read_csv(DATA_URL, usecols=['name', 'date', 'rainfall'])
        df['date'] = pd.to_datetime(df['date'])
        
        # Filter for 2024
        df = df[df['date'].dt.year == 2024]
        
        return df
    except FileNotFoundError:
        st.error(f"Data file '{DATA_URL}' not found. Please ensure it is in the same directory.")
        return pd.DataFrame()

def process_station_data(df):
    """
    Processes data to calculate daily rainfall and identify extreme events.
    Handles cumulative vs incremental counters.
    """
    daily_records = []
    extreme_events = []
    
    stations = df['name'].unique()
    
    for station in stations:
        station_data = df[df['name'] == station].sort_values('date')
        
        if station_data.empty:
            continue
            
        rainfall_values = station_data['rainfall'].values
        dates = station_data['date'].values
        
        # Calculate differences (5-min increments)
        diffs = rainfall_values[1:] - rainfall_values[:-1]
        
        # Determine if cumulative or incremental
        # Heuristic: If many negative diffs (resets) or max value is huge, it's cumulative.
        # If mostly zeros and small positive values, it might be incremental.
        # Based on previous analysis, most are cumulative with resets.
        
        # We will treat positive differences as the rainfall amount for that interval.
        # This works for cumulative (step up) and incremental (if we assume it's just rate).
        # But for incremental, the value ITSELF is the amount.
        
        # Let's use the logic: if max > 1000, it's definitely cumulative.
        # If it's small, we check the nature of diffs.
        
        # However, to be robust and consistent with the ~348mm finding:
        # We used sum of positive differences for most stations.
        
        # Create a series of 5-min amounts
        # Insert 0 at the start to match length
        amounts = np.insert(diffs, 0, 0)
        
        # Filter out negative amounts (resets)
        amounts = np.where(amounts < 0, 0, amounts)
        
        # Create a DataFrame for this station's processed data
        station_processed = pd.DataFrame({
            'date': dates,
            'amount': amounts,
            'station': station
        })
        
        # Daily Aggregation
        station_processed['day'] = station_processed['date'].dt.normalize()
        daily_sum = station_processed.groupby('day')['amount'].sum().reset_index()
        daily_sum['station'] = station
        daily_records.append(daily_sum)
        
        # Extreme Events (5-min intensity)
        # Threshold: e.g., > 5mm in 5 mins is very heavy (60mm/hr)
        heavy_rain = station_processed[station_processed['amount'] > 5]
        if not heavy_rain.empty:
            extreme_events.append(heavy_rain)
            
    if not daily_records:
        return pd.DataFrame(), pd.DataFrame()
        
    all_daily = pd.concat(daily_records)
    all_extremes = pd.concat(extreme_events) if extreme_events else pd.DataFrame(columns=['date', 'amount', 'station'])
    
    return all_daily, all_extremes

# --- Main App Layout ---

st.title("🌧️ Toronto Rainfall Analysis 2024")
st.markdown(f"Data Source: [Toronto Open Data - Rain Gauge Locations and Precipitation]({RESOURCE_URL})")

with st.spinner("Loading and processing data... (this may take a moment)"):
    raw_df = load_data()
    if not raw_df.empty:
        daily_df, extremes_df = process_station_data(raw_df)
    else:
        st.stop()

# Sidebar Controls
st.sidebar.header("Filters")

min_date = daily_df['day'].min().date()
max_date = daily_df['day'].max().date()

start_date, end_date = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Filter data based on selection
mask = (daily_df['day'].dt.date >= start_date) & (daily_df['day'].dt.date <= end_date)
filtered_daily = daily_df.loc[mask]

if filtered_daily.empty:
    st.warning("No data available for the selected date range.")
    st.stop()

# --- Summary Statistics ---

# Calculate city-wide average daily rainfall
city_daily_avg = filtered_daily.groupby('day')['amount'].mean().reset_index()

total_avg_rainfall = city_daily_avg['amount'].sum()
max_daily_avg = city_daily_avg['amount'].max()
wettest_day = city_daily_avg.loc[city_daily_avg['amount'].idxmax(), 'day'].date()

col1, col2, col3 = st.columns(3)
col1.metric("Total Avg Rainfall (City-wide)", f"{total_avg_rainfall:.2f} mm")
col2.metric("Max Daily Avg Rainfall", f"{max_daily_avg:.2f} mm")
col3.metric("Wettest Day", f"{wettest_day}")

# --- Time Series Chart ---

st.subheader("Daily Rainfall (City-wide Average)")
fig = px.line(city_daily_avg, x='day', y='amount', 
              labels={'day': 'Date', 'amount': 'Average Rainfall (mm)'},
              title="Average Daily Rainfall across all Stations")
st.plotly_chart(fig, use_container_width=True)

# --- Extreme Events & Outliers ---

st.subheader("⛈️ Extreme Weather Events & Outliers")

tab1, tab2 = st.tabs(["Wettest Days (Outliers)", "High Intensity Events (Thunderstorms)"])

with tab1:
    st.markdown("Top 10 days with the highest city-wide average rainfall.")
    top_days = city_daily_avg.sort_values('amount', ascending=False).head(10)
    st.dataframe(top_days.style.format({'amount': '{:.2f}'}), use_container_width=True)

with tab2:
    st.markdown("Instances of very high rainfall intensity (> 5mm in 5 minutes). These often indicate thunderstorms or heavy downpours.")
    if not extremes_df.empty:
        # Filter extremes by date range too
        extremes_mask = (extremes_df['date'].dt.date >= start_date) & (extremes_df['date'].dt.date <= end_date)
        filtered_extremes = extremes_df.loc[extremes_mask].sort_values('amount', ascending=False)
        
        st.dataframe(filtered_extremes[['date', 'station', 'amount']].rename(columns={'amount': '5-min Rainfall (mm)'}), use_container_width=True)
    else:
        st.info("No extreme intensity events (> 5mm/5min) detected in this period.")

# --- Footer ---
st.markdown("---")
st.markdown("### Resources")
st.markdown("- [Toronto Open Data Portal](https://open.toronto.ca/)")
st.markdown("- [Rain Gauge Dataset](https://open.toronto.ca/dataset/rain-gauge-locations-and-precipitation/)")
st.markdown("- [Basement Flooding Protection Program](https://www.toronto.ca/services-payments/water-environment/managing-rain-melted-snow/basement-flooding/)")
