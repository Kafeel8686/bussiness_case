import aiohttp
import asyncio
import aiofiles
import os
import logging
from src.utils import ensure_directory, daterange

BASE_URL = 'https://data.binance.vision/data/spot/monthly/klines/BTCUSDT/1m'

async def download_file(session, url, save_path):
    if os.path.exists(save_path):
        logging.info(f"File already exists: {save_path}")
        return
    try:
        async with session.get(url) as response:
            if response.status == 200:
                f = await aiofiles.open(save_path, mode='wb')
                await f.write(await response.read())
                await f.close()
                logging.info(f"Downloaded: {save_path}")
            else:
                logging.warning(f"Failed to download {url}: Status {response.status}")
    except Exception as e:
        logging.error(f"Error downloading {url}: {e}")

async def download_data(start_date, end_date, save_dir):
    ensure_directory(save_dir)
    dates = daterange(start_date, end_date)
    tasks = []
    async with aiohttp.ClientSession() as session:
        for date in dates:
            filename = f"BTCUSDT-1m-{date.strftime('%Y-%m')}.zip"
            url = f"{BASE_URL}/{filename}"
            save_path = os.path.join(save_dir, filename)
            task = asyncio.create_task(download_file(session, url, save_path))
            tasks.append(task)
        await asyncio.gather(*tasks)
