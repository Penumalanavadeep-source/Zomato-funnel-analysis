"""
=============================================================================
 Zomato Food Delivery — Funnel & Conversion Analysis
 Author: [Your Name]
 Purpose: Comprehensive product analytics on the food delivery funnel,
          generating actionable insights and professional visualizations.
=============================================================================

 Analyses Performed:
   1. Overall Funnel Visualization with drop-off rates
   2. Conversion by User Segment (New / Returning / Power)
   3. Cart Abandonment Analysis with reasons breakdown
   4. Hourly Conversion Patterns (time-of-day effects)
   5. Weekly Cohort Retention Heatmap
   6. Delivery Fee Impact on Checkout Conversion
   7. Cuisine Performance Analysis
   8. City-wise Funnel Comparison
   9. Platform (Device) Conversion Analysis
  10. Revenue & Order Trends
=============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from scipy import stats
from datetime import datetime, timedelta
import os
import warnings
warnings.filterwarnings('ignore')

# ─── Configuration ──────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs')

# Visual style
plt.rcParams.update({
    'figure.facecolor': 'white',
    'axes.facecolor': '#fafafa',
    'axes.grid': True,
    'grid.alpha': 0.3,
    'font.family': 'sans-serif',
    'font.size': 11,
    'axes.titlesize': 14,
    'axes.titleweight': 'bold',
    'figure.titlesize': 16,
    'figure.titleweight': 'bold',
})

# Zomato-inspired color palette
ZOMATO_RED = '#E23744'
ZOMATO_DARK = '#2D2D2D'
COLORS = ['#E23744', '#FF7043', '#FFB300', '#66BB6A', '#42A5F5', '#AB47BC',
          '#26A69A', '#EF5350', '#5C6BC0', '#8D6E63']
SEGMENT_COLORS = {'New': '#FF7043', 'Returning': '#42A5F5', 'Power': '#66BB6A'}


def load_data():
    """Load all generated CSV files."""
    print("\n📊 Loading data...")
    data = {}
    for file in ['users', 'restaurants', 'sessions', 'searches',
                  'impressions', 'cart_events', 'orders', 'funnel_events']:
        path = os.path.join(DATA_DIR, f'{file}.csv')
        data[file] = pd.read_csv(path)
        print(f"   ✓ {file}: {len(data[file]):,} rows")
    
    # Parse dates
    data['sessions']['session_start'] = pd.to_datetime(data['sessions']['session_start'])
    data['orders']['timestamp'] = pd.to_datetime(data['orders']['timestamp'])
    data['funnel_events']['timestamp'] = pd.to_datetime(data['funnel_events']['timestamp'])
    data['users']['signup_date'] = pd.to_datetime(data['users']['signup_date'])
    
    return data


# ═══════════════════════════════════════════════════════════════════════════
#  ANALYSIS 1: Overall Funnel Visualization
# ═══════════════════════════════════════════════════════════════════════════

def plot_overall_funnel(funnel_events):
    """Create a professional funnel visualization with drop-off rates."""
    print("\n📈 [1/10] Overall Funnel Visualization...")
    
    stages = ['session_start', 'search', 'restaurant_click', 'add_to_cart',
              'checkout_attempt', 'order_placed']
    labels = ['Session Start', 'Search', 'Restaurant\nClick', 'Add to\nCart',
              'Checkout\nAttempt', 'Order\nPlaced']
    
    counts = [len(funnel_events[funnel_events['event_type'] == s]) for s in stages]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7), gridspec_kw={'width_ratios': [2, 1]})
    fig.suptitle('Zomato Food Delivery — Conversion Funnel', fontsize=18, fontweight='bold', y=1.02)
    
    # Left: Funnel bar chart
    colors_gradient = [plt.cm.Reds(0.3 + 0.1 * i) for i in range(len(stages))]
    colors_gradient[0] = (0.886, 0.216, 0.267, 1.0)  # Zomato red
    
    bars = ax1.barh(range(len(stages)-1, -1, -1), counts, color=colors_gradient,
                    edgecolor='white', linewidth=1.5, height=0.6)
    
    # Add count and percentage labels
    for i, (bar, count) in enumerate(zip(bars, counts)):
        pct_of_total = count / counts[0] * 100
        ax1.text(bar.get_width() + counts[0]*0.01, bar.get_y() + bar.get_height()/2,
                f'{count:,}  ({pct_of_total:.1f}%)',
                va='center', fontsize=11, fontweight='bold')
    
    ax1.set_yticks(range(len(stages)-1, -1, -1))
    ax1.set_yticklabels(labels, fontsize=12)
    ax1.set_xlabel('Number of Events', fontsize=12)
    ax1.set_title('Funnel Volume at Each Stage', pad=15)
    ax1.set_xlim(0, counts[0] * 1.25)
    ax1.grid(axis='y', alpha=0)
    
    # Right: Step conversion rates
    step_conv = []
    for i in range(1, len(counts)):
        step_conv.append(counts[i] / counts[i-1] * 100)
    
    step_labels = ['Session→Search', 'Search→Click', 'Click→Cart',
                   'Cart→Checkout', 'Checkout→Order']
    
    bar_colors = [ZOMATO_RED if c < 50 else '#FF7043' if c < 70 else '#66BB6A' for c in step_conv]
    
    bars2 = ax2.barh(range(len(step_conv)-1, -1, -1), step_conv, color=bar_colors,
                     edgecolor='white', linewidth=1.5, height=0.6)
    
    for bar, conv in zip(bars2, step_conv):
        ax2.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                f'{conv:.1f}%', va='center', fontsize=12, fontweight='bold')
    
    ax2.set_yticks(range(len(step_conv)-1, -1, -1))
    ax2.set_yticklabels(step_labels, fontsize=11)
    ax2.set_xlabel('Conversion Rate (%)', fontsize=12)
    ax2.set_title('Step-wise Conversion Rates', pad=15)
    ax2.set_xlim(0, 110)
    ax2.axvline(x=50, color='red', linestyle='--', alpha=0.3, label='50% benchmark')
    ax2.grid(axis='y', alpha=0)
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, '01_overall_funnel.png'), dpi=150, bbox_inches='tight')
    plt.close()
    
    # Print insights
    overall_conv = counts[-1] / counts[0] * 100
    worst_step = step_labels[step_conv.index(min(step_conv))]
    print(f"   → Overall conversion: {overall_conv:.2f}%")
    print(f"   → Biggest drop-off at: {worst_step} ({min(step_conv):.1f}%)")


# ═══════════════════════════════════════════════════════════════════════════
#  ANALYSIS 2: Conversion by User Segment
# ═══════════════════════════════════════════════════════════════════════════

def plot_segment_funnel(funnel_events):
    """Compare funnel conversion across user segments."""
    print("\n📈 [2/10] Segment-wise Funnel Analysis...")
    
    stages = ['session_start', 'search', 'restaurant_click', 'add_to_cart',
              'checkout_attempt', 'order_placed']
    stage_labels = ['Session', 'Search', 'Rest. Click', 'Add Cart',
                    'Checkout', 'Order']
    segments = ['New', 'Returning', 'Power']
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle('Funnel Conversion by User Segment', fontsize=16, fontweight='bold')
    
    # Left: Absolute conversion rates from session to order
    segment_data = {}
    for seg in segments:
        seg_events = funnel_events[funnel_events['user_segment'] == seg]
        seg_counts = [len(seg_events[seg_events['event_type'] == s]) for s in stages]
        segment_data[seg] = seg_counts
    
    x = np.arange(len(stages))
    width = 0.25
    
    for i, seg in enumerate(segments):
        normalized = [c / segment_data[seg][0] * 100 for c in segment_data[seg]]
        axes[0].bar(x + i*width, normalized, width, label=seg,
                    color=SEGMENT_COLORS[seg], edgecolor='white')
    
    axes[0].set_xticks(x + width)
    axes[0].set_xticklabels(stage_labels)
    axes[0].set_ylabel('% of Sessions')
    axes[0].set_title('Funnel Progression (% of Sessions)')
    axes[0].legend()
    
    # Right: Step conversion comparison
    step_labels = ['→Search', '→Click', '→Cart', '→Checkout', '→Order']
    
    for i, seg in enumerate(segments):
        step_rates = []
        for j in range(1, len(stages)):
            if segment_data[seg][j-1] > 0:
                step_rates.append(segment_data[seg][j] / segment_data[seg][j-1] * 100)
            else:
                step_rates.append(0)
        axes[1].plot(step_labels, step_rates, 'o-', label=seg,
                     color=SEGMENT_COLORS[seg], linewidth=2, markersize=8)
    
    axes[1].set_ylabel('Step Conversion Rate (%)')
    axes[1].set_title('Step Conversion by Segment')
    axes[1].legend()
    axes[1].set_ylim(0, 100)
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, '02_segment_funnel.png'), dpi=150, bbox_inches='tight')
    plt.close()
    
    # Insight
    for seg in segments:
        overall = segment_data[seg][-1] / segment_data[seg][0] * 100 if segment_data[seg][0] > 0 else 0
        print(f"   → {seg} users overall conversion: {overall:.2f}%")


# ═══════════════════════════════════════════════════════════════════════════
#  ANALYSIS 3: Cart Abandonment Analysis
# ═══════════════════════════════════════════════════════════════════════════

def plot_cart_abandonment(cart_events):
    """Analyze cart abandonment rates and reasons."""
    print("\n📈 [3/10] Cart Abandonment Analysis...")
    
    total_carts = len(cart_events)
    abandoned = cart_events[cart_events['abandoned'] == True]
    completed = cart_events[cart_events['abandoned'] == False]
    
    abandon_rate = len(abandoned) / total_carts * 100
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle(f'Cart Abandonment Analysis (Overall Rate: {abandon_rate:.1f}%)',
                 fontsize=16, fontweight='bold')
    
    # Left: Abandonment rate pie
    axes[0].pie([len(completed), len(abandoned)],
                labels=['Completed', 'Abandoned'],
                colors=['#66BB6A', ZOMATO_RED],
                autopct='%1.1f%%', startangle=90,
                textprops={'fontsize': 13, 'fontweight': 'bold'},
                explode=(0, 0.05))
    axes[0].set_title(f'Cart Outcomes\n({total_carts:,} total carts)')
    
    # Middle: Abandonment reasons
    if 'abandonment_reason' in abandoned.columns:
        reasons = abandoned['abandonment_reason'].value_counts()
        reason_colors = [ZOMATO_RED, '#FF7043', '#FFB300', '#42A5F5', '#AB47BC', '#26A69A']
        axes[1].barh(reasons.index, reasons.values,
                     color=reason_colors[:len(reasons)], edgecolor='white')
        for i, (val, label) in enumerate(zip(reasons.values, reasons.index)):
            axes[1].text(val + 5, i, f'{val:,} ({val/len(abandoned)*100:.1f}%)',
                        va='center', fontsize=10, fontweight='bold')
        axes[1].set_xlabel('Number of Abandoned Carts')
        axes[1].set_title('Abandonment Reasons')
        axes[1].grid(axis='y', alpha=0)
    
    # Right: Abandonment rate by delivery fee
    cart_events_with_fee = cart_events.copy()
    cart_events_with_fee['fee_bucket'] = pd.cut(
        cart_events_with_fee['delivery_fee'],
        bins=[-1, 0, 20, 40, 60],
        labels=['Free', '₹1-20', '₹21-40', '₹41-60']
    )
    
    abandon_by_fee = cart_events_with_fee.groupby('fee_bucket', observed=False)['abandoned'].mean() * 100
    
    bar_colors = ['#66BB6A', '#FFB300', '#FF7043', ZOMATO_RED]
    axes[2].bar(abandon_by_fee.index, abandon_by_fee.values,
                color=bar_colors, edgecolor='white', linewidth=1.5)
    
    for i, val in enumerate(abandon_by_fee.values):
        axes[2].text(i, val + 1, f'{val:.1f}%', ha='center',
                     fontsize=12, fontweight='bold')
    
    axes[2].set_ylabel('Abandonment Rate (%)')
    axes[2].set_xlabel('Delivery Fee Range')
    axes[2].set_title('Abandonment by Delivery Fee')
    axes[2].set_ylim(0, max(abandon_by_fee.values) * 1.2)
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, '03_cart_abandonment.png'), dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"   → Abandonment rate: {abandon_rate:.1f}%")
    if 'abandonment_reason' in abandoned.columns:
        top_reason = abandoned['abandonment_reason'].mode().iloc[0]
        print(f"   → Top reason: {top_reason}")


# ═══════════════════════════════════════════════════════════════════════════
#  ANALYSIS 4: Hourly Conversion Patterns
# ═══════════════════════════════════════════════════════════════════════════

def plot_hourly_patterns(funnel_events, sessions):
    """Analyze conversion rates by hour of day."""
    print("\n📈 [4/10] Hourly Conversion Patterns...")
    
    # Merge session hour info with funnel events
    session_hours = sessions[['session_id', 'hour_of_day', 'is_weekend']].copy()
    
    hourly_sessions = funnel_events[funnel_events['event_type'] == 'session_start'].merge(
        session_hours, on='session_id', how='left'
    )
    hourly_orders = funnel_events[funnel_events['event_type'] == 'order_placed'].merge(
        session_hours, on='session_id', how='left'
    )
    
    session_counts = hourly_sessions.groupby('hour_of_day').size()
    order_counts = hourly_orders.groupby('hour_of_day').size()
    
    hourly_conv = (order_counts / session_counts * 100).fillna(0)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    fig.suptitle('Hourly Patterns — Volume & Conversion', fontsize=16, fontweight='bold')
    
    # Top: Volume by hour
    hours = range(24)
    session_vals = [session_counts.get(h, 0) for h in hours]
    order_vals = [order_counts.get(h, 0) for h in hours]
    
    ax1.fill_between(hours, session_vals, alpha=0.3, color='#42A5F5')
    ax1.plot(hours, session_vals, 'o-', color='#42A5F5', label='Sessions', linewidth=2)
    ax1.fill_between(hours, order_vals, alpha=0.3, color=ZOMATO_RED)
    ax1.plot(hours, order_vals, 's-', color=ZOMATO_RED, label='Orders', linewidth=2)
    
    # Highlight peak hours
    for peak in [12, 13, 19, 20, 21]:
        ax1.axvspan(peak-0.5, peak+0.5, alpha=0.08, color='gold')
    
    ax1.set_xlabel('Hour of Day')
    ax1.set_ylabel('Count')
    ax1.set_title('Session & Order Volume by Hour')
    ax1.legend(fontsize=12)
    ax1.set_xticks(range(24))
    ax1.set_xticklabels([f'{h:02d}:00' for h in range(24)], rotation=45, fontsize=9)
    
    # Bottom: Conversion rate by hour
    conv_vals = [hourly_conv.get(h, 0) for h in hours]
    bar_colors = [ZOMATO_RED if v >= np.percentile(conv_vals, 75) else '#FF7043'
                  if v >= np.percentile(conv_vals, 50) else '#BDBDBD' for v in conv_vals]
    
    ax2.bar(hours, conv_vals, color=bar_colors, edgecolor='white', linewidth=0.5)
    avg_conv = np.mean(conv_vals)
    ax2.axhline(y=avg_conv, color=ZOMATO_DARK, linestyle='--', alpha=0.5,
                label=f'Average: {avg_conv:.1f}%')
    
    ax2.set_xlabel('Hour of Day')
    ax2.set_ylabel('Conversion Rate (%)')
    ax2.set_title('Session-to-Order Conversion by Hour')
    ax2.set_xticks(range(24))
    ax2.set_xticklabels([f'{h:02d}:00' for h in range(24)], rotation=45, fontsize=9)
    ax2.legend(fontsize=12)
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, '04_hourly_patterns.png'), dpi=150, bbox_inches='tight')
    plt.close()
    
    peak_hour = max(hours, key=lambda h: hourly_conv.get(h, 0))
    print(f"   → Peak conversion hour: {peak_hour:02d}:00 ({hourly_conv.get(peak_hour, 0):.1f}%)")


# ═══════════════════════════════════════════════════════════════════════════
#  ANALYSIS 5: Cohort Retention Heatmap
# ═══════════════════════════════════════════════════════════════════════════

def plot_cohort_retention(orders, users):
    """Build weekly cohort retention analysis."""
    print("\n📈 [5/10] Cohort Retention Heatmap...")
    
    # Merge user info with orders
    order_users = orders.merge(users[['user_id', 'signup_date']], on='user_id')
    order_users['order_date'] = pd.to_datetime(order_users['timestamp'])
    
    # Create weekly cohorts based on first order
    first_orders = order_users.groupby('user_id')['order_date'].min().reset_index()
    first_orders.columns = ['user_id', 'first_order_date']
    first_orders['cohort_week'] = first_orders['first_order_date'].dt.to_period('W')
    
    # Merge cohort back
    order_users = order_users.merge(first_orders[['user_id', 'cohort_week']], on='user_id')
    order_users['order_week'] = order_users['order_date'].dt.to_period('W')
    
    # Calculate week number relative to cohort
    order_users['weeks_since_first'] = (
        order_users['order_week'].apply(lambda x: x.start_time) -
        order_users['cohort_week'].apply(lambda x: x.start_time)
    ).dt.days // 7
    
    # Build retention matrix
    cohort_sizes = first_orders.groupby('cohort_week').size()
    retention_data = order_users.groupby(['cohort_week', 'weeks_since_first'])['user_id'].nunique()
    
    # Limit to first 12 cohorts and 10 weeks
    cohorts = sorted(cohort_sizes.index)[:12]
    max_weeks = 10
    
    retention_matrix = pd.DataFrame(index=range(len(cohorts)), columns=range(max_weeks + 1))
    
    for i, cohort in enumerate(cohorts):
        cohort_size = cohort_sizes.get(cohort, 0)
        if cohort_size == 0:
            continue
        for week in range(max_weeks + 1):
            if (cohort, week) in retention_data:
                retention_matrix.loc[i, week] = retention_data[(cohort, week)] / cohort_size * 100
            else:
                retention_matrix.loc[i, week] = 0
    
    retention_matrix = retention_matrix.astype(float)
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    sns.heatmap(retention_matrix, annot=True, fmt='.0f', cmap='YlOrRd',
                linewidths=0.5, linecolor='white',
                cbar_kws={'label': 'Retention %'},
                ax=ax, vmin=0, vmax=100)
    
    ax.set_xlabel('Weeks Since First Order', fontsize=12)
    ax.set_ylabel('Cohort (Week)', fontsize=12)
    ax.set_title('Weekly Cohort Retention Heatmap\n(% of users who reordered)', fontsize=16, fontweight='bold')
    
    cohort_labels = [str(c) for c in cohorts]
    ax.set_yticklabels(cohort_labels[:len(retention_matrix)], rotation=0, fontsize=9)
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, '05_cohort_retention.png'), dpi=150, bbox_inches='tight')
    plt.close()
    
    # Calculate average week-1 retention
    week1_retention = retention_matrix[1].mean()
    print(f"   → Average Week-1 retention: {week1_retention:.1f}%")


# ═══════════════════════════════════════════════════════════════════════════
#  ANALYSIS 6: Delivery Fee Impact
# ═══════════════════════════════════════════════════════════════════════════

def plot_delivery_fee_impact(cart_events, orders):
    """Analyze how delivery fee affects checkout conversion."""
    print("\n📈 [6/10] Delivery Fee Impact Analysis...")
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle('Impact of Delivery Fee on Conversion & Revenue',
                 fontsize=16, fontweight='bold')
    
    # Left: Checkout conversion by delivery fee
    cart_events_copy = cart_events.copy()
    cart_events_copy['fee_bucket'] = pd.cut(
        cart_events_copy['delivery_fee'],
        bins=[-1, 0, 15, 30, 45, 60],
        labels=['Free (₹0)', '₹1-15', '₹16-30', '₹31-45', '₹46-60']
    )
    
    checkout_rate = cart_events_copy.groupby('fee_bucket', observed=False).apply(
        lambda x: (x['abandoned'] == False).mean() * 100
    )
    
    colors = ['#2E7D32', '#66BB6A', '#FFB300', '#FF7043', '#D32F2F']
    axes[0].bar(checkout_rate.index, checkout_rate.values, color=colors, edgecolor='white')
    
    for i, val in enumerate(checkout_rate.values):
        axes[0].text(i, val + 1.5, f'{val:.1f}%', ha='center',
                     fontsize=12, fontweight='bold')
    
    axes[0].set_ylabel('Checkout Completion Rate (%)')
    axes[0].set_xlabel('Delivery Fee Range')
    axes[0].set_title('Checkout Conversion by Delivery Fee')
    axes[0].tick_params(axis='x', rotation=15)
    
    # Right: Avg order value by delivery fee
    orders_copy = orders.copy()
    orders_copy['fee_bucket'] = pd.cut(
        orders_copy['delivery_fee'],
        bins=[-1, 0, 15, 30, 45, 60],
        labels=['Free', '₹1-15', '₹16-30', '₹31-45', '₹46-60']
    )
    
    aov_by_fee = orders_copy.groupby('fee_bucket', observed=False)['final_order_value'].mean()
    order_count_by_fee = orders_copy.groupby('fee_bucket', observed=False).size()
    
    axes[1].bar(aov_by_fee.index, aov_by_fee.values, color='#42A5F5', edgecolor='white',
                alpha=0.8, label='Avg Order Value')
    
    ax2 = axes[1].twinx()
    ax2.plot(order_count_by_fee.index, order_count_by_fee.values, 'D-',
             color=ZOMATO_RED, linewidth=2, markersize=8, label='Order Count')
    ax2.set_ylabel('Number of Orders', color=ZOMATO_RED)
    
    axes[1].set_ylabel('Avg Order Value (₹)')
    axes[1].set_xlabel('Delivery Fee Range')
    axes[1].set_title('AOV & Volume by Delivery Fee')
    axes[1].tick_params(axis='x', rotation=15)
    
    # Combined legend
    lines1, labels1 = axes[1].get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    axes[1].legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, '06_delivery_fee_impact.png'), dpi=150, bbox_inches='tight')
    plt.close()
    
    # Statistical test
    free_checkout = cart_events_copy[cart_events_copy['delivery_fee'] == 0]['abandoned'].mean()
    paid_checkout = cart_events_copy[cart_events_copy['delivery_fee'] > 30]['abandoned'].mean()
    print(f"   → Free delivery abandonment: {free_checkout*100:.1f}%")
    print(f"   → High fee (>₹30) abandonment: {paid_checkout*100:.1f}%")


# ═══════════════════════════════════════════════════════════════════════════
#  ANALYSIS 7: Cuisine Performance
# ═══════════════════════════════════════════════════════════════════════════

def plot_cuisine_analysis(orders, restaurants):
    """Analyze cuisine-wise performance."""
    print("\n📈 [7/10] Cuisine Performance Analysis...")
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle('Cuisine Performance Analysis', fontsize=16, fontweight='bold')
    
    # Left: Orders and revenue by cuisine
    cuisine_stats = orders.groupby('cuisine').agg(
        order_count=('order_id', 'count'),
        total_revenue=('final_order_value', 'sum'),
        avg_order_value=('final_order_value', 'mean'),
        avg_rating=('rating_given', 'mean')
    ).sort_values('order_count', ascending=True)
    
    top_cuisines = cuisine_stats.tail(10)
    
    axes[0].barh(top_cuisines.index, top_cuisines['order_count'],
                 color=COLORS[:len(top_cuisines)], edgecolor='white')
    
    for i, (val, rev) in enumerate(zip(top_cuisines['order_count'], top_cuisines['total_revenue'])):
        axes[0].text(val + 5, i, f'{val:,} orders | ₹{rev/1000:.0f}K',
                     va='center', fontsize=9, fontweight='bold')
    
    axes[0].set_xlabel('Number of Orders')
    axes[0].set_title('Top Cuisines by Order Volume')
    axes[0].grid(axis='y', alpha=0)
    
    # Right: AOV vs Rating bubble chart
    cuisine_agg = orders.groupby('cuisine').agg(
        avg_order_value=('final_order_value', 'mean'),
        avg_rating=('rating_given', 'mean'),
        order_count=('order_id', 'count')
    ).reset_index()
    
    scatter_colors = plt.cm.Set3(np.linspace(0, 1, len(cuisine_agg)))
    scatter = axes[1].scatter(
        cuisine_agg['avg_rating'], cuisine_agg['avg_order_value'],
        s=cuisine_agg['order_count'] * 0.5, alpha=0.7,
        c=scatter_colors, edgecolors='white', linewidth=1.5
    )
    
    for _, row in cuisine_agg.iterrows():
        axes[1].annotate(row['cuisine'], (row['avg_rating'], row['avg_order_value']),
                        fontsize=8, ha='center', va='bottom', fontweight='bold')
    
    axes[1].set_xlabel('Average Rating')
    axes[1].set_ylabel('Avg Order Value (₹)')
    axes[1].set_title('Cuisine: Rating vs AOV (bubble = volume)')
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, '07_cuisine_analysis.png'), dpi=150, bbox_inches='tight')
    plt.close()
    
    top = cuisine_stats.tail(3).index.tolist()[::-1]
    print(f"   → Top 3 cuisines: {', '.join(top)}")


# ═══════════════════════════════════════════════════════════════════════════
#  ANALYSIS 8: City-wise Funnel Comparison
# ═══════════════════════════════════════════════════════════════════════════

def plot_city_comparison(funnel_events, orders):
    """Compare funnel performance across cities."""
    print("\n📈 [8/10] City-wise Comparison...")
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle('City-wise Performance Comparison', fontsize=16, fontweight='bold')
    
    # Calculate conversion by city
    city_sessions = funnel_events[funnel_events['event_type'] == 'session_start'].groupby('city').size()
    city_orders = funnel_events[funnel_events['event_type'] == 'order_placed'].groupby('city').size()
    
    city_conv = (city_orders / city_sessions * 100).sort_values(ascending=True)
    
    colors = plt.cm.RdYlGn(np.linspace(0.2, 0.9, len(city_conv)))
    
    axes[0].barh(city_conv.index, city_conv.values, color=colors, edgecolor='white')
    
    for i, val in enumerate(city_conv.values):
        axes[0].text(val + 0.2, i, f'{val:.1f}%', va='center',
                     fontsize=11, fontweight='bold')
    
    avg_conv = city_conv.mean()
    axes[0].axvline(x=avg_conv, color=ZOMATO_RED, linestyle='--', alpha=0.7,
                    label=f'Avg: {avg_conv:.1f}%')
    axes[0].set_xlabel('Session-to-Order Conversion (%)')
    axes[0].set_title('Conversion Rate by City')
    axes[0].legend()
    axes[0].grid(axis='y', alpha=0)
    
    # Right: Revenue and AOV by city
    city_revenue = orders.groupby('city').agg(
        revenue=('final_order_value', 'sum'),
        aov=('final_order_value', 'mean'),
        orders=('order_id', 'count')
    ).sort_values('revenue', ascending=True)
    
    axes[1].barh(city_revenue.index, city_revenue['revenue'] / 1000,
                 color='#42A5F5', edgecolor='white', alpha=0.8)
    
    for i, (rev, aov) in enumerate(zip(city_revenue['revenue'], city_revenue['aov'])):
        axes[1].text(rev/1000 + 2, i, f'₹{rev/1000:.0f}K (AOV: ₹{aov:.0f})',
                     va='center', fontsize=9, fontweight='bold')
    
    axes[1].set_xlabel('Total Revenue (₹ thousands)')
    axes[1].set_title('Revenue by City')
    axes[1].grid(axis='y', alpha=0)
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, '08_city_comparison.png'), dpi=150, bbox_inches='tight')
    plt.close()
    
    best_city = city_conv.idxmax()
    print(f"   → Best converting city: {best_city} ({city_conv.max():.1f}%)")


# ═══════════════════════════════════════════════════════════════════════════
#  ANALYSIS 9: Platform / Device Analysis
# ═══════════════════════════════════════════════════════════════════════════

def plot_platform_analysis(funnel_events):
    """Analyze conversion by platform/device type."""
    print("\n📈 [9/10] Platform Analysis...")
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle('Platform / Device Analysis', fontsize=16, fontweight='bold')
    
    platforms = ['Android', 'iOS', 'Web']
    platform_colors = {'Android': '#3DDC84', 'iOS': '#007AFF', 'Web': '#FF7043'}
    
    stages = ['session_start', 'search', 'restaurant_click', 'add_to_cart',
              'checkout_attempt', 'order_placed']
    stage_short = ['Session', 'Search', 'Click', 'Cart', 'Checkout', 'Order']
    
    # Left: Funnel by platform
    for platform in platforms:
        pf_events = funnel_events[funnel_events['platform'] == platform]
        counts = [len(pf_events[pf_events['event_type'] == s]) for s in stages]
        if counts[0] > 0:
            normalized = [c / counts[0] * 100 for c in counts]
        else:
            normalized = [0] * len(counts)
        axes[0].plot(stage_short, normalized, 'o-', label=platform,
                     color=platform_colors[platform], linewidth=2.5, markersize=8)
    
    axes[0].set_ylabel('% of Sessions Retained')
    axes[0].set_title('Funnel Progression by Platform')
    axes[0].legend(fontsize=12)
    axes[0].set_ylim(0, 110)
    
    # Right: Overall conversion by platform
    conv_data = {}
    for platform in platforms:
        pf_events = funnel_events[funnel_events['platform'] == platform]
        sessions = len(pf_events[pf_events['event_type'] == 'session_start'])
        orders = len(pf_events[pf_events['event_type'] == 'order_placed'])
        conv_data[platform] = orders / sessions * 100 if sessions > 0 else 0
    
    bars = axes[1].bar(conv_data.keys(), conv_data.values(),
                       color=[platform_colors[p] for p in conv_data.keys()],
                       edgecolor='white', linewidth=2)
    
    for bar, val in zip(bars, conv_data.values()):
        axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                     f'{val:.1f}%', ha='center', fontsize=14, fontweight='bold')
    
    axes[1].set_ylabel('Session → Order Conversion (%)')
    axes[1].set_title('Overall Conversion by Platform')
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, '09_platform_analysis.png'), dpi=150, bbox_inches='tight')
    plt.close()
    
    best_platform = max(conv_data, key=conv_data.get)
    print(f"   → Best converting platform: {best_platform} ({conv_data[best_platform]:.1f}%)")


# ═══════════════════════════════════════════════════════════════════════════
#  ANALYSIS 10: Revenue & Order Trends
# ═══════════════════════════════════════════════════════════════════════════

def plot_revenue_trends(orders):
    """Analyze weekly revenue and order trends."""
    print("\n📈 [10/10] Revenue & Order Trends...")
    
    orders_copy = orders.copy()
    orders_copy['week'] = orders_copy['timestamp'].dt.to_period('W').apply(lambda x: x.start_time)
    
    weekly = orders_copy.groupby('week').agg(
        orders=('order_id', 'count'),
        revenue=('final_order_value', 'sum'),
        aov=('final_order_value', 'mean'),
        unique_users=('user_id', 'nunique'),
        avg_delivery_time=('delivery_time_mins', 'mean')
    ).reset_index()
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    fig.suptitle('Weekly Revenue & Order Trends', fontsize=16, fontweight='bold')
    
    # Top-left: Order volume
    axes[0, 0].fill_between(weekly['week'], weekly['orders'], alpha=0.3, color=ZOMATO_RED)
    axes[0, 0].plot(weekly['week'], weekly['orders'], '-', color=ZOMATO_RED, linewidth=2)
    axes[0, 0].set_title('Weekly Order Volume')
    axes[0, 0].set_ylabel('Orders')
    axes[0, 0].tick_params(axis='x', rotation=45)
    
    # Top-right: Revenue
    axes[0, 1].fill_between(weekly['week'], weekly['revenue']/1000, alpha=0.3, color='#42A5F5')
    axes[0, 1].plot(weekly['week'], weekly['revenue']/1000, '-', color='#42A5F5', linewidth=2)
    axes[0, 1].set_title('Weekly Revenue')
    axes[0, 1].set_ylabel('Revenue (₹K)')
    axes[0, 1].tick_params(axis='x', rotation=45)
    
    # Bottom-left: AOV trend
    axes[1, 0].plot(weekly['week'], weekly['aov'], 'o-', color='#66BB6A', linewidth=2)
    avg_aov = weekly['aov'].mean()
    axes[1, 0].axhline(y=avg_aov, color='gray', linestyle='--', alpha=0.5,
                        label=f'Avg: ₹{avg_aov:.0f}')
    axes[1, 0].set_title('Avg Order Value Trend')
    axes[1, 0].set_ylabel('AOV (₹)')
    axes[1, 0].legend()
    axes[1, 0].tick_params(axis='x', rotation=45)
    
    # Bottom-right: Unique ordering users
    axes[1, 1].bar(weekly['week'], weekly['unique_users'], color='#AB47BC',
                   edgecolor='white', width=5)
    axes[1, 1].set_title('Weekly Active Ordering Users')
    axes[1, 1].set_ylabel('Unique Users')
    axes[1, 1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, '10_revenue_trends.png'), dpi=150, bbox_inches='tight')
    plt.close()
    
    total_revenue = orders_copy['final_order_value'].sum()
    total_orders = len(orders_copy)
    print(f"   → Total orders: {total_orders:,}")
    print(f"   → Total revenue: ₹{total_revenue:,.0f}")
    print(f"   → Average AOV: ₹{total_revenue/total_orders:.0f}")


# ═══════════════════════════════════════════════════════════════════════════
#  EXECUTIVE SUMMARY — Key Metrics
# ═══════════════════════════════════════════════════════════════════════════

def generate_summary(data):
    """Generate key metrics summary."""
    print("\n" + "=" * 60)
    print("  📋 EXECUTIVE SUMMARY")
    print("=" * 60)
    
    funnel = data['funnel_events']
    orders = data['orders']
    cart = data['cart_events']
    
    total_sessions = len(funnel[funnel['event_type'] == 'session_start'])
    total_orders = len(funnel[funnel['event_type'] == 'order_placed'])
    overall_conv = total_orders / total_sessions * 100
    
    total_revenue = orders['final_order_value'].sum()
    avg_aov = orders['final_order_value'].mean()
    total_carts = len(cart)
    abandon_rate = cart['abandoned'].mean() * 100
    
    unique_orderers = orders['user_id'].nunique()
    repeat_orderers = orders.groupby('user_id').size()
    repeat_rate = (repeat_orderers > 1).mean() * 100
    
    avg_delivery_time = orders['delivery_time_mins'].mean()
    avg_rating = orders['rating_given'].mean()
    
    summary = f"""
    ┌─────────────────────────────────────────────────────────┐
    │  OVERALL METRICS                                        │
    ├─────────────────────────────────────────────────────────┤
    │  Total Sessions:          {total_sessions:>10,}                    │
    │  Total Orders:            {total_orders:>10,}                    │
    │  Overall Conversion:      {overall_conv:>9.2f}%                    │
    │  Total Revenue:           ₹{total_revenue:>10,.0f}                 │
    │  Average Order Value:     ₹{avg_aov:>10,.0f}                    │
    ├─────────────────────────────────────────────────────────┤
    │  ENGAGEMENT                                             │
    │  Unique Orderers:         {unique_orderers:>10,}                    │
    │  Repeat Order Rate:       {repeat_rate:>9.1f}%                    │
    │  Cart Abandonment Rate:   {abandon_rate:>9.1f}%                    │
    ├─────────────────────────────────────────────────────────┤
    │  OPERATIONS                                             │
    │  Avg Delivery Time:       {avg_delivery_time:>8.1f} mins                  │
    │  Avg Order Rating:        {avg_rating:>8.1f} / 5.0                   │
    └─────────────────────────────────────────────────────────┘
    """
    print(summary)
    
    # Save summary to file
    with open(os.path.join(OUTPUT_DIR, 'summary_metrics.txt'), 'w') as f:
        f.write(summary)
    
    return {
        'total_sessions': total_sessions,
        'total_orders': total_orders,
        'overall_conv': overall_conv,
        'total_revenue': total_revenue,
        'avg_aov': avg_aov,
        'abandon_rate': abandon_rate,
        'repeat_rate': repeat_rate,
        'avg_delivery_time': avg_delivery_time,
    }


# ═══════════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("  Zomato Food Delivery — Funnel & Conversion Analysis")
    print("=" * 60)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Load data
    data = load_data()
    
    # Run all analyses
    plot_overall_funnel(data['funnel_events'])
    plot_segment_funnel(data['funnel_events'])
    plot_cart_abandonment(data['cart_events'])
    plot_hourly_patterns(data['funnel_events'], data['sessions'])
    plot_cohort_retention(data['orders'], data['users'])
    plot_delivery_fee_impact(data['cart_events'], data['orders'])
    plot_cuisine_analysis(data['orders'], data['restaurants'])
    plot_city_comparison(data['funnel_events'], data['orders'])
    plot_platform_analysis(data['funnel_events'])
    plot_revenue_trends(data['orders'])
    
    # Executive summary
    metrics = generate_summary(data)
    
    print("\n  ✅ All analyses complete!")
    print(f"  📊 Charts saved to: {OUTPUT_DIR}")
    print(f"  📁 10 visualization files generated")
    
    return metrics


if __name__ == '__main__':
    main()
