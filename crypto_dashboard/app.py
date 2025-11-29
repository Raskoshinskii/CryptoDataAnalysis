import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

from fear_greed_index import get_index
from constants import FEAR_GREED_INDEX_URL
URL = FEAR_GREED_INDEX_URL
from functions import create_gauge, get_index_recommendation, traffic_lights, get_recommendation
from functions import get_index_trend
from stockmarket import get_raw_stockmarket_data, get_yearly_stockmarket_trend
from stockmarket import get_montly_stockmarket_trend, get_yearly_stockmarket_data_for_dashboard
from inflation import get_cpi, get_inflation

st.set_page_config(layout='wide')

def main() -> None:
    """
    Main Streamlit appliccation for crypto market analysis
    """
    st.markdown("""
    <style>
    /* Center all text in the app */
    .stApp {
        text-align: center;
    }
    
    /* Center headers and subheaders */
    h1, h2, h3, h4, h5, h6 {
        text-align: center !important;
    }
    
    /* Center metric containers */
    [data-testid="metric-container"] {
        text-align: center !important;
    }
    
    /* Center the button */
    .stButton > button {
        animation: pulse 2s infinite;
        background-color: #FF4B4B;
        color: white;
        border: none;
        font-size: 20px;
        font-weight: bold;
        padding: 15px 30px;
        border-radius: 10px;
        margin: 0 auto !important;
        display: block !important;
    }
    
    /* Center plotly charts */
    .js-plotly-plot {
        margin: 0 auto !important;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(255, 75, 75, 0.7); }
        70% { transform: scale(1.05); box-shadow: 0 0 0 15px rgba(255, 75, 75, 0); }
        100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(255, 75, 75, 0); }
    }
    
    /* Center column content */
    .stColumn {
        text-align: center;
    }
    
    /* Ensure all divs in columns are centered */
    .stColumn > div {
        text-align: center !important;
        justify-content: center !important;
    }
    </style>
    """, unsafe_allow_html=True)

    if "page" not in st.session_state:
        st.session_state.page = 'start'

    if st.session_state.page == "start":
        # Use wider middle column and apply centering to each element
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            # Apply centering to each element individually
            
            current_datetime = datetime.now()
            today = current_datetime.strftime("%B %d, %Y")
            st.subheader(f"Today is {today}")

            df = get_index(URL, limit=1, format="json")
            index = df.iloc[0]['value_classification']
            st.subheader("Crypto Fear & Greed Index is:")
            st.subheader(f"{index}")

            current_value = df.iloc[0]['value']
            fig_gauge = create_gauge(current_value)
            
            # Center the gauge chart with additional styling
            st.plotly_chart(fig_gauge, use_container_width=True)

            index_recommendation = get_index_recommendation(current_value)
            st.subheader(f"It tells investors to {index_recommendation}")
            st.subheader("But should you? 🤔")

            st.write("\n")
            st.write("\n")

            # Create a centered container for the button
            button_col1, button_col2, button_col3 = st.columns([1, 2, 1])
            with button_col2:
                if st.button("Verify Fear & Greed Index", key='verify_button', use_container_width=True):
                    st.session_state.page = "analysis"
                    st.rerun()

    elif st.session_state.page == "analysis":

        df_index = get_index(URL, limit=30, format="json")
        lt_trend = get_index_trend(df_index)

        raw_stockmarket = get_raw_stockmarket_data()
        df_stockmarket = get_montly_stockmarket_trend(raw_stockmarket)

        cpi = get_cpi()
        df_inflation = get_inflation(cpi)

        recommendation = get_recommendation(df_index, lt_trend, df_stockmarket, df_inflation)

        tcol1, tcol2, tcol3 = st.columns([6, 1, 6])
        with tcol2:
            traffic_lights(recommendation)

        rcol1, rcol2, rcol3 = st.columns([2, 1, 2])
        with rcol2:
            st.header(f"{recommendation}")
            st.subheader("Because:")
            st.header(":point_down:")


        #F&G Index:
        st.subheader(f"📈 F&G long-term trend: {lt_trend}")
                
        # Line chart
        df_fg_index = get_index(URL, timeout = 10, limit=30, format = 'json')
        fig_line = px.line(
            df_fg_index,
            x='date', 
            y='value',
            labels={'date': 'Date', 'value': 'F&G Index'},
            color_discrete_sequence=["#1fb42b"]
        )
        
        # Add horizontal lines for different zones
        ap = 'top left'
        af = dict(size=16, family='Arial')
        fig_line.add_hline(y=25,
                        line_dash="dash",
                        line_color="red",
                        annotation_text="Extreme Fear",
                        annotation_position=ap,
                        annotation_font=af)
        fig_line.add_hline(y=45,
                        line_dash="dash",
                        line_color="orange",
                        annotation_text="Fear",
                        annotation_position=ap,
                        annotation_font=af)
        fig_line.add_hline(y=55,
                        line_dash="dash", 
                        line_color="yellow",
                        annotation_text="Neutral",
                        annotation_position=ap,
                        annotation_font=af)
        fig_line.add_hline(y=75,
                        line_dash="dash",
                        line_color="lightgreen",
                        annotation_text="Greed",
                        annotation_position=ap,
                        annotation_font=af)
        fig_line.add_hline(y=100,
                        line_dash="dash",
                        line_color="green",
                        annotation_text="Extreme Greed",
                        annotation_position=ap,
                        annotation_font=af)
        fig_line.update_layout(
            height=500,
            xaxis_title="Date",
            yaxis_title="Index Value (0-100)",
            yaxis=dict(range=[0, 100])
        )
        st.plotly_chart(fig_line, use_container_width=True)
        
        #col2 - Stockmarket
        raw_sm = get_raw_stockmarket_data()
        sm = get_yearly_stockmarket_data_for_dashboard(raw_sm)
        curr_sm = sm.iloc[-1]['stockmarket_value']
        monthly_sm = get_montly_stockmarket_trend(raw_sm)
        yearly_sm = get_yearly_stockmarket_trend(raw_sm)
        month_sm = sm.iloc[-25]['stockmarket_value']
        year_sm = sm.iloc[0]['stockmarket_value']

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

        monthly_trend_value = monthly_sm.iloc[0]['stockmarket']
        st.subheader(f"👩‍💼 Stock market: {monthly_trend_value}")

        st.markdown("""
        <style>
        div[data-testid='metric-container']{
                    text-align: center !important;
                    justify-content: center !important;
        }
        [data-testid='stMetricValue']{
                    font-size: 20px;
                    text-align: center !important;
                    justify-content: center !important;
                    align-items: center !important;
        }
        [data-testid='stMetricLabel']{
                    font-size: 16px;
                    text-align: center !important;
                    justify-content: center !important;
        }
        </style>
        """, unsafe_allow_html=True)
        cur_col = st.columns(1)[0]
        with cur_col:
            st.metric('Current S&P 500 value', f'{curr_sm:.2f}', border=True)

        scol1, scol2 = st.columns(2)
        
        with scol1:
            st.metric('S&P 500 a month ago', f'{month_sm:.2f}', border=True, height='stretch', width='stretch')
        with scol2:
            st.metric('S&P 500 a year ago', f'{year_sm:.2f}', border=True, height='stretch', width='stretch')

        sm1_col1, sm1_col2 = st.columns(2)

        with sm1_col1:
            monthly_trend_value = monthly_sm.iloc[0]['stockmarket']
            monthly_direction = 'normal' if monthly_trend_value == 'Rising' else 'inverse' if monthly_trend_value == 'Falling' else 'off'
        
            st.metric(
                label = 'Monthly trend',
                value=monthly_trend_value,
                delta = f"{monthly_change:.2f}%",
                delta_color=monthly_direction, border=True, height='stretch', width='stretch')
        
        with sm1_col2:
            yearly_trend_value = yearly_sm.iloc[0]['stockmarket']
            yearly_direction = 'normal' if monthly_trend_value == 'Rising' else 'inverse' if monthly_trend_value == 'Falling' else 'off'
        
            st.metric(
                label = 'Yearly trend',
                value=yearly_trend_value,
                delta = f"{yearly_change:.2f}%",
                delta_color=yearly_direction, border=True, height='stretch', width='stretch')
            
        #Stockmarket long-term trend
        st.area_chart(sm.set_index('date')['stockmarket_value'])
        
    
        #Inflation
        cpi = get_cpi()
        inflation = get_inflation(cpi)
        current_inflation = inflation.iloc[0]['current_inflation']
        inflation_growth = inflation.iloc[0]['inflation_growth']
        inflation_estimate = inflation.iloc[0]['inflation_estimate']
        
        st.subheader(f"💸 Inflation: {inflation_estimate}")
        inf_col1, inf_col2, inf_col3 = st.columns(3)
        with inf_col1:
            st.metric(label='Central Bank target', value=f"{2.0}%", border=True, height='stretch', width='stretch')
        with inf_col2:
            st.metric(label='Current', value = f"{current_inflation}%", border=True, height='stretch', width='stretch')
        with inf_col3:
            st.metric(label='Growth', value = f"{inflation_growth}%", border=True, height='stretch', width='stretch')

        #Long-term inflatioin trend
        cpi = get_cpi()
        plot_cpi = cpi.copy()
        plot_cpi = plot_cpi[:-2]
        plot_cpi.sort_values(by = 'date', ascending=True, inplace=True)
        
        fig = px.bar(
        plot_cpi, 
        x='date_formatted', 
        y='hist_inf_rate',
        labels={'hist_inf_rate': 'Monthly Inflation Rate (%)', 'date_formatted': 'Date'},
        color='hist_inf_rate',
        color_continuous_scale='RdYlGn_r')
        fig.update_traces(
        texttemplate='%{y:.1f}%',
        textposition='outside')
        fig.update_layout(
        xaxis_tickangle=-45,
        showlegend=False,
        height=500, width=None, autosize=True)
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()