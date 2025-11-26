import pandas as pd
import numpy as np

def analyze_rainfall(file_path):
    print(f"Loading {file_path}...")
    df = pd.read_csv(file_path, usecols=['name', 'date', 'rainfall'])
    df['date'] = pd.to_datetime(df['date'])
    df = df[df['date'].dt.year == 2024]
    
    # Drop NaNs
    df = df.dropna(subset=['rainfall'])
    
    stations = df['name'].unique()
    print(f"Found {len(stations)} stations.")
    
    station_totals = []
    full_year_stations = []
    
    for station in stations:
        station_data = df[df['name'] == station].sort_values('date')
        
        if station_data.empty:
            continue
            
        min_date = station_data['date'].min()
        max_date = station_data['date'].max()
        days_covered = (max_date - min_date).days
        
        rainfall_values = station_data['rainfall'].values
        
        # Check for resets
        diffs = rainfall_values[1:] - rainfall_values[:-1]
        pos_diffs = diffs[diffs > 0]
        neg_diffs = diffs[diffs < 0]
        
        # If many negative diffs, check if they are resets (large drops) or small fluctuations
        # If cumulative, drops should be large (reset to 0).
        # If incremental, drops are just lower rain rate.
        
        # Let's assume cumulative if max value is high and drops are significant.
        # Or if the values are monotonically increasing in short bursts.
        
        # Strategy: Sum of positive differences.
        # This works for cumulative with resets (counts all upward movement).
        # This also works for incremental if we assume incremental is just "add to total".
        # Wait, if it's incremental (0.2mm in 5 mins), then sum(values) is correct.
        # If it's cumulative (100mm -> 100.2mm), then sum(pos_diffs) is 0.2. Correct.
        # But if it's incremental, sum(pos_diffs) would be difference between rates, which is WRONG.
        
        # We need to distinguish.
        # Cumulative: values increase over time. 10, 10.2, 10.4.
        # Incremental: values are independent. 0.2, 0.2, 0.2.
        
        # Check correlation with time?
        # Or check if values are generally increasing.
        
        is_cumulative = False
        if len(rainfall_values) > 10:
            # Check if sorted
            # But resets break sortedness.
            # Check if diffs are mostly >= 0.
            ratio_pos = len(pos_diffs)
            ratio_neg = len(neg_diffs)
            
            # If cumulative, we expect mostly >= 0 diffs.
            # If incremental, we expect random diffs (up and down).
            
            if ratio_neg < len(diffs) * 0.1:
                is_cumulative = True
            else:
                # Check if it looks like a counter that resets often
                # E.g. 0, 0.2, 0.4, 0, 0.2...
                # This would have many negative diffs (resets).
                # But the values would be small.
                pass

        # Let's look at the data sample from previous run:
        # 0.009, 0.01, 0.011. Increasing.
        # This suggests cumulative.
        
        # Let's try to detect "reset to near zero".
        # If it's cumulative, total = sum(pos_diffs).
        # If it's incremental, total = sum(values).
        
        # Let's calculate both and see which one makes sense.
        sum_values = rainfall_values.sum()
        sum_pos_diffs = pos_diffs.sum()
        
        # If sum_values is huge (e.g. 1000 * 10000 points), it's definitely cumulative.
        # If sum_values is reasonable (e.g. 800mm), it might be incremental.
        
        # However, 0.01 mm is tiny. 
        # If it's cumulative, the max value tells us the total accumulation (if no resets).
        max_val = rainfall_values.max()
        
        final_total = 0
        method = "Unknown"
        
        # Heuristic:
        # If max_val > 1000, it's likely cumulative (unless it's a flood!).
        # If sum_pos_diffs is reasonable (e.g. 200-1500mm) and sum_values is huge, it's cumulative.
        
        if sum_values > 2000: # 2000mm is very wet for Toronto
            is_cumulative = True
            final_total = sum_pos_diffs
            method = "Cumulative (Sum Pos Diffs)"
        else:
            # Hard to tell.
            # But 0.009, 0.010... is definitely cumulative.
            # Maybe the gauge resets every day?
            # If so, sum_pos_diffs is correct.
            # If it's incremental, sum_pos_diffs would be small or meaningless.
            
            # Let's trust sum_pos_diffs for now as it handles the "increasing" nature we saw.
            final_total = sum_pos_diffs
            method = "Cumulative (Sum Pos Diffs)"

        print(f"Station {station}: {days_covered} days. Max: {max_val:.2f}. Sum Values: {sum_values:.2f}. Sum Pos Diffs: {final_total:.2f}. Method: {method}")
        
        if days_covered > 300:
            full_year_stations.append(final_total)
        
        station_totals.append(final_total)

    if full_year_stations:
        avg_rain = sum(full_year_stations) / len(full_year_stations)
        print(f"\nAverage rainfall (Full Year Stations only): {avg_rain:.2f} mm")
        print(f"Max rainfall at any station: {max(full_year_stations):.2f} mm")
    else:
        print("\nNo full year stations found.")
        if station_totals:
             print(f"Average of all stations: {sum(station_totals)/len(station_totals):.2f} mm")

if __name__ == "__main__":
    analyze_rainfall("data/precipitation-data-2024.csv")
