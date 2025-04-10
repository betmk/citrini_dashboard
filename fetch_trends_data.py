
import pandas as pd
import json
import time
from pytrends.request import TrendReq

# Load data
df = pd.read_csv("cleaned_company_data_with_formatted_descriptions.csv")
df['Market Cap'] = df['Market Cap'].replace('[\$,]', '', regex=True).astype(float)

# Initialize Pytrends
pytrends = TrendReq(hl='en-US', tz=360)
sectors = sorted(df['Sectors'].unique())
all_data = {}

# Pull data
for sector in sectors:
    top_companies = (
        df[df['Sectors'] == sector]
        .sort_values('Market Cap', ascending=False)
        .head(5)
    )
    companies = top_companies['Company Name'].tolist()

    try:
        pytrends.build_payload(companies[:4], timeframe='today 12-m', geo='')
        interest = pytrends.interest_over_time()

        if not interest.empty:
            all_data[sector] = {
                company: interest[company].dropna().tolist()
                for company in companies if company in interest.columns
            }
            all_data[sector]["dates"] = interest.index.strftime('%Y-%m-%d').tolist()
        else:
            print(f"No data returned for {sector}")

    except Exception as e:
        print(f"Failed to fetch for {sector}: {e}")

    time.sleep(2)

if not all_data:
    print("❌ No data fetched. Exiting.")
    exit()

# Save to file
with open("preloaded_trends.json", "w") as f:
    json.dump(all_data, f)

print("✅ Saved preloaded_trends.json")
