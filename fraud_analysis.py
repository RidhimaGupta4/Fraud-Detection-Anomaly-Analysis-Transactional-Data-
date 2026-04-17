"""
Fraud Detection & Anomaly Analysis
====================================
100,000 retail transaction simulation | Jan 2023 - Dec 2024
Techniques: Rule-based detection, statistical anomaly scoring, risk segmentation
"""

import pandas as pd
import numpy as np

df = pd.read_csv('fraud_transactions.csv')

print("=" * 60)
print("FRAUD DETECTION & ANOMALY ANALYSIS")
print("=" * 60)

# ─── 1. DATASET OVERVIEW ───────────────────────────────────────
print("\n[1] DATASET OVERVIEW")
print(f"  Total transactions:     {len(df):>10,}")
print(f"  Date range:             Jan 2023 – Dec 2024")
print(f"  Unique customers:       {df['customer_id'].nunique():>10,}")
print(f"  Unique merchants:       {df['merchant_id'].nunique():>10,}")
print(f"  Total revenue:          £{df['amount'].sum():>12,.2f}")
print(f"  Avg transaction:        £{df['amount'].mean():>10,.2f}")

# ─── 2. RULE-BASED DETECTION LOGIC ────────────────────────────
print("\n[2] RULE-BASED DETECTION RULES")

rules = {
    "R1 – Off-hours (00:00–04:59)":  (df['hour'] < 5) & (df['fraud_flag'] == 1),
    "R2 – Large amount (>£2,000)":   (df['amount'] > 2000) & (df['fraud_flag'] == 1),
    "R3 – High-Risk segment":        (df['customer_segment'] == 'High-Risk') & (df['fraud_flag'] == 1),
    "R4 – Online Jewellery/Electr.": (df['channel'] == 'Online') & (df['category'].isin(['Jewellery','Electronics'])) & (df['fraud_flag'] == 1),
    "R5 – Risk score ≥ 75 (Crit.)":  df['risk_score'] >= 75,
}
for rule, mask in rules.items():
    hit = mask.sum()
    print(f"  {rule}: {hit:,} flagged")

# ─── 3. STATISTICAL ANALYSIS ──────────────────────────────────
print("\n[3] STATISTICAL ANOMALY THRESHOLDS")
fraud_df = df[df['fraud_flag'] == 1]
clean_df = df[df['fraud_flag'] == 0]

amount_mean = clean_df['amount'].mean()
amount_std  = clean_df['amount'].std()
z_threshold = 3

print(f"  Clean txn mean:   £{amount_mean:.2f}")
print(f"  Clean txn std:    £{amount_std:.2f}")
print(f"  3-sigma threshold: £{amount_mean + z_threshold*amount_std:.2f}")
high_z = df[df['amount'] > amount_mean + z_threshold*amount_std]
print(f"  Txns beyond 3σ:   {len(high_z):,} ({len(high_z)/len(df)*100:.1f}%)")

print(f"\n  Avg risk score – Fraud:  {fraud_df['risk_score'].mean():.2f}")
print(f"  Avg risk score – Clean:  {clean_df['risk_score'].mean():.2f}")
print(f"  Separation ratio:        {fraud_df['risk_score'].mean()/clean_df['risk_score'].mean():.1f}×")

# ─── 4. FRAUD BY TYPE ─────────────────────────────────────────
print("\n[4] FRAUD PATTERN BREAKDOWN")
for ftype, cnt in fraud_df['fraud_type'].value_counts().items():
    pct = cnt / len(fraud_df) * 100
    print(f"  {ftype:<35} {cnt:>5,}  ({pct:.1f}%)")

# ─── 5. RISK SEGMENTATION ─────────────────────────────────────
print("\n[5] RISK TIER DISTRIBUTION")
for tier in ['Critical','High','Medium','Low']:
    cnt = len(df[df['risk_tier'] == tier])
    pct = cnt / len(df) * 100
    print(f"  {tier:<10} {cnt:>7,}  ({pct:.1f}%)")

# ─── 6. SEGMENT ANALYSIS ──────────────────────────────────────
print("\n[6] CUSTOMER SEGMENT RISK RATES")
seg = df.groupby('customer_segment').agg(
    total=('fraud_flag','count'),
    fraud=('fraud_flag','sum'),
    avg_risk=('risk_score','mean')
).reset_index()
seg['fraud_rate'] = (seg['fraud']/seg['total']*100).round(2)
seg = seg.sort_values('fraud_rate', ascending=False)
for _, r in seg.iterrows():
    print(f"  {r['customer_segment']:<12} {r['fraud_rate']:>6.1f}% fraud rate | avg risk: {r['avg_risk']:.1f}")

# ─── 7. AMOUNT BAND THRESHOLDS ────────────────────────────────
print("\n[7] FRAUD RATE BY AMOUNT BAND (threshold logic)")
bins   = [0,50,100,250,500,1000,5000,float('inf')]
labels = ['<£50','£50-100','£100-250','£250-500','£500-1K','£1K-5K','>£5K']
df['band'] = pd.cut(df['amount'], bins=bins, labels=labels)
band_stats = df.groupby('band', observed=True).agg(
    total=('fraud_flag','count'), fraud=('fraud_flag','sum')).reset_index()
band_stats['rate'] = (band_stats['fraud']/band_stats['total']*100).round(2)
for _, r in band_stats.iterrows():
    flag = " ← AUTO-BLOCK THRESHOLD" if r['rate'] > 50 else (" ← REVIEW QUEUE" if r['rate'] > 20 else "")
    print(f"  {str(r['band']):<12} {r['rate']:>6.1f}% fraud rate{flag}")

# ─── 8. CITY EXPOSURE ─────────────────────────────────────────
print("\n[8] GEOGRAPHIC RISK EXPOSURE (top 5 cities)")
city = df.groupby('location').agg(
    total=('fraud_flag','count'),
    fraud=('fraud_flag','sum'),
    exposure=('amount', lambda x: x[df.loc[x.index,'fraud_flag']==1].sum())
).reset_index()
city['rate'] = (city['fraud']/city['total']*100).round(2)
city = city.sort_values('fraud', ascending=False).head(5)
for _, r in city.iterrows():
    print(f"  {r['location']:<12} {r['fraud']:>5,} flagged | {r['rate']:.2f}% rate | £{r['exposure']:,.0f} exposed")

# ─── 9. ACTIONABLE THRESHOLDS ─────────────────────────────────
print("\n[9] RECOMMENDED LOSS PREVENTION THRESHOLDS")
print("  AUTO-BLOCK:   risk_score ≥ 90  OR  amount > £5,000  OR  hour in [0-4]")
print("  MANUAL REVIEW: risk_score 55–89  OR  segment = 'High-Risk'  OR  amount > £1,000")
print("  MONITOR:      risk_score 35–54  OR  velocity flag  OR  channel = 'Phone'")
print("  PASS:         risk_score < 35  AND  no rule triggers")

print("\n[10] REVENUE IMPACT SUMMARY")
at_risk = df[df['risk_tier'].isin(['Critical','High'])]['amount'].sum()
print(f"  High+Critical exposure:  £{at_risk:>12,.2f}")
print(f"  % of total revenue:       {at_risk/df['amount'].sum()*100:.1f}%")
print(f"  Avg exposure per flagged: £{at_risk/len(df[df['risk_tier'].isin(['Critical','High'])]):,.2f}")

print("\n" + "=" * 60)
print("Analysis complete. Dataset: fraud_transactions.csv")
print("=" * 60)
