# Crypto Fear & Greed Index Dashboard

A simple Streamlit dashboard that visualizes the Crypto Fear & Greed Index data using the Alternative.me API.

## Features

- **Real-time Index Display**: Shows the current Fear & Greed Index value with a gauge visualization
- **Historical Trends**: Line chart showing historical data for the selected time period
- **Statistical Analysis**: Distribution charts and summary statistics
- **Interactive Controls**: Adjustable data range and auto-refresh options
- **Classification Breakdown**: Pie chart showing distribution of different sentiment classifications

## Index Scale

- **0-25**: Extreme Fear 😰 (Red)
- **26-45**: Fear 😟 (Orange) 
- **46-55**: Neutral 😐 (Yellow)
- **56-75**: Greed 😊 (Light Green)
- **76-100**: Extreme Greed 🤑 (Green)

## Installation

1. Install the required dependencies:
```bash
pip install streamlit plotly pandas requests
```

Or install from the requirements file:
```bash
pip install -r requirements_streamlit.txt
```

## Running the Dashboard

### Option 1: Direct command
```bash
streamlit run crypto_dashboard/streamlit_app.py
```

### Option 2: Using the run script
```bash
./run_dashboard.sh
```

The dashboard will be available at `http://localhost:8501`

## Usage

1. **Select Data Range**: Use the sidebar to choose how many days of historical data to display (7, 30, 60, 100, or 200 days)

2. **Auto-refresh**: Enable auto-refresh to update the data every 5 minutes automatically

3. **Current Metrics**: View the current index value, classification, and last update date

4. **Gauge Visualization**: See the current sentiment level on an easy-to-read gauge

5. **Historical Analysis**: Analyze trends over time with the interactive line chart

6. **Statistics**: Review statistical summaries and distribution analyses

7. **Raw Data**: Expand the "View Raw Data" section to see the underlying dataset

## Data Source

The dashboard uses the [Alternative.me Crypto Fear & Greed Index API](https://alternative.me/crypto/fear-and-greed-index/) which provides sentiment analysis of the cryptocurrency market.

## Features Overview

- **Interactive Visualizations**: Built with Plotly for responsive, interactive charts
- **Real-time Data**: Fetches live data from the Alternative.me API
- **Responsive Design**: Works on desktop and mobile devices
- **Error Handling**: Graceful error handling for API failures
- **Performance**: Efficient data loading and caching