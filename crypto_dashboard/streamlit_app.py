import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from fear_greed_index import get_index
from constants import FEAR_GREED_INDEX_URL
URL = FEAR_GREED_INDEX_URL
from functions import create_gauge
from stockmarket import get_raw_stockmarket_data, get_yearly_stockmarket_trend
from stockmarket import get_montly_stockmarket_trend, get_yearly_stockmarket_data_for_dashboard
from inflation import get_cpi, get_inflation

def main():
    # Page configuration
    st.set_page_config(
        page_title="Dashboard to Verify the crypto Fear & Greed index",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Title and description
    st.title("📈 Dashboard to Verify the crypto Fear & Greed index")
    st.markdown("""
    The Fear & Greed Index is a sentiment indicator that measures crypto market emotions on a scale of 0-100.
    - **0-25**: Extreme Fear (Red) 😰
    - **26-45**: Fear (Orange) 😟
    - **46-55**: Neutral (Yellow) 😐
    - **56-75**: Greed (Light Green) 😊
    - **76-100**: Extreme Greed (Green) 🤑
    """)

    # Sidebar controls
    st.sidebar.header("⚙️ What do you want to do with crypto?")
    
    # Data limit selector
    data_choice = st.sidebar.selectbox(
        label = 'Choose an option:',
        options=['I want to buy crypto', 'I want to sell crypto']
    )

    # Auto-refresh option
    auto_refresh = st.sidebar.checkbox("Auto-refresh (every 5 minutes)", value=False)
    
    if auto_refresh:
        st.sidebar.info("Data will refresh automatically every 5 minutes")

    # Fetch data
    with st.spinner("Fetching Fear & Greed Index data..."):
        df = get_index(URL, limit=360, format="json")

    if df is None or df.empty:
        st.error("❌ Unable to fetch data. Please try again later.")
        return

    # Current index value
    current_value = df.iloc[0]['value']
    current_classification = df.iloc[0]['value_classification']
    current_date = df.iloc[0]['date'].strftime('%Y-%m-%d')
    
    # Main metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Crypto Fear & Greed Index Today",
            value=f"{current_value}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="Classification",
            value=current_classification,
            delta=None
        )
    
    with col3:
        st.metric(
            label="Last Updated",
            value=current_date,
            delta=None
        )

    # Gauge chart for current value
    st.subheader("📊 Current Fear & Greed Level")
    
    fig_gauge = create_gauge(current_value)
    st.plotly_chart(fig_gauge, use_container_width=True)

    # Historical trend
    st.subheader("📈 Historical Trend")
    
    # Line chart
    fig_line = px.line(
        df,
        x='date', 
        y='value',
        title=f"Fear & Greed Index - Last 360 Days",
        labels={'date': 'Date', 'value': 'Index Value'},
        color_discrete_sequence=['#1f77b4']
    )
    
    # Add horizontal lines for different zones
    fig_line.add_hline(y=25, line_dash="dash", line_color="red", annotation_text="Extreme Fear")
    fig_line.add_hline(y=45, line_dash="dash", line_color="orange", annotation_text="Fear")
    fig_line.add_hline(y=55, line_dash="dash", line_color="yellow", annotation_text="Neutral")
    fig_line.add_hline(y=75, line_dash="dash", line_color="lightgreen", annotation_text="Greed")
    # TODO: добавить "Extreme Greed"
    
    fig_line.update_layout(
        height=500,
        xaxis_title="Date",
        yaxis_title="Index Value (0-100)",
        yaxis=dict(range=[0, 100])
    )
    
    st.plotly_chart(fig_line, use_container_width=True)

    # Stockmarket
    raw_sm = get_raw_stockmarket_data()
    sm = get_yearly_stockmarket_data_for_dashboard(raw_sm)
    curr_sm = sm.iloc[-1]['stockmarket_value']
    monthly_sm = get_montly_stockmarket_trend(raw_sm)
    yearly_sm = get_yearly_stockmarket_trend(raw_sm)

    #calculate montly rise / fall:
    
    monthly_change = (
        (sm.iloc[-1]['stockmarket_value'] - sm.iloc[-25]['stockmarket_value'])
        / sm.iloc[-25]['stockmarket_value']
        ) * 100
    
    #calculate yearly rise / fall:
    yearly_change = (
        (sm.iloc[-1]['stockmarket_value'] - sm.iloc[0]['stockmarket_value'])
        / sm.iloc[0]['stockmarket_value']
        ) * 100

    st.header("👩‍💼 Stock market")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric('Current stock market value', f'{curr_sm:.2f}')
    
    with col2:
        monthly_trend_value = monthly_sm.iloc[0]['stockmarket']
        monthly_direction = 'normal' if monthly_trend_value == 'Rising' else 'inverse' if monthly_trend_value == 'Falling' else 'off'
        
        st.metric(
            label = 'Monthly stock market trend',
            value=monthly_trend_value,
            delta = f"{monthly_change:.2f}%",
            delta_color=monthly_direction)

    with col3:
        yearly_trend_value = yearly_sm.iloc[0]['stockmarket']
        yearly_direction = 'normal' if monthly_trend_value == 'Rising' else 'inverse' if monthly_trend_value == 'Falling' else 'off'
        
        st.metric(
            label = 'Yearly stock market trend',
            value=yearly_trend_value,
            delta = f"{yearly_change:.2f}%",
            delta_color=yearly_direction)

    #Stockmarket long-term trend
    st.subheader('Stock market value distribution')
    st.area_chart(sm.set_index('date')['stockmarket_value'])

    #Inflation
    cpi = get_cpi()
    inflation = get_inflation(cpi)
    current_inflation = inflation.iloc[0]['current_inflation']
    inflation_growth = inflation.iloc[0]['inflation_growth']
    inflation_estimate = inflation.iloc[0]['inflation_estimate']

    st.header("💸 Inflation")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label='Current Inflation', value = f"{current_inflation}%")
    
    with col2:
        st.metric(label='Inflation growth', value = f"{inflation_growth}%")

    with col3:
        st.metric(label='Inflation estimate', value = f"{inflation_estimate}")


if __name__ == "__main__":
    main()