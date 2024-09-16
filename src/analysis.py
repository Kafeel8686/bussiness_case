import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import logging
import numpy as np
import os
from scipy import stats
from src.utils import ensure_directory
from src.report_generator import generate_data_catalogue

def evaluate_data_quality(df, reports_dir):
    logging.info("Evaluating data quality...")
    report = {}

    report['data_catalogue'] = generate_data_catalogue()

    # convert to date time
    df['Open time'] = pd.to_datetime(df['Open time'], unit='ms')
    df['Close time'] = pd.to_datetime(df['Close time'], unit='ms')

    #Data Completeness
    report['completeness'] = data_completeness(df)

    #Data Quality
    report['quality'] = data_quality_checks(df)

    #Anomalies Detection
    report['anomalies'] = anomalies_detection(df, reports_dir)

    return report

def data_completeness(df):
    logging.info("Checking data completeness...")
    completeness = {}

    # Generate expected timestamps
    start_time = df['Open time'].min()
    end_time = df['Open time'].max()
    expected_index = pd.date_range(start=start_time, end=end_time, freq='1T')
    actual_index = df['Open time']

    # Identify missing timestamps
    missing_timestamps = expected_index.difference(actual_index)
    missing_percentage = (len(missing_timestamps) / len(expected_index)) * 100

    completeness['total_expected'] = len(expected_index)
    completeness['total_missing'] = len(missing_timestamps)
    completeness['missing_percentage'] = round(missing_percentage, 6)
    completeness['missing_timestamps'] = missing_timestamps

    return completeness

def data_quality_checks(df):
    logging.info("Performing data quality checks...")
    quality = {}

    # Missing Values
    missing_values = df.isnull().sum().to_dict()
    quality['missing_values'] = missing_values

    # Duplicates
    duplicates_count = df.duplicated().sum()
    quality['duplicates'] = duplicates_count

    # Remove duplicates
    df.drop_duplicates(inplace=True)

    # # Data Types
    numeric_cols = ['Open', 'High', 'Low', 'Close', 'Volume',
                    'Base asset volume',  'Taker buy base volume', 'Taker buy base asset volume']
    # df[numeric_cols] = df[numeric_cols].astype('float64')

    # Statistical Summary
    stats_summary = df[numeric_cols].describe().to_dict()
    quality['stats_summary'] = stats_summary

    # Logical Consistency Checks
    inconsistent_prices = df[
        (df['High'] < df['Low']) |
        (df['High'] < df['Open']) |
        (df['High'] < df['Close']) |
        (df['Low'] > df['Open']) |
        (df['Low'] > df['Close'])
    ]
    quality['inconsistent_prices_count'] = len(inconsistent_prices)

    negative_value = df[
        (df['Open'] < 0) |
        (df['High'] < 0) |
        (df['Low'] < 0) |
        (df['Close'] < 0) |
        (df['Volume'] < 0)
    ]
    quality['negative_values_count'] = len(negative_value)

    # Zero or Negative Values
    zero_values = df[
        (df['Open'] <= 0) |
        (df['High'] <= 0) |
        (df['Low'] <= 0) |
        (df['Close'] <= 0) |
        (df['Volume'] <= 0)
    ]
    quality['zero_values_count'] = len(zero_values)


    logging.info("Analyzing zero volume instances...")
    zero_volume_df = df[df['Volume'] == 0]
    zero_volume_count = len(zero_volume_df)
    zero_volume_dates = zero_volume_df['Open time'].dt.strftime('%Y-%m-%d').tolist()
    quality['zero_volume_count'] = zero_volume_count 
    quality['zero_volume_dates'] = list(dict.fromkeys(zero_volume_dates))

    return quality

