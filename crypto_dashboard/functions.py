import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

def format_timedelta(td_series):
    """Convert timedelta to readable format '00 hours and 00 minutes' """
    data = td_series.iloc[0]
    total_seconds = data.total_seconds()
    hours = int((total_seconds // 3600))
    minutes = int((total_seconds % 3600) // 60)
    formatted = f"{hours} hours and {minutes:02d} minutes"
    res = td_series.copy()
    res.iloc[0] = formatted
    return res

def create_gauge(value, title_text="Fear & Greed Index"):
    """
    Create a gauge with smooth gradient
    """
    # Create smooth gradient by adding many small steps
    steps = []
    for i in range(100):
        # Calculate color based on position (red -> yellow -> green)
        if i <= 50:
            # Red to Yellow
            r = 255
            g = int(255 * (i / 50))
            b = 0
        else:
            # Yellow to Green
            r = int(255 * (1 - (i - 50) / 50))
            g = 255
            b = 0
        color = f'rgb({r}, {g}, {b})'
        steps.append({'range': [i, i+1], 'color': color})
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title={'text': title_text, 'font': {'size': 15}},
        number = {'font': {'size': 18, 'color':  'black'},
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
        shapes = [
            {
                'type': 'rect',
                'xref': 'paper',
                'yref': 'paper',
                'x0': 0,
                'y0': 0,
                'x1': 1,
                'y1': 1,
                'line': {
                    'color': 'white',
                    'width': 2,
                }
            }
        ],
        title={
            'text': title_text,
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 15}
        },
        height=150,
        margin=dict(l=20, r=20, t=55, b=20),
        paper_bgcolor='dark blue',
        font={'family': 'Arial'}
    )
    return fig


def get_fear_greed_color(value):
    """
    Returns color based on Fear & Greed Index value.
    """
    if value <= 25:
        return "#FF0000"  # Extreme Fear - Red
    elif value <= 45:
        return "#FF8C00"  # Fear - Orange
    elif value <= 55:
        return "#FFD700"  # Neutral - Yellow
    elif value <= 75:
        return "#90EE90"  # Greed - Light Green
    else:
        return "#00FF00"  # Extreme Greed - Green