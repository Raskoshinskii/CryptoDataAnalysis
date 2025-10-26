import yfinance as yf
import pandas as pd
import logging
from datetime import datetime
from typing import Union

from typing import Union

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

def get_raw_stockmarket_data(ticker_name: str="^GSPC", period: str="1y") -> Union[pd.DataFrame, None]:
    """
    Fetches stock market value for the last month.
    Parameters:c
    - ticker_name (str): symbol for stockmarket value, specified by the yfinance library.
    - period (str): period for which to fetch data. Default is 1 month.
    Returns:
    - pd.DataFrame | None
    """
    try:
        data = yf.Ticker(ticker_name).history(period = period)
        if data.empty:
            logger.info("No stock market data found for the ticker: %s", ticker_name)
            return None
        return data
    except Exception as e:
        logger.error(f"Error getting stock market data: %s", e)
        return None

def get_yearly_stockmarket_trend(stockmarket_data: pd.DataFrame) -> Union[pd.DataFrame, None]:
    """
    Converts the raw stockmarket pd.DataFrame into a pd.DataFrame that contains:
    - current data;
    - trend estimator showing if stock market is "Rising" or "Falling".
    Parameters:
    - stockmarket_data (dataframe).
    Returns:c
    - pd.DataFrame | None
    """
    try:
        df = stockmarket_data.reset_index()[['Close']].copy()
        df = df.rename(columns={'Close': 'stockmarket_value'})
        start_year = stockmarket_data.iloc[-1, 1]
        end_year = stockmarket_data.iloc[0, 1]
        if start_year > end_year:
            estimate = "Rising"
        elif start_year == end_year:
            estimate = "Stable"
        else:
            estimate = "Falling"
        date = datetime.now().date()
        stockmarket = pd.DataFrame({'date': [date], 'stockmarket': [estimate]})
        return stockmarket
    except Exception as e:
        logger.info("Error preprocessing stock market data: %s", e)
        return None

def get_montly_stockmarket_trend(stockmarket_data: pd.DataFrame) -> Union[pd.DataFrame, None]:
    """
    Converts the raw stockmarket pd.DataFrame into a pd.DataFrame that contains:
    - current data;
    - trend estimator showing if stock market is "Rising" or "Falling".
    Parameters:
    - stockmarket_data (dataframe).
    Returns:c
    - pd.DataFrame | None
    """
    try:
        df = stockmarket_data.reset_index()[['Close']].copy()
        df = df.rename(columns={'Close': 'stockmarket_value'})
        start_month = df.iloc[-25, 0]
        end_month = df.iloc[-1, 0]
        if start_month < end_month:
            estimate = "Rising"
        elif start_month == end_month:
            estimate = "Stable"
        else:
            estimate = "Falling"
        date = datetime.now().date()
        stockmarket = pd.DataFrame({'date': [date], 'stockmarket': [estimate]})
        return stockmarket
    except Exception as e:
        logger.info("Error preprocessing stock market data: %s", e)
        return None

def get_yearly_stockmarket_data_for_dashboard(stockmarket_data: pd.DataFrame) -> Union[pd.DataFrame, None]:
    """
    Converts the raw stockmarket pd.DataFrame into a pd.DataFrame that contains:
    - current data;
    - trend estimator showing if stock market is "Rising" or "Falling".
    Parameters:
    - stockmarket_data (dataframe).
    Returns:c
    - pd.DataFrame | None
    """
    try:
        df = stockmarket_data.reset_index()[['Date','Close']].copy()
        df = df.rename(columns={'Close': 'stockmarket_value', 'Date': 'date'})
        df['date'] = df['date'].dt.date
        return df
    except Exception as e:
        logger.info("Error preprocessing stock market data: %s", e)
        return None