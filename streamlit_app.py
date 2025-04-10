
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

view_mode = st.radio("View Mode", ["Top 5 by Sector", "Search by Company"], horizontal=True)

display_mode = st.radio("Display Mode", ["% Change vs. 12 Months Ago", "Absolute Search Interest"], horizontal=True)

if view_mode == "Top 5 by Sector":
    for sector in sectors:
        if sector not in trends_data:
            continue
        sector_data = trends_data[sector]
        dates = sector_data["dates"]
        company_names = [c for c in sector_data if c != "dates"]

        top5 = df[(df['Sectors'] == sector) & (df['Company Name'].isin(company_names))]

        with st.expander(f"📊 {sector} – Top 5 Companies by Market Cap", expanded=False):
            fig = go.Figure()
            for company in company_names:
                values = sector_data[company]
                if display_mode == "% Change vs. 12 Months Ago" and len(values) > 1:
                    start = values[0] or 1e-6
                    values = [(v - start) / start * 100 if start else 0 for v in values]
                fig.add_trace(go.Scatter(
                    x=dates, y=values,
                    mode='lines', name=company
                ))
            fig.update_layout(
                height=400,
                margin=dict(t=10, b=10),
                xaxis_title="Date",
                yaxis_title="% Change" if display_mode.startswith("%") else "Search Interest (0–100)",
            )
            st.plotly_chart(fig, use_container_width=True)

            for company in company_names:
                desc = top5[top5['Company Name'] == company]['Formatted Description'].values[0]
                st.markdown(desc)

else:
    company_list = df['Company Name'].unique()
    search_input = st.text_input("Search for a Company")
    matches = [c for c in company_list if search_input.lower() in c.lower()]

    if matches:
        company = st.selectbox("Matching Companies", matches)
        sector = df[df['Company Name'] == company]['Sectors'].values[0]
        description = df[df['Company Name'] == company]['Formatted Description'].values[0]

        # Try to find the data in the trends JSON
        trends = trends_data.get(sector, {})
        if company in trends:
            values = trends[company]
            dates = trends["dates"]
            if display_mode == "% Change vs. 12 Months Ago" and len(values) > 1:
                base = values[0] or 1e-6
                values = [(v - base) / base * 100 if base else 0 for v in values]

            st.subheader(f"{company} ({sector})")
            st.markdown(description)
            st.line_chart(pd.DataFrame({company: values}, index=pd.to_datetime(dates)))
        else:
            st.warning("No trend data available for this company.")
    else:
        if search_input:
            st.warning("No matches found.")
