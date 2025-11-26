import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.metrics import mean_squared_error, mean_absolute_error

# Setup directories
DATA_PATH = "../data/toronto-island-ferry-ticket-counts.csv"
OUTPUT_DIR = "../output/figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Set plot style
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

def load_and_preprocess():
    print("Loading data...")
    df = pd.read_csv(DATA_PATH)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df.set_index('Timestamp', inplace=True)
    df.sort_index(inplace=True)
    
    # Resample to Weekly
    df_weekly = df[['Sales Count', 'Redemption Count']].resample('W').sum()
    df_weekly.rename(columns={'Sales Count': 'Sales', 'Redemption Count': 'Redemptions'}, inplace=True)
    return df_weekly

def plot_sales_redemptions(df):
    print("Plotting Sales and Redemptions...")
    plt.figure(figsize=(14, 7))
    plt.plot(df.index, df['Sales'], label='Sales', alpha=0.8)
    plt.plot(df.index, df['Redemptions'], label='Redemptions', alpha=0.8)
    plt.title('Weekly Ferry Ticket Sales and Redemptions')
    plt.xlabel('Date')
    plt.ylabel('Count')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'sales_redemptions_over_time.png'))
    plt.close()

def plot_seasonality(df):
    print("Plotting Seasonality...")
    df_seasonal = df.copy()
    df_seasonal['Month'] = df_seasonal.index.month
    
    plt.figure(figsize=(12, 6))
    sns.boxplot(x='Month', y='Sales', data=df_seasonal)
    plt.title('Distribution of Weekly Sales by Month')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'sales_by_month_boxplot.png'))
    plt.close()

def decompose_series(df):
    print("Decomposing Time Series...")
    # Decompose Sales
    decomposition = seasonal_decompose(df['Sales'], model='additive', period=52) # Weekly data, annual seasonality
    
    fig = decomposition.plot()
    fig.set_size_inches(14, 10)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'decomposition.png'))
    plt.close()

def forecast_sales(df):
    print("Forecasting...")
    # Prepare data
    sales_data = df['Sales']
    
    # Split train/test (last year as test)
    train_size = int(len(sales_data) * 0.85)
    train_data = sales_data.iloc[:train_size]
    test_data = sales_data.iloc[train_size:]
    
    # Fit model
    model = ExponentialSmoothing(
        train_data,
        seasonal_periods=52,
        trend='add',
        seasonal='add',
        use_boxcox=True,
        initialization_method="estimated"
    ).fit()
    
    # Forecast
    forecast = model.forecast(len(test_data))
    
    # Metrics
    rmse = np.sqrt(mean_squared_error(test_data, forecast))
    mae = mean_absolute_error(test_data, forecast)
    
    print(f"Forecast RMSE: {rmse:.2f}")
    print(f"Forecast MAE: {mae:.2f}")
    
    # Plot
    plt.figure(figsize=(14, 7))
    plt.plot(train_data.index, train_data, label='Training Data')
    plt.plot(test_data.index, test_data, label='Test Data (Actual)', color='green')
    plt.plot(test_data.index, forecast, label='Forecast', color='red', linestyle='--')
    plt.title('Ferry Ticket Sales Forecast (Holt-Winters)')
    plt.xlabel('Date')
    plt.ylabel('Sales Count')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'forecast.png'))
    plt.close()
    
    return rmse, mae

if __name__ == "__main__":
    try:
        df_weekly = load_and_preprocess()
        plot_sales_redemptions(df_weekly)
        plot_seasonality(df_weekly)
        decompose_series(df_weekly)
        forecast_sales(df_weekly)
        print("Analysis complete. Plots saved.")
    except Exception as e:
        print(f"An error occurred: {e}")
