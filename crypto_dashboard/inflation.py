import os
from dotenv import load_dotenv

load_dotenv()

infl_api_url = os.getenv('infl_api_url')
infl_api_key = os.getenv('infl_api_key')

from datetime import datetime
import requests
import pandas as pd
import logging
from typing import Union

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

def get_cpi(
        url: str = infl_api_url,
        key: str = infl_api_key,
        limit: int = 13,
        format: str = "json",
        timeout: int = 10
) -> Union[pd.DataFrame, None]:
    """
    Fetches the CPI index for the specified limit; used to calculate inflation.
    Parameters:
    - url (str): The API endpoint with placeholders for key, format, and limit.
    - key (str): API key provided by World Bank.
    - limit (int): The number months for which to receive CPI indexes.
    - format (str): The response format: "json", "csv", "xml", or "xlsx".
    - timeout (int): The timeout for HTTP request in seconds.
    Returns:
    - pd.DataFrame or None.
    """

    url = url.format(key = key, limit = limit, format = format)
    try:
        response = requests.get(url, timeout=10).json()
        df = response['observations']
        data = pd.DataFrame(df)
        data = data.drop(columns = ['realtime_start', 'realtime_end'])

        #transform string "value" to numerical value
        data['value'] = pd.to_numeric(data['value'], errors = 'coerce')

        #transform "date" to proper date format
        data['date'] = pd.to_datetime(data['date'], format='%Y-%m-%d')

        #sort by "date" in descending order
        data.sort_values(by = 'date', ascending=False, inplace = True)
        data.reset_index(drop=True, inplace=True)

        data['hist_inf_rate'] = round((((data['value'] / data['value'].shift(-1)) - 1) * 100) * 10, 1)
        data['date_formatted'] = data['date'].dt.strftime("%B %y")

        return data

    except requests.exceptions.RequestException as e:
        logger.error("Error getting fear & greed data: %s", e)
        return None
    
def get_inflation(data: pd.DataFrame) -> Union[pd.DataFrame, None]:
    """
    Converts dict with cpi indexes into dataframe showing inflation estimate: "High", "Moderate", "Low".
    Parameters: 
    - cpi indexes (pd.DataFrame).
    Returns:
    - pd.DataFrame containing inflation trend for the current date.
    """

    try:
        #extract the cpi value for the recent month
        first_value = float(round(data['value'].iloc[0], 2))

        #extract the cpi value for the previous month
        last_value = float(round(data['value'].iloc[1], 2))

        #calculate monthly inflation
        monthly_inflation_rate = ((first_value / last_value) - 1) * 100

        #based on the monthly inflation, assume what annual inflation would be
        annualized_inflation = ((1 + monthly_inflation_rate / 100) ** 12 - 1) * 100

        #compare annual inflation to Central Bank target and produce estimate
        if annualized_inflation <= 2:
            estimate = "Low"
        elif annualized_inflation <= 5:
            estimate = "Moderate"
        elif annualized_inflation > 5:
            estimate = "High"
        
        current_inflation = round((monthly_inflation_rate * 10), 1)

        #calculate inflation growth
        back_end = data['value'].iloc[-1]
        front_end = data['value'].iloc[0]
        inflation_growth = round((((front_end - back_end) / back_end) * 100), 1)

        #get the current date
        date = datetime.now().date()
        
        #create a final dataframe with the current date and inflation estimate
        inflation = pd.DataFrame({'date': [date],
                                  'current_inflation': [current_inflation],
                                  'inflation_estimate': [estimate],
                                  'inflation_growth': [inflation_growth]
                                  })    
        return inflation
    except Exception as e:
        logger.info("Error processing data into DataFrame: %s", e)
        return None