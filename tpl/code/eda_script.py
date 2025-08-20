import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import re

# --- Configuration ---
# Set plot style for better aesthetics
sns.set_style("whitegrid")

# Define paths to the datasets
BRANCH_INFO_PATH = "./tpl/data/library-branch-general-information.csv"
CIRCULATION_PATH = "./tpl/data/library-circulation.csv"
VISITS_PATH = "./tpl/data/library-visits.csv"
REGISTRATIONS_PATH = "./tpl/data/library-card-registrations.csv"
WORKSTATION_USAGE_PATH = "./tpl/data/library-workstation-usage.csv"
EVENTS_PATH = "./tpl/data/library-branch-programs-and-events-feed.csv"

# --- Data Loading and Initial Inspection ---
# This section loads all relevant datasets into pandas DataFrames.
# It also performs initial checks like displaying head, info, describe, and missing values.

print("--- 1. Data Loading and Initial Inspection ---")

# Load datasets
branch_info = pd.read_csv(BRANCH_INFO_PATH)
circulation = pd.read_csv(CIRCULATION_PATH)
visits = pd.read_csv(VISITS_PATH)
registrations = pd.read_csv(REGISTRATIONS_PATH)
workstation_usage = pd.read_csv(WORKSTATION_USAGE_PATH)
events = pd.read_csv(EVENTS_PATH)

# Drop '_id' column from usage and events dataframes as it's just an index and causes merge issues
# This ensures clean merges later and removes redundant information.
circulation = circulation.drop(columns=['_id'])
visits = visits.drop(columns=['_id'])
registrations = registrations.drop(columns=['_id'])
workstation_usage = workstation_usage.drop(columns=['_id'])
events = events.drop(columns=['_id'])

# Display initial information for each DataFrame
print("\n--- Branch Information (branch_info) ---")
print("Head:\n", branch_info.head())
print("\nInfo:")
branch_info.info()
print("\nDescription:\n", branch_info.describe())
print("\nMissing Values:\n", branch_info.isnull().sum())

print("\n--- Circulation Data (circulation) ---")
print("Head:\n", circulation.head())
print("\nInfo:")
circulation.info()
print("\nDescription:\n", circulation.describe())
print("\nMissing Values:\n", circulation.isnull().sum())

print("\n--- Visits Data (visits) ---")
print("Head:\n", visits.head())
print("\nInfo:")
visits.info()
print("\nDescription:\n", visits.describe())
print("\nMissing Values:\n", visits.isnull().sum())

print("\n--- Registrations Data (registrations) ---")
print("Head:\n", registrations.head())
print("\nInfo:")
registrations.info()
print("\nDescription:\n", registrations.describe())
print("\nMissing Values:\n", registrations.isnull().sum())

print("\n--- Workstation Usage Data (workstation_usage) ---")
print("Head:\n", workstation_usage.head())
print("\nInfo:")
workstation_usage.info()
print("\nDescription:\n", workstation_usage.describe())
print("\nMissing Values:\n", workstation_usage.isnull().sum())

print("\n--- Events Data (events) ---")
print("Head:\n", events.head())
print("\nInfo:")
events.info()
print("\nDescription:\n", events.describe())
print("\nMissing Values:\n", events.isnull().sum())

# --- 2. Overall Library Usage Trends ---
# This section analyzes and visualizes the high-level trends in TPL's performance
# across all branches for key metrics over time.

print("\n--- 2. Overall Library Usage Trends ---")

# Merge all usage dataframes into a single dataframe based on 'Year' and 'BranchCode'.
# Using 'outer' merge to ensure all years and branches are included, even if some data is missing.
usage_data_merged = circulation.merge(visits, on=['Year', 'BranchCode'], how='outer') \
                        .merge(registrations, on=['Year', 'BranchCode'], how='outer') \
                        .merge(workstation_usage, on=['Year', 'BranchCode'], how='outer')

