import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from fear_greed_index import get_index_data
from constants import FEAR_GREED_INDEX_URL

URL = FEAR_GREED_INDEX_URL


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

def main():
    # Page configuration
    st.set_page_config(
        page_title="Crypto Fear & Greed Index Dashboard",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Title and description
    st.title("📈 Crypto Fear & Greed Index Dashboard")
    st.markdown("""
    The Fear & Greed Index is a sentiment indicator that measures crypto market emotions on a scale of 0-100.
    - **0-25**: Extreme Fear (Red) 😰
    - **26-45**: Fear (Orange) 😟
    - **46-55**: Neutral (Yellow) 😐
    - **56-75**: Greed (Light Green) 😊
    - **76-100**: Extreme Greed (Green) 🤑
    """)

    # Sidebar controls
    st.sidebar.header("⚙️ Controls")
    
    # Data limit selector
    data_limit = st.sidebar.selectbox(
        "Select data range:",
        options=[7, 30, 60, 100, 200],
        index=2,
        help="Number of days of historical data to fetch"
    )

    # Auto-refresh option
    auto_refresh = st.sidebar.checkbox("Auto-refresh (every 5 minutes)", value=False)
    
    if auto_refresh:
        st.sidebar.info("Data will refresh automatically every 5 minutes")

    # Fetch data
    with st.spinner("Fetching Fear & Greed Index data..."):
        df = get_index_data(URL, limit=data_limit, format="json")

    if df is None or df.empty:
        st.error("❌ Unable to fetch data. Please try again later.")
        return

    # Current index value
    current_value = df.iloc[-1]['value']
    current_classification = df.iloc[-1]['value_classification']
    current_date = df.iloc[-1]['date'].strftime('%Y-%m-%d')
    
    # Main metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Current Index",
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
    
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = current_value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Fear & Greed Index"},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': get_fear_greed_color(current_value)},
            'steps': [
                {'range': [0, 25], 'color': "lightgray"},
                {'range': [25, 45], 'color': "gray"},
                {'range': [45, 55], 'color': "lightgray"},
                {'range': [55, 75], 'color': "gray"},
                {'range': [75, 100], 'color': "lightgray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig_gauge.update_layout(height=400)
    st.plotly_chart(fig_gauge, use_container_width=True)

    # Historical trend
    st.subheader("📈 Historical Trend")
    
    # Line chart
    fig_line = px.line(
        df, 
        x='date', 
        y='value',
        title=f"Fear & Greed Index - Last {data_limit} Days",
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

    # Distribution analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Value Distribution")
        fig_hist = px.histogram(
            df, 
            x='value', 
            nbins=20, 
            title="Distribution of Index Values",
            labels={'value': 'Index Value', 'count': 'Frequency'}
        )
        fig_hist.update_layout(height=400)
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        st.subheader("🏷️ Classification Breakdown")
        classification_counts = df['value_classification'].value_counts()
        fig_pie = px.pie(
            values=classification_counts.values,
            names=classification_counts.index,
            title="Distribution by Classification"
        )
        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, use_container_width=True)

    # Statistics
    st.subheader("📋 Statistical Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Average", f"{df['value'].mean():.1f}")
    
    with col2:
        st.metric("Median", f"{df['value'].median():.1f}")
    
    with col3:
        st.metric("Minimum", f"{df['value'].min():.1f}")
    
    with col4:
        st.metric("Maximum", f"{df['value'].max():.1f}")

    # Raw data table
    if st.expander("📋 View Raw Data"):
        st.dataframe(
            df.sort_values('date', ascending=False),
            use_container_width=True,
            hide_index=True
        )

    # Footer
    st.markdown("---")
    st.markdown(
        "📊 **Data Source**: [Alternative.me Crypto Fear & Greed Index](https://alternative.me/crypto/fear-and-greed-index/)"
    )

if __name__ == "__main__":
    main()