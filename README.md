# 🍽️ Zomato Food Delivery — Funnel & Conversion Analysis

> A comprehensive product analytics project analyzing the food delivery conversion funnel, user retention, and key business metrics — built for a Product Analyst portfolio.

---

## 📋 Project Overview

This project simulates and analyzes **Zomato's food delivery funnel** — from app session to completed order — to identify conversion bottlenecks, revenue drivers, and actionable product improvements.

### Business Questions Answered
1. **What is the overall session-to-order conversion rate?** Where are the biggest drop-offs?
2. **How do user segments (New/Returning/Power) behave differently** in the funnel?
3. **What drives cart abandonment?** How does delivery fee impact checkout?
4. **When do users convert best?** Hourly and daily patterns.
5. **How well do we retain users?** Cohort-based reorder analysis.
6. **Which cuisines and cities drive the most revenue?**
7. **Does platform (Android/iOS/Web) impact conversion?**

---

## 🗂️ Project Structure

```
zomato-funnel-analysis/
│
├── README.md                    # Project documentation (this file)
├── requirements.txt             # Python dependencies
│
├── src/
│   ├── generate_data.py         # Synthetic data generator (10K users, 50K sessions)
│   └── funnel_analysis.py       # Full analysis with 10 visualizations
│
├── sql/
│   └── analysis_queries.sql     # 10 SQL queries for the same analysis
│
├── data/                        # Generated CSV datasets
│   ├── users.csv
│   ├── restaurants.csv
│   ├── sessions.csv
│   ├── searches.csv
│   ├── impressions.csv
│   ├── cart_events.csv
│   ├── orders.csv
│   └── funnel_events.csv
│
└── outputs/                     # Generated charts and reports
    ├── 01_overall_funnel.png
    ├── 02_segment_funnel.png
    ├── 03_cart_abandonment.png
    ├── 04_hourly_patterns.png
    ├── 05_cohort_retention.png
    ├── 06_delivery_fee_impact.png
    ├── 07_cuisine_analysis.png
    ├── 08_city_comparison.png
    ├── 09_platform_analysis.png
    ├── 10_revenue_trends.png
    └── summary_metrics.txt
```

---

## 🛠️ Tech Stack

| Tool | Usage |
|------|-------|
| **Python** | Core analysis language |
| **Pandas** | Data manipulation & aggregation |
| **NumPy** | Statistical computations |
| **Matplotlib + Seaborn** | Professional visualizations |
| **SQL** | Alternative query-based analysis |
| **SciPy** | Statistical testing |

---

## 🚀 How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate synthetic data (10K users, 50K sessions)
python src/generate_data.py

# 3. Run the full analysis (generates 10 charts)
python src/funnel_analysis.py
```

---

## 📊 Analyses & Key Findings

### 1. Overall Funnel
The conversion funnel from session to order, showing drop-off at each stage. The biggest drop-off occurs at the **Restaurant Click → Add to Cart** stage.

### 2. User Segment Analysis
Power users convert at **~2x** the rate of new users. New user conversion is the biggest growth lever.

### 3. Cart Abandonment
Cart abandonment rate is driven primarily by:
- **High delivery fees** (₹35+ fee → significant drop-off)
- **Price sensitivity** (changed mind / found better option)

### 4. Hourly Patterns
Peak conversion windows are **12–2 PM (Lunch)** and **7–10 PM (Dinner)**. Off-peak hours show significantly lower conversion.

### 5. Cohort Retention
Weekly cohort analysis reveals retention curves and identifies the critical first-week reorder behavior.

### 6. Delivery Fee Impact
Free delivery shows substantially higher checkout completion vs. ₹40+ delivery fee — a strong case for subsidized delivery on first orders.

### 7. Cuisine & City Performance
Revenue concentration across cuisines and cities, with bubble charts showing the AOV-Rating relationship.

---

## 💡 Product Recommendations

Based on the analysis, the top product interventions recommended:

| # | Recommendation | Expected Impact | Priority |
|---|---------------|----------------|----------|
| 1 | **Reduce delivery fee visibility shock** — show total price earlier | +8% checkout conversion | P0 |
| 2 | **Free delivery on first 3 orders** for new users | +15% new user conversion | P0 |
| 3 | **Push notifications during lunch/dinner peaks** | +12% session-to-search rate | P1 |
| 4 | **Personalized coupon at cart abandonment** | -20% cart abandonment | P1 |
| 5 | **"Reorder" button on home screen** for returning users | +10% repeat rate | P2 |

---

## 📝 SQL Queries

The `sql/analysis_queries.sql` file contains **10 production-ready SQL queries** covering:
- Funnel conversion rates
- User segment comparison
- Cart abandonment reasons
- Peak hours analysis
- Retention (reorder within 7/14/30 days)
- Restaurant performance scorecard
- Coupon impact analysis
- City × Cuisine revenue matrix
- Payment method analysis
- Weekly growth trends

---

## 👤 Author

**[Penumala Navadeep]**  
Product Analyst | Data Analytics  


---

## 📄 License

This project is for educational and portfolio purposes.