# Fill NaN values with 0 for numerical columns after merging.
# This is important for accurate summation of usage metrics.
for col in ['Circulation', 'Visits', 'Registrations', 'Sessions']:
    usage_data_merged[col] = usage_data_merged[col].fillna(0)

# Aggregate yearly totals for all metrics.
# This provides a summary of TPL's overall performance evolution.
yearly_summary = usage_data_merged.groupby('Year')[['Circulation', 'Visits', 'Registrations', 'Sessions']].sum().reset_index()

print("\n--- Yearly Summary of Library Usage ---")
print(yearly_summary)

# Plotting overall trends using Plotly Express for interactivity.
# These line plots show how each key metric has changed year over year.
fig_circ = px.line(yearly_summary, x='Year', y='Circulation', title='Total Circulation Over Time')
fig_circ.show()

fig_visits = px.line(yearly_summary, x='Year', y='Visits', title='Total Visits Over Time')
fig_visits.show()

fig_reg = px.line(yearly_summary, x='Year', y='Registrations', title='Total Registrations Over Time')
fig_reg.show()

fig_ws = px.line(yearly_summary, x='Year', y='Sessions', title='Total Workstation Sessions Over Time')
fig_ws.show()

# --- 3. Branch-Specific Performance Analysis ---
# This section focuses on the performance of individual library branches.
# It helps identify top/bottom performers and potential correlations with branch attributes.

print("\n--- 3. Branch-Specific Performance Analysis ---")

# Merge all data into a single DataFrame for comprehensive analysis.
# This combines usage statistics with detailed branch information.
full_data = usage_data_merged.merge(branch_info, on='BranchCode', how='left')

# Calculate total performance metrics per branch across all years.
# 'first' is used for 'SquareFootage' and 'ServiceTier' as they are static attributes per branch.
branch_performance = full_data.groupby('BranchName').agg({
    'Circulation': 'sum',
    'Visits': 'sum',
    'Registrations': 'sum',
    'Sessions': 'sum',
    'SquareFootage': 'first',
    'ServiceTier': 'first'
}).reset_index()

print("\n--- Branch Performance Summary (All Years) ---")
print(branch_performance.head())

# Sort and display top/bottom branches for each metric.
# This highlights branches with exceptional or struggling performance.
print("\n--- Top 10 Branches by Total Circulation ---")
print(branch_performance.nlargest(10, 'Circulation'))

print("\n--- Bottom 10 Branches by Total Circulation ---")
print(branch_performance.nsmallest(10, 'Circulation'))

print("\n--- Top 10 Branches by Total Visits ---")
print(branch_performance.nlargest(10, 'Visits'))

print("\n--- Bottom 10 Branches by Total Visits ---")
print(branch_performance.nsmallest(10, 'Visits'))

print("\n--- Top 10 Branches by Total Registrations ---")
print(branch_performance.nlargest(10, 'Registrations'))

print("\n--- Bottom 10 Branches by Total Registrations ---")
print(branch_performance.nsmallest(10, 'Registrations'))

print("\n--- Top 10 Branches by Total Workstation Sessions ---")
print(branch_performance.nlargest(10, 'Sessions'))

print("\n--- Bottom 10 Branches by Total Workstation Sessions ---")
print(branch_performance.nsmallest(10, 'Sessions'))

# Visualizations for branch performance using Plotly Express.
# Bar charts for top 15 branches provide a quick visual comparison.
fig_branch_circ = px.bar(branch_performance.nlargest(15, 'Circulation'),
                         x='Circulation', y='BranchName', orientation='h',
                         title='Top 15 Branches by Total Circulation (All Years)')
fig_branch_circ.show()

fig_branch_visits = px.bar(branch_performance.nlargest(15, 'Visits'),
                         x='Visits', y='BranchName', orientation='h',
                         title='Top 15 Branches by Total Visits (All Years)')
fig_branch_visits.show()

