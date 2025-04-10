
import streamlit as st
import pandas as pd
from pytrends.request import TrendReq
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("📈 Google Trends Dashboard")
st.caption("Last 12 months · Global · Top 5 Companies per Sector by Market Cap")

@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_company_data_with_formatted_descriptions.csv")
    df['Market Cap'] = df['Market Cap'].replace('[\$,]', '', regex=True).astype(float)
    return df

@st.cache_data
def fetch_trends(companies, timeframe='today 12-m', geo=''):
    pytrends = TrendReq(hl='en-US', tz=360)
    pytrends.build_payload(companies, timeframe=timeframe, geo=geo)
    df_trends = pytrends.interest_over_time()
    if 'isPartial' in df_trends.columns:
        df_trends = df_trends.drop(columns=['isPartial'])
    return df_trends

df = load_data()
sectors = sorted(df['Sectors'].unique())

for sector in sectors:
    top5 = (
        df[df['Sectors'] == sector]
        .sort_values('Market Cap', ascending=False)
        .head(5)
    )
    companies = top5['Company Name'].tolist()
    
    with st.expander(f"📊 {sector} – Top 5 Companies by Market Cap", expanded=True):
        with st.spinner(f"Loading Google Trends for {sector}..."):
            try:
                trends = fetch_trends(companies)
                fig = go.Figure()
                for company in companies:
                    fig.add_trace(go.Scatter(
                        x=trends.index, y=trends[company],
                        mode='lines', name=company
                    ))
                fig.update_layout(
                    height=400,
                    margin=dict(t=10, b=10),
                    xaxis_title="Date",
                    yaxis_title="Search Interest (0–100)",
                )
                st.plotly_chart(fig, use_container_width=True)

                for company in companies:
                    desc = top5[top5['Company Name'] == company]['Formatted Description'].values[0]
                    st.markdown(desc)

            except Exception as e:
                st.error(f"Failed to load data for {sector}: {e}")
