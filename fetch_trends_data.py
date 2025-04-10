
import pandas as pd
import json
import time
from pytrends.request import TrendReq

# Load company data
df = pd.read_csv("cleaned_company_data_with_formatted_descriptions.csv")
df['Market Cap'] = df['Market Cap'].replace('[\$,]', '', regex=True).astype(float)

# Group by sector and select top 5 by market cap
sectors = sorted(df['Sectors'].unique())
pytrends = TrendReq(hl='en-US', tz=360)

all_data = {}

for sector in sectors:
    top5 = (
        df[df['Sectors'] == sector]
        .sort_values('Market Cap', ascending=False)
        .head(5)
    )
    companies = top5['Company Name'].tolist()
    try:
        pytrends.build_payload(companies, timeframe='today 12-m', geo='')
        interest = pytrends.interest_over_time()
        if not interest.empty:
            all_data[sector] = {
                company: interest[company].dropna().tolist()
                for company in companies
                if company in interest.columns
            }
            all_data[sector]["dates"] = interest.index.strftime('%Y-%m-%d').tolist()
    except Exception as e:
        print(f"Failed to fetch for {sector}: {e}")
    time.sleep(2)  # delay to avoid rate-limiting

# Save to JSON
with open("preloaded_trends.json", "w") as f:
    json.dump(all_data, f)
print("✅ Saved to preloaded_trends.json")
