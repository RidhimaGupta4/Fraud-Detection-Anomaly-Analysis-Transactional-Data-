import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)

N = 100000

segments = ['Regular', 'Premium', 'New', 'High-Risk']
seg_weights = [0.55, 0.20, 0.15, 0.10]

start_date = datetime(2023, 1, 1)
end_date = datetime(2024, 12, 31)
date_range = (end_date - start_date).days

transaction_ids = [f"TXN{str(i).zfill(7)}" for i in range(1, N+1)]
customer_ids = [f"CUST{str(np.random.randint(1, 8000)).zfill(5)}" for _ in range(N)]
customer_segments = np.random.choice(segments, size=N, p=seg_weights)

hour_p = [0.01,0.005,0.003,0.003,0.004,0.012,0.032,0.052,
          0.072,0.082,0.072,0.062,0.072,0.072,0.062,0.062,
          0.062,0.057,0.052,0.047,0.042,0.032,0.022,0.012]
hour_p = [x/sum(hour_p) for x in hour_p]

hours = np.random.choice(range(24), size=N, p=hour_p)
days_offset = np.random.randint(0, date_range, size=N)
timestamps = [start_date + timedelta(days=int(d), hours=int(h), minutes=random.randint(0,59)) for d, h in zip(days_offset, hours)]

categories = ['Electronics', 'Clothing', 'Groceries', 'Fuel', 'Restaurants',
              'Travel', 'Healthcare', 'Entertainment', 'Online Retail', 'Jewellery']
cat_weights = [0.12, 0.13, 0.18, 0.10, 0.12, 0.08, 0.07, 0.08, 0.09, 0.03]
transaction_categories = np.random.choice(categories, size=N, p=cat_weights)

channels = ['In-Store', 'Online', 'Mobile App', 'ATM', 'Phone']
chan_weights = [0.35, 0.30, 0.20, 0.10, 0.05]
transaction_channels = np.random.choice(channels, size=N, p=chan_weights)

cat_amount_params = {
    'Electronics': (450, 0.7), 'Clothing': (85, 0.6), 'Groceries': (65, 0.5),
    'Fuel': (55, 0.4), 'Restaurants': (40, 0.5), 'Travel': (380, 0.7),
    'Healthcare': (120, 0.6), 'Entertainment': (60, 0.5), 'Online Retail': (95, 0.6),
    'Jewellery': (800, 0.8)
}
amounts = []
for cat in transaction_categories:
    mu, sigma = cat_amount_params[cat]
    amounts.append(max(1.0, round(np.random.lognormal(np.log(mu), sigma), 2)))
amounts = np.array(amounts)

cities = ['London', 'Manchester', 'Birmingham', 'Edinburgh', 'Glasgow',
          'Leeds', 'Bristol', 'Liverpool', 'Sheffield', 'Newcastle']
city_weights = [0.28, 0.12, 0.10, 0.08, 0.07, 0.08, 0.07, 0.07, 0.07, 0.06]
locations = np.random.choice(cities, size=N, p=city_weights)

payment_methods_list = ['Credit Card', 'Debit Card', 'Digital Wallet', 'Cash', 'Bank Transfer']
pm_weights = [0.35, 0.30, 0.20, 0.10, 0.05]
payment_methods_col = np.random.choice(payment_methods_list, size=N, p=pm_weights)

merchant_ids = [f"MERCH{str(np.random.randint(1, 2000)).zfill(4)}" for _ in range(N)]

fraud_flags = np.zeros(N, dtype=int)
fraud_types = [''] * N
risk_scores = np.random.uniform(0, 30, size=N)

large_idx = np.random.choice(N, size=2000, replace=False)
amounts[large_idx] *= np.random.uniform(5, 20, size=2000)
for i in large_idx:
    fraud_flags[i] = 1
    fraud_types[i] = 'Large Amount Anomaly'
    risk_scores[i] = np.random.uniform(75, 100)

