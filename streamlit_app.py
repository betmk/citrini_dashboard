
import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("📈 Google Trends Dashboard")
st.caption("Preloaded · Last 12 months · Global · Top 5 Companies per Sector by Market Cap")

@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_company_data_with_formatted_descriptions.csv")
    df['Market Cap'] = df['Market Cap'].replace('[\$,]', '', regex=True).astype(float)
    return df

@st.cache_data
def load_trends():
    with open("preloaded_trends.json", "r") as f:
        return json.load(f)

df = load_data()
trends_data = load_trends()
sectors = sorted(df['Sectors'].unique())

for sector in sectors:
    if sector not in trends_data:
        continue
    sector_data = trends_data[sector]
    dates = sector_data["dates"]
    company_names = [c for c in sector_data if c != "dates"]

    top5 = df[(df['Sectors'] == sector) & (df['Company Name'].isin(company_names))]

    with st.expander(f"📊 {sector} – Top 5 Companies by Market Cap", expanded=True):
        fig = go.Figure()
        for company in company_names:
            fig.add_trace(go.Scatter(
                x=dates, y=sector_data[company],
                mode='lines', name=company
            ))
        fig.update_layout(
            height=400,
            margin=dict(t=10, b=10),
            xaxis_title="Date",
            yaxis_title="Search Interest (0–100)",
        )
        st.plotly_chart(fig, use_container_width=True)

        for company in company_names:
            desc = top5[top5['Company Name'] == company]['Formatted Description'].values[0]
            st.markdown(desc)
