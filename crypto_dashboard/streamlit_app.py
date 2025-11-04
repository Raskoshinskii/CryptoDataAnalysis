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

def main():
    if "page" not in st.session_state:
        st.session_state.page = 'start'

    if st.session_state.page == "start":
        current_datetime = datetime.now()
        today = current_datetime.strftime("%B %d, %Y")
        st.subheader(f"Today, {today}")

        st.subheader("Crypto Fear & Greed Index is:")
        df = get_index(URL, limit=1, format="json")
        index = df.iloc[0]['value_classification']
        st.subheader(f"{index}")

        current_value = df.iloc[0]['value']
        fig_gauge = create_gauge(current_value)
        st.plotly_chart(fig_gauge, use_container_width=True)

        index_recommendation = get_index_recommendation(current_value)
        st.subheader(f"It tells you to {index_recommendation}")
        st.subheader("But should you? 🤔")

        st.markdown("""
        <style>
        div.stButton > button:first-child {
            animation: pulse 2s infinite;
            background-color: #FF4B4B;
            color: white;
            border: none;
            font-size: 20px;
            font-weight: bold;
            padding: 15px 30px;
            border-radius: 10px;
        }

        @keyframes pulse {
            0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(255, 75, 75, 0.7); }
            70% { transform: scale(1.05); box-shadow: 0 0 0 15px rgba(255, 75, 75, 0); }
            100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(255, 75, 75, 0); }
        }
        </style>
        """, unsafe_allow_html=True)

        if st.button("Verify F&G Index", key = 'verify_button'):
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
        traffic_lights(recommendation)
        st.markdown(f"{recommendation}")

        st.markdown("Because:")
        st.subheader(f"📈 F&G {lt_trend}")
                
        # Line chart
        df_fg_index = get_index(URL, timeout = 10, limit=30, format = 'json')
        fig_line = px.line(
            df_fg_index,
            x='date', 
            y='value',
            title=f"Fear & Greed Index - Last 30 Days",
            labels={'date': 'Date', 'value': 'Index Value'},
            color_discrete_sequence=["#1fb42b"]
        )
        
        # Add horizontal lines for different zones
        ap = 'top left'
        af = dict(size=16, family='Arial')
        fig_line.add_hline(y=25, line_dash="dash", line_color="red", annotation_text="Extreme Fear", annotation_position=ap, annotation_font=af)
        fig_line.add_hline(y=45, line_dash="dash", line_color="orange", annotation_text="Fear", annotation_position=ap, annotation_font=af)
        fig_line.add_hline(y=55, line_dash="dash", line_color="yellow", annotation_text="Neutral", annotation_position=ap, annotation_font=af)
        fig_line.add_hline(y=75, line_dash="dash", line_color="lightgreen", annotation_text="Greed", annotation_position=ap, annotation_font=af)
        fig_line.add_hline(y=100, line_dash="dash", line_color="green", annotation_text="Extreme Greed", annotation_position=ap, annotation_font=af)
       
        
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

        st.header("👩‍💼 Stock market")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric('Current stock market value', f'{curr_sm:.2f}')
            st.metric('Stock market value a month ago', f'{month_sm:.2f}')
            st.metric('Stock market value a month ago', f'{year_sm:.2f}')
        
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
        st.subheader('Stock market value distribution over the year')
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

        #Long-term inflatioin trend
        cpi = get_cpi()
        plot_cpi = cpi.copy()
        plot_cpi = plot_cpi[:-2]
        plot_cpi.sort_values(by = 'date', ascending=True, inplace=True)
        st.subheader("Inflation trend over the year")
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.barplot(data = plot_cpi, x = 'date_formatted', y = 'hist_inf_rate', ax=ax)
        plt.bar_label(ax.containers[0], fmt='%.1f%%')
        plt.ylabel('Monthly inflation rate')
        plt.xlabel('Date')
        plt.xticks(rotation = 45)
        plt.tight_layout()
        st.pyplot(fig)

if __name__ == "__main__":
    main()