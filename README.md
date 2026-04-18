# Fraud Detection & Anomaly Analysis

> Transactional data analysis across 100,000+ retail records to identify revenue leakage, flag high-risk behaviour, and support loss prevention strategy.

## Overview

This project simulates a real-world retail fraud detection pipeline. It generates a realistic transactional dataset, applies rule-based and statistical anomaly detection techniques, segments customers by risk profile, and visualises findings through an interactive dashboard.

**Live dashboard →** https://RidhimaGupta4.github.io/Fraud-Detection-Anomaly-Analysis-Transactional-Data-/

---

## Key findings

- **10,077 transactions flagged** (10.1% of volume) across 6 fraud pattern types
- **£6.81M revenue at risk** out of £25M total — 27.1% exposure
- Off-hours transactions (00:00–04:59) carry a **100% fraud rate** — strongest rule-based signal
- High-Risk segment customers flag at **37.4%** vs 7.1% for regular customers (5.3× higher)
- Transactions above **£5,000** have an 89.6% fraud rate → recommended auto-block threshold
- Risk scores separate fraudulent from clean transactions by a **5× margin** (75.2 vs 15.0 avg)

---

## Techniques used

| Category | Methods |
|---|---|
| Data simulation | Lognormal amount distributions, hour-weighted timestamps, injected fraud patterns |
| Rule-based detection | Off-hours threshold, amount ceiling, segment flag, channel-category correlation |
| Statistical anomaly | Z-score / 3-sigma outlier detection, risk scoring (0–100), tier segmentation |
| Risk segmentation | 4-tier classification: Critical / High / Medium / Low |
| Visualisation | Interactive HTML dashboard (Chart.js) — monthly trends, heatmaps, city exposure |

---

## Fraud patterns injected

| Pattern | Count | Detection method |
|---|---|---|
| High-Risk Segment | 3,000 | Customer segment rule |
| Velocity Fraud | 2,500 | Repeat-customer clustering |
| Off-Hours Transaction | 2,431 | Hour-of-day threshold (00:00–04:59) |
| Large Amount Anomaly | 2,000 | Magnitude multiplier + z-score |
| Structuring Pattern | 94 | Round-number detection |
| Suspicious Channel-Category | 52 | Cross-field correlation (online + jewellery/electronics at night) |

---

## Project structure
````markdown
```text
fraud-detection-analysis/
├── data/
│   └── fraud_transactions.csv       # 100,000-row dataset (17 columns)
├── src/
│   ├── generate_fraud_data.py       # Dataset generator
│   └── fraud_analysis.py            # Full analysis pipeline
├── dashboard/
│   └── index.html                   # Self-contained interactive dashboard
├── outputs/
│   └── fraud_analysis.json          # Pre-computed summary statistics
└── requirements.txt
```
````

## How to run

```bash
pip install -r requirements.txt
python src/generate_fraud_data.py   # regenerate dataset
python src/fraud_analysis.py        # run full analysis
```

## Dataset schema

| Column | Description |
|---|---|
| `transaction_id` | Unique ID (TXN0000001 format) |
| `customer_id` | Customer reference |
| `customer_segment` | Regular / Premium / New / High-Risk |
| `timestamp` | Datetime of transaction |
| `amount` | Transaction value (£) |
| `category` | Merchant category (10 types) |
| `channel` | In-Store / Online / Mobile App / ATM / Phone |
| `location` | UK city (10 cities) |
| `fraud_flag` | 1 = flagged, 0 = clean |
| `fraud_type` | Pattern label if flagged |
| `risk_score` | 0–100 continuous score |
| `risk_tier` | Critical / High / Medium / Low |

---

*Built with Python (pandas, numpy) · Dashboard: Chart.js · Hosted via GitHub Pages*
