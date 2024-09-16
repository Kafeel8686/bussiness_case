# src/utils.py

import os
import logging
from datetime import datetime, timedelta

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname)s] %(asctime)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

def ensure_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

def daterange(start_date, end_date):
    dates = []
    while start_date <= end_date:
        dates.append(start_date)
        start_date = (start_date.replace(day=28) + timedelta(days=4)).replace(day=1)
    return dates
