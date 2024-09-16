from jinja2 import Environment, FileSystemLoader
import logging
import os

def generate_report(report, reports_dir):
    logging.info("Generating HTML report...")
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('report_template.html')

    html_out = template.render(report=report)
    report_path = os.path.join(reports_dir, 'report.html')
    with open(report_path, 'w') as f:
        f.write(html_out)
    logging.info(f"Report generated at {report_path}")



def get_steps_description():
    steps_description = [
        {
            'title': 'Data Download',
            'description': 'Downloaded historical 1-minute Kline data for BTCUSDT from Binance starting from January 2017 to June 2024 using asynchronous requests, ensuring data is not re-downloaded if it already exists.'
        },
        {
            'title': 'Data Preprocessing',
            'description': 'Unzipped and read CSV files, combined them into a single DataFrame, and assigned appropriate column names.'
        },
        {
            'title': 'Data Quality Evaluation',
            'description': 'Evaluated the dataset for completeness, missing values, duplicates, data types, logical consistency, and anomalies.'
        },
        {
            'title': 'Anomaly Detection',
            'description': 'Identified unusual spikes and drops in price and volume using statistical methods and moving averages.'
        },
        {
            'title': 'Report Generation',
            'description': 'Generated an HTML report summarizing the findings, including charts and observations.'
        }
    ]
    return steps_description


def generate_data_catalogue():
    data_catalogue = [
        {'name': 'Open time', 'description': 'Start time of the candlestick (in milliseconds since epoch, UTC).'},
        {'name': 'Open', 'description': 'Price at which the candlestick opened.'},
        {'name': 'High', 'description': 'Highest price during the candlestick period.'},
        {'name': 'Low', 'description': 'Lowest price during the candlestick period.'},
        {'name': 'Close', 'description': 'Price at which the candlestick closed.'},
        {'name': 'Volume', 'description': 'Trading volume during the candlestick period.'},
        {'name': 'Close time', 'description': 'End time of the candlestick (in milliseconds since epoch, UTC).'},
        {'name': 'Quote asset volume', 'description': 'Volume of the quote asset traded during the candlestick period.'},
        {'name': 'Number of trades', 'description': 'Number of trades that took place during the candlestick period.'},
        {'name': 'Taker buy base asset volume', 'description': 'Volume of the base asset bought by takers.'},
        {'name': 'Taker buy quote asset volume', 'description': 'Volume of the quote asset bought by takers.'},
        {'name': 'Ignore', 'description': 'This field is deprecated and should be ignored.'}
    ]
    return data_catalogue

