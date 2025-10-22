import requests
import pandas as pd
import logging

from typing import Union

# configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


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
        response = requests.get(url, timeout=timeout)
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Error getting Fear & Greed data: %s", e)
        return None


def index_data_to_pandas(index_data: dict) -> Union[pd.DataFrame, None]:
    """
    Converts the Fear & Greed Index data into a pd.DataFrame.

    Parameters:
    - index_data (dict): 
        The Fear & Greed Index data.

    Returns:
    - pd.DataFrame | None: 
        A DataFrame containing the index data, or None if input is invalid.
    """
    # delete later
    columns_to_drop = [
        'timestamp',
        'time_until_update'
    ]

    try:
        df = pd.DataFrame(index_data)
        # preprocess data
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        df['value_classification'] = df['value_classification'].astype('str')
        df['date'] = pd.to_datetime(df['timestamp'], unit='s')
        df.drop(columns=columns_to_drop, inplace=True)
        return df.sort_values(by='date').reset_index(drop=True)
    except Exception as e:
        logger.info("Error processing data into DataFrame: %s", e)
        return None
    

def get_index_data(url: str, limit: int = 10, format: str = "json") -> Union[pd.DataFrame, None]:
    """
    """
    index_data = get_index(url=url, limit=limit, format=format)
    return index_data_to_pandas(index_data=index_data)
