import requests
import pandas as pd
import logging

from typing import Union
from functions import format_timedelta

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

from constants import FEAR_GREED_INDEX_URL
URL = FEAR_GREED_INDEX_URL


def get_index(
    url: str,
    timeout: int = 10,
    limit: int = 10,
    format: str = "json"
) -> Union[dict, None]:
    """
    Fetches the Fear & Greed Index data from the specified URL.

    Parameters:
    - url (str): The API endpoint URL with placeholders for limit and format.
    - timeout (int): The timeout for the HTTP request in seconds.
    - limit (int): The number of data points to retrieve.
    - format (str): The response format, either 'json' or 'csv'.

    Returns:
    - dict or None: The JSON response as a dictionary if successful, otherwise None.
    """
    url = url.format(limit=limit, format=format)
    try:
        response = requests.get(url, timeout=timeout).json()
        raw = response['data']
        df = pd.DataFrame(raw)
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        df['value_classification'] = df['value_classification'].astype('str')
        df['timestamp'] = pd.to_numeric(df['timestamp'])
        df['date'] = pd.to_datetime(df['timestamp'], unit='s')
        df.sort_values(by = 'date', ascending = False)
        df['time_until_update'] = pd.to_numeric(df['time_until_update'])
        df['time_until_update'] = pd.to_timedelta(df['time_until_update'], unit='s')
        df['time_until_update'] = format_timedelta(df['time_until_update'])
        df.drop(columns = 'timestamp', inplace = True)
        return df
    except requests.exceptions.RequestException as e:
        logger.error("Error getting Fear & Greed data: %s", e)
        return None