def anomalies_detection(df, reports_dir):
    logging.info("Detecting anomalies...")
    anomalies = {}
    figures_dir = os.path.join(reports_dir, 'figures')
    ensure_directory(figures_dir)


    # Price Anomalies ( percentage in price over pass min by 5%)
    df['Close'] = pd.to_numeric(df['Close'])
    df['Price_change_pct'] = df['Close'].pct_change() * 100
    price_anomalies = df[abs(df['Price_change_pct']) > 5]
    anomalies['price_anomalies_count'] = len(price_anomalies)
    anomalies['price_anomalies'] = price_anomalies[['Open time', 'Price_change_pct']].to_dict(orient='records')

    # Plotting Price Anomalies
    plt.figure(figsize=(15, 7))
    plt.plot(df['Open time'], df['Close'], label='Close Price')
    plt.scatter(price_anomalies['Open time'], df.loc[price_anomalies.index, 'Close'], color='red', label='Anomalies')
    plt.title('BTCUSDT Price with Anomalies Highlighted')
    plt.xlabel('Date')
    plt.ylabel('Closing Price (USDT)')
    plt.legend()
    price_anomalies_plot = os.path.join(figures_dir, 'price_anomalies.png')
    plt.savefig(price_anomalies_plot)
    plt.close()

    # Volume Anomalies
    df['Volume'] = pd.to_numeric(df['Volume'])
    df['Volume_zscore'] = stats.zscore(df['Volume'])
    volume_anomalies = df[abs(df['Volume_zscore']) > 3]
    anomalies['volume_anomalies_count'] = len(volume_anomalies)
    anomalies['volume_anomalies'] = volume_anomalies[['Open time', 'Volume']].to_dict(orient='records')

    # Plotting Volume Anomalies
    plt.figure(figsize=(15, 7))
    plt.plot(df['Open time'], df['Volume'], label='Volume')
    plt.scatter(volume_anomalies['Open time'], df.loc[volume_anomalies.index, 'Volume'], color='red', label='Anomalies')
    plt.title('BTCUSDT Volume with Anomalies Highlighted')
    plt.xlabel('Date')
    plt.ylabel('Volume')
    plt.legend()
    volume_anomalies_plot = os.path.join(figures_dir, 'volume_anomalies.png')
    plt.savefig(volume_anomalies_plot)
    plt.close()

    # Distribution of Price Changes
    plt.figure(figsize=(10, 6))
    sns.histplot(df['Price_change_pct'], kde=True)
    plt.title('Distribution of Per Minute Price Changes (%)')
    plt.xlabel('Price Change (%) (per minute)')
    plt.ylabel('Frequency')
    price_change_dist_plot = os.path.join(figures_dir, 'price_change_distribution.png')
    plt.savefig(price_change_dist_plot)
    plt.close()


    # Calculate a 50-period moving average
    df['MA50'] = df['Close'].rolling(window=50).mean()

    # Calculate deviation from moving average
    df['Deviation'] = df['Close'] - df['MA50']

    # Identify significant deviations (e.g., greater than 2 standard deviations)
    std_dev = df['Deviation'].std()
    significant_deviations = df[np.abs(df['Deviation']) > (2 * std_dev)]
    anomalies['deviations'] = significant_deviations
    plt.figure(figsize=(15, 7))
    plt.plot(df['Open time'], df['Close'], label='Close Price')
    plt.plot(df['Open time'], df['MA50'], label='50-Period MA', color='orange')
    plt.xlabel('Date')
    plt.ylabel('Price (USD)')
    plt.title('BTCUSDT Close Price and 50-Period Moving Average')
    plt.legend()
    plt.tight_layout()
    close_price_ma = os.path.join(figures_dir, 'close_price_ma.png')
    plt.savefig(close_price_ma)
    plt.close()


    # Add plot paths to anomalies dictionary
    anomalies['price_anomalies_plot'] = os.path.relpath(price_anomalies_plot, reports_dir)
    anomalies['volume_anomalies_plot'] = os.path.relpath(volume_anomalies_plot, reports_dir)
    anomalies['price_change_dist_plot'] = os.path.relpath(price_change_dist_plot, reports_dir)
    anomalies['close_price_ma_plot'] = os.path.relpath(close_price_ma, reports_dir)

    return anomalies

def plot_closing_price(df, reports_dir):
    logging.info("Generating closing price plot...")
    figures_dir = os.path.join(reports_dir, 'figures')
    ensure_directory(figures_dir)

    plt.figure(figsize=(15, 7))
    df['Close'] = pd.to_numeric(df['Close'])
    sns.lineplot(x='Open time', y='Close', data=df)
    plt.title('BTCUSDT Closing Price Over Time')
    plt.xlabel('Date')
    plt.ylabel('Closing Price (USDT)')
    plot_path = os.path.join(figures_dir, 'closing_price_over_time.png')
    plt.savefig(plot_path)
    plt.close()
    return os.path.relpath(plot_path, reports_dir)
