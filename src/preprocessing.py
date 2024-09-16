import pandas as pd
import zipfile
import os
import logging

def quality_gates(df):
    expected_columns = {
        'Open time': 'int64',
        'Open': 'float64',
        'High': 'float64',
        'Low': 'float64',
        'Close': 'float64',
        'Volume': 'float64',
        'Close time': 'int64',
        'Base asset volume': 'float64',
        'Number of trades': 'int64',
        'Taker buy base volume': 'float64',
        'Taker buy base asset volume': 'float64',
        'Ignore': 'float64'
    }

    # Check for missing columns
    missing_columns = set(expected_columns.keys()) - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing expected columns: {missing_columns}")

    # Check for unexpected columns
    unexpected_columns = set(df.columns) - set(expected_columns.keys())
    if unexpected_columns:
        raise ValueError(f"Unexpected columns found: {unexpected_columns}")

    # Check data types
    for col, expected_dtype in expected_columns.items():
        if df[col].dtype != expected_dtype:
            raise TypeError(f"Column '{col}' has incorrect data type. Expected {expected_dtype}, got {df[col].dtype}")

    logging.info("Quality gates passed: All expected columns are present with correct data types.")

def preprocess_data(data_dir):
    '''
    Params :
        data_dir :  raw data directory path
        Output : Historical data avilable in the directory 

        Give the data directory where zip files that are download from  binance api
        it will extract and read the csv files. 
    '''

    all_data = []
    for file in sorted(os.listdir(data_dir)):
        if file.endswith('.zip'):
            file_path = os.path.join(data_dir, file)
            logging.info(f"Processing {file_path}")
            try:
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    csv_filename = zip_ref.namelist()[0]
                    with zip_ref.open(csv_filename) as csvfile:
                        df = pd.read_csv(csvfile, header=None)
                        all_data.append(df)
            except Exception as e:
                logging.error(f"Error processing {file_path}: {e}")
    if all_data:
        df_all = pd.concat(all_data, ignore_index=True)
        
        # columns from https://developers.binance.com/docs/derivatives/coin-margined-futures/market-data/Kline-Candlestick-Data
        # data definitions
        df_all.columns = [
            'Open time', 'Open', 'High', 'Low', 'Close', 'Volume',
            'Close time', 'Base asset volume', 'Number of trades',
            'Taker buy base volume', 'Taker buy base asset volume', 'Ignore'
        ]
        quality_gates(df_all)
        return df_all
    else:
        logging.error("No data to process.")
        return pd.DataFrame()
