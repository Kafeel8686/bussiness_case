import asyncio
import logging
from datetime import datetime
from src.utils import setup_logging
from src.downloader import download_data
from src.preprocessing import preprocess_data
from src.analysis import evaluate_data_quality, plot_closing_price
from src.utils import ensure_directory
from src.report_generator import generate_report ,get_steps_description


def run_pipeline():
    logging.info("Starting pipeline...")
    data_dir = 'data/raw'
    reports_dir = 'reports'
    ensure_directory(data_dir)
    ensure_directory(reports_dir)

    # Define date range
    start_date = datetime(2017, 8, 1)
    end_date = datetime(2024, 6, 1) 

    # Download data
    asyncio.run(download_data(start_date, end_date, data_dir))

    # Preprocess data
    df = preprocess_data(data_dir)
    if df.empty:
        logging.error("No data available after preprocessing. Exiting pipeline.")
        return

    # Analyze data
    closing_price_plot = plot_closing_price(df, reports_dir)
    report = evaluate_data_quality(df, reports_dir)
    report['closing_price_plot'] = closing_price_plot
    report['steps_description'] = get_steps_description()
    # Generate report
    generate_report(report, reports_dir)
    logging.info("Pipeline completed successfully.")


if __name__ == '__main__':
    setup_logging()
    run_pipeline()