fig_branch_reg = px.bar(branch_performance.nlargest(15, 'Registrations'),
                        x='Registrations', y='BranchName', orientation='h',
                        title='Top 15 Branches by Total Registrations (All Years)')
fig_branch_reg.show()

fig_branch_ws = px.bar(branch_performance.nlargest(15, 'Sessions'),
                       x='Sessions', y='BranchName', orientation='h',
                       title='Top 15 Branches by Total Workstation Sessions (All Years)')
fig_branch_ws.show()

# Scatter plots to explore correlations between branch attributes and usage.
# This helps understand if factors like size influence performance.
fig_sqft_circ = px.scatter(branch_performance, x='SquareFootage', y='Circulation',
                           hover_name='BranchName', title='Circulation vs. Square Footage')
fig_sqft_circ.show()

fig_sqft_visits = px.scatter(branch_performance, x='SquareFootage', y='Visits',
                            hover_name='BranchName', title='Visits vs. Square Footage')
fig_sqft_visits.show()

# --- 4. Programs and Events Analysis ---
# This section analyzes the types of programs and events offered, their distribution,
# and trends over time to understand engagement and offerings.

print("\n--- 4. Programs and Events Analysis ---")

# Clean event descriptions by removing HTML tags for better readability.
events['description'] = events['description'].apply(lambda x: re.sub(r'<[^>]*>', '', str(x)))

# Convert 'startdate' to datetime objects for time-based analysis.
# 'errors='coerce'' will turn unparseable dates into NaT (Not a Time).
events['startdate'] = pd.to_datetime(events['startdate'], errors='coerce')

# Analyze top event types based on the three event type columns.
# This helps identify the most common categories of programs offered.
print("\n--- Top 10 Event Types (eventtype1) ---")
print(events['eventtype1'].value_counts().nlargest(10))

print("\n--- Top 10 Event Types (eventtype2) ---")
print(events['eventtype2'].value_counts().nlargest(10))

print("\n--- Top 10 Event Types (eventtype3) ---")
print(events['eventtype3'].value_counts().nlargest(10))

# Analyze top age groups targeted by events.
# This provides insight into who the programs are designed for.
print("\n--- Top 5 Age Groups (agegroup1) ---")
print(events['agegroup1'].value_counts().nlargest(5))

# Analyze the number of events per library.
# This shows which branches are most active in terms of program offerings.
print("\n--- Top 10 Libraries by Number of Events ---")
print(events['library'].value_counts().nlargest(10))

# Plotting top event types using Plotly Express.
fig_event_types = px.bar(events['eventtype1'].value_counts().nlargest(10).reset_index(),
                         x='count', y='eventtype1', orientation='h',
                         title='Top 10 Event Types (eventtype1)')
fig_event_types.show()

# Plotting top age groups using Plotly Express.
fig_age_groups = px.bar(events['agegroup1'].value_counts().nlargest(5).reset_index(),
                        x='count', y='agegroup1', orientation='h',
                        title='Top 5 Age Groups for Events')
fig_age_groups.show()

# Plotting events per library using Plotly Express.
fig_events_per_library = px.bar(events['library'].value_counts().nlargest(10).reset_index(),
                                x='count', y='library', orientation='h',
                                title='Top 10 Libraries by Number of Events')
fig_events_per_library.show()

# Calculate and plot the monthly trend of events.
# This helps identify seasonality or changes in event frequency over time.
# First, extract year and month to create a period.
events['month_year'] = events['startdate'].dt.to_period('M')
# Count events per month and sort by time.
monthly_events = events['month_year'].value_counts().sort_index().reset_index()
monthly_events.columns = ['Month_Year', 'Event_Count']
# Convert Month_Year back to datetime for plotting
monthly_events['Month_Year'] = monthly_events['Month_Year'].dt.to_timestamp()

fig_monthly_events = px.line(monthly_events, x='Month_Year', y='Event_Count',
                             title='Monthly Trend of Events')
fig_monthly_events.show()
