import math
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objects import Figure
from typing import Union

def format_timedelta(td_series: pd.Series) -> str:
    """Convert timedelta to readable format '00 hours and 00 minutes'"""
    data = td_series.iloc[0]
    total_seconds = data.total_seconds()
    hours = int((total_seconds // 3600))
    minutes = int((total_seconds % 3600) // 60)
    formatted = f"{hours} hours and {minutes:02d} minutes"
    res = td_series.copy()
    res.iloc[0] = formatted
    return res

def create_gauge(value: Union[int, float]) -> Figure:
    """
    Create a gauge with smooth gradient
    """
    # Calculate color based on current value (red -> yellow -> green)
    if value <= 50:
        # Red to Yellow
        r = 255
        g = int(255 * (value / 50))
        b = 0
    else:
        # Yellow to Green
        r = int(255 * (1 - (value - 50) / 50))
        g = 255
        b = 0
    
    number_color = f'rgb({r}, {g}, {b})'
    
    # Create smooth gradient by adding many small steps
    steps = []
    for i in range(100):
        # Calculate color based on position (red -> yellow -> green)
        if i <= 50:
            # Red to Yellow
            r_step = 255
            g_step = int(255 * (i / 50))
            b_step = 0
        else:
            # Yellow to Green
            r_step = int(255 * (1 - (i - 50) / 50))
            g_step = 255
            b_step = 0
        color = f'rgb({r_step}, {g_step}, {b_step})'
        steps.append({'range': [i, i+1], 'color': color})
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        number = {'font': {'size': 48, 'color': number_color},  # Use dynamic color here
                  'suffix': '',
                  'valueformat': 'd'},
        gauge = {
            'axis': {'range': [0, 100],
                     'showticklabels': False,
                     'ticks': '',
                     'tickwidth': 0},
            'bar': {'color': "rgba(0,0,0,0)"},
            'bgcolor': "white",
            'borderwidth': 0,
            'bordercolor': "gray",
            'steps': steps,
            'threshold': {
                'line': {'color': "black", 'width': 3},
                'thickness': 0.4,
                'value': value
            }
        }
    ))
    
    fig.update_layout(
        height=150,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor='dark blue',
        font={'family': 'Arial'}
    )
    return fig
    
def get_index_recommendation(current_value: int) -> str:
    """ Returns string based on inputed numeric value. """
    if current_value <= 50:
        return "buy."
    elif current_value <= 100:
        return "sell."
    
def traffic_lights(value: str) -> None:
    """ Displays traffic lights visualization based on the trading recommendations. """

    if value == "It's safe to buy!" or value == "Sell now! The Crypto market is a bubble!":
        active_color = "green"
    elif value == "Stop! Don't buy!" or value == "Don't sell! Crypto will rise further!":
        active_color = "red"
    elif value == "Wait! The market is uncertain!":
        active_color = "yellow"
    else:
        active_color = "gray"

    #Traffic lights CSS
    st.markdown("""
    <style>
    .traffic-light {
        width: 100px;
        background-color: #333;
        border-radius: 15px;
        padding: 15px;
        margin: 20x auto;
        border: 3px solid #555;
    }
    .light {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        margin: 10px auto;
        border: 2px solid #666;
        background-color: #222;
    }
    .red.active { background-color: #ff4444; box-shadow: 0 0 20px #ff4444; }
    .yellow.active { background-color: #ffff44; box-shadow: 0 0 20px #ffff44; }
    .green.active { background-color: #44ff44; box-shadow: 0 0 20px #44ff44; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="traffic-light">
        <div class="light red {'active' if active_color == 'red' else ''}"></div>
        <div class="light yellow {'active' if active_color == 'yellow' else ''}"></div>
        <div class="light green {'active' if active_color == 'green' else ''}"></div>
        
    </div>
    """, unsafe_allow_html=True)

def get_recommendation(df_index: str, lt_trend: str, df_stockmarket: str, df_inflation: str) -> str:
    """ Generate trading recommendation based on multiple market indicators. """

    if df_index.iloc[0]['value_classification'] == 'Fear' or df_index.iloc[0]['value_classification'] == 'Extreme Fear' \
        or df_index.iloc[0]['value_classification'] == 'Neutral' and \
        lt_trend == 'Long-term trend is stable' or lt_trend == 'Long-term trend is unstable' and \
        df_stockmarket.iloc['stockmarket'] == 'Rising' and \
            df_inflation.iloc[0]['inflation'] == 'Low' or df_inflation.iloc[0]['inflation'] == 'Moderate':
        return "It's safe to buy!"
    
    elif df_index.iloc[0]['value_classification'] == 'Fear' or df_index.iloc[0]['value_classification'] == 'Extreme Fear' and \
    lt_trend == 'Long-term trend is stable' or lt_trend == 'Long-term trend is unstable' and \
        df_stockmarket.iloc[0]['stockmarket'] == 'Falling' and \
            df_inflation.iloc[0]['inflation'] == 'Low' or df_inflation.iloc[0]['inflation'] == 'Moderate' or \
            df_inflation.iloc[0]['inflation'] == 'High':
        return "Stop! Don't buy!"
    
    elif df_index.iloc[0]['value_classification'] == 'Greed' or  df_index.iloc[0]['value_classification'] == 'Extreme Greed' and \
    lt_trend == 'Long-term trend is stable' or lt_trend == 'Long-term trend is unstable' and \
        df_stockmarket.iloc[0]['stockmarket'] == 'Rising' and \
            df_inflation.iloc[0]['inflation'] == 'Low' or df_inflation.iloc[0]['inflation'] == 'Moderate':
        return "Don't sell! Crypto will rise further!"
    
    elif df_index.iloc[0]['value_classification'] == 'Greed' or  df_index.iloc[0]['value_classification'] == 'Extreme Greed' and \
    lt_trend == 'Long-term trend is stable' or lt_trend == 'Long-term trend is unstable' and \
        df_stockmarket.iloc[0]['stockmarket'] == 'Falling' and \
            df_inflation.iloc[0]['inflation'] == 'Low' or df_inflation.iloc[0]['inflation'] == 'Moderate' or \
            df_inflation.iloc[0]['inflation'] == 'High':
        return "Sell now! The Crypto market is a bubble!"
    
    elif df_index.iloc[0]['value_classification'] == 'Neutral' and \
    lt_trend == 'Long-term trend is stable' or lt_trend == 'Long-term trend is unstable' and \
        df_stockmarket.iloc[0]['stockmarket'] == 'Rising' and \
            df_inflation.iloc[0]['inflation'] == 'Low' or df_inflation.iloc[0]['inflation'] == 'Moderate' or \
            df_inflation.iloc[0]['inflation'] == 'High':
        return "It's safe to buy!"
    
    elif df_index.iloc[0]['value_classification'] == 'Neutral' and \
    lt_trend == 'Long-term trend is stable' or lt_trend == 'Long-term trend is unstable' and \
        df_stockmarket.iloc[0]['stockmarket'] == 'Falling' and \
            df_inflation.iloc[0]['inflation'] == 'Low' or df_inflation.iloc[0]['inflation'] == 'Moderate' or \
            df_inflation.iloc[0]['inflation'] == 'High':
        return "Wait! The market is uncertain!"
    
def get_index_trend(df: pd.DataFrame) -> str:
    """ Determine if Fear & Greed Index trend is stable or not """
    value = df.iloc[0]['value_classification']
    if value == "Fear" or value == "Extreme Fear":
        ef_list = []
        for i in range(21):
            if df.iloc[i]['value'] >= 0 and df.iloc[i]['value'] <= 47:
                ef_list.append(i)
        if len(ef_list) >= 18:
            return "Stable"
        else:
            return "Unstable"
    elif value == "Greed" or value == "Extreme Greed":
        eg_list = []
        for i in range(21):
            if df.iloc[i]['value'] >= 55 and df.iloc[i]['value'] <= 100:
                eg_list.append(i)
        if len(eg_list) >= 18:
            return "Long-term trend is stable"
        else:
            return "Long-term trend is unstable"
        