off_hours_pool = [i for i in range(N) if hours[i] in [0,1,2,3,4] and fraud_flags[i]==0]
off_hours_idx = np.random.choice(off_hours_pool, size=min(3000, len(off_hours_pool)), replace=False)
for i in off_hours_idx:
    fraud_flags[i] = 1
    fraud_types[i] = 'Off-Hours Transaction'
    risk_scores[i] = np.random.uniform(60, 85)

cust_list = list(set(customer_ids))
rapid_custs = np.random.choice(cust_list, size=400, replace=False)
rapid_set = set(rapid_custs)
rapid_pool = [i for i, c in enumerate(customer_ids) if c in rapid_set and fraud_flags[i]==0]
rapid_idx = np.random.choice(rapid_pool, size=min(2500, len(rapid_pool)), replace=False)
for i in rapid_idx:
    fraud_flags[i] = 1
    fraud_types[i] = 'Velocity Fraud'
    risk_scores[i] = np.random.uniform(65, 90)

hr_pool = [i for i in range(N) if customer_segments[i]=='High-Risk' and fraud_flags[i]==0]
hr_selected = np.random.choice(hr_pool, size=min(3000, len(hr_pool)), replace=False)
for i in hr_selected:
    fraud_flags[i] = 1
    fraud_types[i] = 'High-Risk Segment'
    risk_scores[i] = np.random.uniform(55, 80)

cat_chan_pool = [i for i in range(N) if transaction_categories[i] in ['Jewellery','Electronics']
                and transaction_channels[i] == 'Online' and hours[i] in [1,2,3,23] and fraud_flags[i]==0]
if len(cat_chan_pool) > 0:
    cc_selected = np.random.choice(cat_chan_pool, size=min(2000, len(cat_chan_pool)), replace=False)
    for i in cc_selected:
        fraud_flags[i] = 1
        fraud_types[i] = 'Suspicious Channel-Category'
        risk_scores[i] = np.random.uniform(60, 85)

round_pool = [i for i in range(N) if round(amounts[i]) % 100 == 0 and amounts[i] >= 500 and fraud_flags[i]==0]
if len(round_pool) > 0:
    round_selected = np.random.choice(round_pool, size=min(1500, len(round_pool)), replace=False)
    for i in round_selected:
        fraud_flags[i] = 1
        fraud_types[i] = 'Structuring Pattern'
        risk_scores[i] = np.random.uniform(50, 75)

risk_scores = np.clip(risk_scores, 0, 100)

risk_tiers = []
for s in risk_scores:
    if s >= 75: risk_tiers.append('Critical')
    elif s >= 55: risk_tiers.append('High')
    elif s >= 35: risk_tiers.append('Medium')
    else: risk_tiers.append('Low')

df = pd.DataFrame({
    'transaction_id': transaction_ids,
    'customer_id': customer_ids,
    'customer_segment': customer_segments,
    'timestamp': timestamps,
    'hour': hours,
    'day_of_week': [t.strftime('%A') for t in timestamps],
    'month': [t.strftime('%B') for t in timestamps],
    'amount': np.round(amounts, 2),
    'category': transaction_categories,
    'channel': transaction_channels,
    'payment_method': payment_methods_col,
    'location': locations,
    'merchant_id': merchant_ids,
    'fraud_flag': fraud_flags,
    'fraud_type': fraud_types,
    'risk_score': np.round(risk_scores, 2),
    'risk_tier': risk_tiers
})

df.to_csv('fraud_transactions.csv', index=False)
print(f"Dataset: {len(df):,} records")
print(f"Fraud rate: {df['fraud_flag'].mean()*100:.1f}%")
print(df[df['fraud_flag']==1]['fraud_type'].value_counts())
print(f"\nRisk tiers:\n{df['risk_tier'].value_counts()}")
flagged = len(df[df['risk_tier'].isin(['High','Critical'])])
print(f"High+Critical flagged: {flagged:,} ({flagged/N*100:.1f}%)")
