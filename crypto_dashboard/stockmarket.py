import yfinance as yf
import pandas as pd
import logging

from typing import Union

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_stockmarket(ticker_name: str = "^GSPC", period: str = "1mo") -> Union[pd.DataFrame, None]:
    """
    Fetches historical stock market data for the given ticker.

    Parameters:
    - ticker_name (str): 
        The stock ticker symbol. Default is "^GSPC"
    - period (str): 
        The period for which to fetch data. Default is "1mo".

    Returns:
    - pd.DataFrame | None: A DataFrame containing the historical stock data, or None
    """
    try:
        data = yf.Ticker(ticker_name).history(period=period)

        if data.empty:
            logger.info("No stock market data found for ticker: %s", ticker_name)
            return None
        return data
    except Exception as e:
        logger.error("Error getting stock market data: %s", e)
        return None