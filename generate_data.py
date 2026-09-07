"""
=============================================================================
 Zomato Food Delivery — Synthetic Data Generator
 Author: [Your Name]
 Purpose: Generate realistic synthetic data simulating Zomato's food delivery
          funnel for product analytics portfolio project.
=============================================================================

 Data Tables Generated:
   1. users.csv          — 10,000 users with demographics
   2. restaurants.csv    — 500 restaurants across cities
   3. sessions.csv       — 50,000 app sessions over 6 months
   4. searches.csv       — search events within sessions
   5. impressions.csv    — restaurant impressions shown in search results
   6. cart_events.csv    — add-to-cart events
   7. orders.csv         — completed orders
   8. funnel_events.csv  — unified event log for funnel analysis

 Realistic Patterns Embedded:
   - New users convert at lower rates than returning/power users
   - Lunch (12–2 PM) and dinner (7–10 PM) peaks
   - Weekends have 25% higher order volume
   - Higher delivery fees → lower checkout conversion
   - Coupons boost checkout conversion by ~15%
   - Higher-rated restaurants get more clicks
   - Promoted restaurants get 2x impression-to-click rate
=============================================================================
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import warnings
warnings.filterwarnings('ignore')

# ─── Reproducibility ────────────────────────────────────────────────────────
np.random.seed(42)

# ─── Configuration ──────────────────────────────────────────────────────────
NUM_USERS = 10_000
NUM_RESTAURANTS = 500
NUM_SESSIONS = 50_000
START_DATE = datetime(2026, 3, 1)
END_DATE = datetime(2026, 8, 31)
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

# ─── Reference Data ─────────────────────────────────────────────────────────
CITIES = {
    'Mumbai': 0.18, 'Delhi NCR': 0.20, 'Bangalore': 0.15,
    'Hyderabad': 0.12, 'Chennai': 0.08, 'Pune': 0.08,
    'Kolkata': 0.07, 'Ahmedabad': 0.05, 'Jaipur': 0.04, 'Lucknow': 0.03
}

CUISINES = [
    'North Indian', 'South Indian', 'Chinese', 'Italian', 'Fast Food',
    'Biryani', 'Street Food', 'Desserts', 'Healthy Food', 'Pizza',
    'Mughlai', 'Continental', 'Thai', 'Rolls', 'Beverages'
]

CUISINE_WEIGHTS = [0.15, 0.10, 0.12, 0.06, 0.13, 0.10, 0.08, 0.05, 0.04, 0.07,
                   0.03, 0.02, 0.02, 0.02, 0.01]

AGE_GROUPS = ['18-24', '25-34', '35-44', '45+']
AGE_WEIGHTS = [0.30, 0.40, 0.20, 0.10]

DEVICES = ['Android', 'iOS', 'Web']
DEVICE_WEIGHTS = [0.55, 0.30, 0.15]

PAYMENT_METHODS = ['UPI', 'Credit Card', 'Debit Card', 'Wallet', 'COD']
PAYMENT_WEIGHTS = [0.40, 0.15, 0.10, 0.20, 0.15]

RESTAURANT_NAME_PREFIXES = [
    'Royal', 'Golden', 'Silver', 'Green', 'Blue', 'Red', 'Fresh', 'Spice',
    'Taste', 'Foodie', 'Hungry', 'Yummy', 'Desi', 'Urban', 'Classic'
]
RESTAURANT_NAME_SUFFIXES = [
    'Kitchen', 'Dhaba', 'Cafe', 'Grill', 'House', 'Express', 'Bites',
    'Corner', 'Hub', 'Point', 'Palace', 'Junction', 'Spot', 'Den', 'Box'
]


def generate_users():
    """Generate user profiles with realistic demographics."""
    print("  Generating users...")
    
    signup_dates = [
        START_DATE - timedelta(days=np.random.randint(1, 365))
        for _ in range(NUM_USERS)
    ]
    
    cities = np.random.choice(
        list(CITIES.keys()), NUM_USERS, p=list(CITIES.values())
    )
    
    users = pd.DataFrame({
        'user_id': range(1, NUM_USERS + 1),
        'signup_date': signup_dates,
        'city': cities,
        'age_group': np.random.choice(AGE_GROUPS, NUM_USERS, p=AGE_WEIGHTS),
        'device_type': np.random.choice(DEVICES, NUM_USERS, p=DEVICE_WEIGHTS),
    })
    
    # User segment based on account age
    days_since_signup = [(START_DATE - d).days for d in signup_dates]
    segments = []
    for days in days_since_signup:
        if days < 30:
            segments.append('New')
        elif days < 90:
            segments.append('Returning')
        else:
            segments.append('Power' if np.random.random() < 0.35 else 'Returning')
    users['user_segment'] = segments
    
    return users


def generate_restaurants():
    """Generate restaurant listings with realistic attributes."""
    print("  Generating restaurants...")
    
    names = []
    for i in range(NUM_RESTAURANTS):
        prefix = np.random.choice(RESTAURANT_NAME_PREFIXES)
        suffix = np.random.choice(RESTAURANT_NAME_SUFFIXES)
        names.append(f"{prefix} {suffix} #{i+1}")
    
    ratings = np.clip(np.random.normal(3.8, 0.6, NUM_RESTAURANTS), 2.0, 5.0).round(1)
    
    restaurants = pd.DataFrame({
        'restaurant_id': range(1, NUM_RESTAURANTS + 1),
        'name': names,
        'cuisine': np.random.choice(CUISINES, NUM_RESTAURANTS, p=CUISINE_WEIGHTS),
        'city': np.random.choice(list(CITIES.keys()), NUM_RESTAURANTS, p=list(CITIES.values())),
        'rating': ratings,
        'avg_cost_for_two': np.random.choice(
            [200, 300, 400, 500, 600, 800, 1000, 1200, 1500],
            NUM_RESTAURANTS,
            p=[0.10, 0.15, 0.20, 0.18, 0.15, 0.10, 0.06, 0.04, 0.02]
        ),
        'avg_delivery_time_mins': np.clip(
            np.random.normal(35, 10, NUM_RESTAURANTS), 15, 60
        ).astype(int),
        'has_photos': np.random.choice([True, False], NUM_RESTAURANTS, p=[0.7, 0.3]),
        'is_promoted': np.random.choice([True, False], NUM_RESTAURANTS, p=[0.15, 0.85]),
        'delivery_fee': np.random.choice(
            [0, 15, 25, 35, 49, 59], NUM_RESTAURANTS,
            p=[0.15, 0.20, 0.25, 0.20, 0.12, 0.08]
        ),
        'total_reviews': np.random.randint(10, 5000, NUM_RESTAURANTS)
    })
    
    return restaurants


def generate_sessions(users):
    """Generate app sessions with time-of-day and day-of-week patterns."""
    print("  Generating sessions...")
    
    total_days = (END_DATE - START_DATE).days
    sessions = []
    
    for i in range(NUM_SESSIONS):
        user = users.sample(1).iloc[0]
        
        # Generate timestamp with realistic patterns
        day_offset = np.random.randint(0, total_days)
        session_date = START_DATE + timedelta(days=day_offset)
        
        # Hour distribution: peaks at lunch (12-14) and dinner (19-22)
        hour_probs = np.array([
            0.01, 0.005, 0.005, 0.005, 0.005, 0.01,  # 0-5 AM
            0.02, 0.03, 0.04, 0.05, 0.06, 0.08,       # 6-11 AM
            0.10, 0.09, 0.06, 0.04, 0.05, 0.06,       # 12-5 PM
            0.07, 0.09, 0.10, 0.08, 0.05, 0.03         # 6-11 PM
        ])
        hour_probs = hour_probs / hour_probs.sum()  # Normalize to sum to 1
        hour = np.random.choice(range(24), p=hour_probs)
        minute = np.random.randint(0, 60)
        
        session_ts = session_date.replace(hour=hour, minute=minute)
        
        # Session duration: 1–20 minutes, skewed short
        duration = int(np.clip(np.random.exponential(5) * 60, 30, 1200))
        
        sessions.append({
            'session_id': i + 1,
            'user_id': user['user_id'],
            'session_start': session_ts,
            'session_duration_secs': duration,
            'platform': user['device_type'],
            'day_of_week': session_ts.strftime('%A'),
            'hour_of_day': hour,
            'is_weekend': session_date.weekday() >= 5
        })
    
    return pd.DataFrame(sessions)


def simulate_funnel(sessions, users, restaurants):
    """
    Simulate the conversion funnel for each session.
    
    Funnel Stages:
      1. Session Start → Search         (~82%)
      2. Search → Restaurant Click      (~58%)
      3. Restaurant Click → Add to Cart  (~38%)
      4. Add to Cart → Checkout Attempt  (~72%)
      5. Checkout → Order Placed         (~83%)
    
    Conversion rates vary by user segment, time, and other factors.
    """
    print("  Simulating funnel events...")
    
    searches = []
    impressions = []
    cart_events = []
    orders = []
    funnel_events = []
    
    search_id = 0
    impression_id = 0
    cart_id = 0
    order_id = 0
    
    user_order_count = {}  # Track orders per user for reorder analysis
    
    for _, session in sessions.iterrows():
        sid = session['session_id']
        uid = session['user_id']
        user = users[users['user_id'] == uid].iloc[0]
        segment = user['user_segment']
        is_weekend = session['is_weekend']
        hour = session['hour_of_day']
        
        # Segment-based conversion multipliers
        segment_mult = {'New': 0.75, 'Returning': 1.0, 'Power': 1.25}[segment]
        
        # Time-based multiplier (peak hours convert better)
        is_peak = hour in [12, 13, 19, 20, 21]
        time_mult = 1.15 if is_peak else 1.0
        weekend_mult = 1.10 if is_weekend else 1.0
        
        # Record session start
        funnel_events.append({
            'event_id': len(funnel_events) + 1,
            'session_id': sid,
            'user_id': uid,
            'event_type': 'session_start',
            'timestamp': session['session_start'],
            'user_segment': segment,
            'city': user['city'],
            'platform': session['platform']
        })
        
        # ── Stage 1: Search ──────────────────────────────────────────────
        search_prob = min(0.82 * segment_mult * time_mult, 0.95)
        if np.random.random() > search_prob:
            continue  # User bounced without searching
        
        search_id += 1
        cuisine_searched = np.random.choice(CUISINES, p=CUISINE_WEIGHTS)
        
        searches.append({
            'search_id': search_id,
            'session_id': sid,
            'user_id': uid,
            'cuisine_searched': cuisine_searched,
            'timestamp': session['session_start'] + timedelta(seconds=np.random.randint(5, 60))
        })
        
        funnel_events.append({
            'event_id': len(funnel_events) + 1,
            'session_id': sid,
            'user_id': uid,
            'event_type': 'search',
            'timestamp': session['session_start'] + timedelta(seconds=np.random.randint(5, 60)),
            'user_segment': segment,
            'city': user['city'],
            'platform': session['platform']
        })
        
        # ── Stage 2: Restaurant Click ────────────────────────────────────
        # Show 5-10 restaurant impressions
        city_restaurants = restaurants[restaurants['city'] == user['city']]
        if len(city_restaurants) < 3:
            city_restaurants = restaurants.sample(min(8, len(restaurants)))
        
        num_impressions = min(np.random.randint(5, 11), len(city_restaurants))
        shown_restaurants = city_restaurants.sample(num_impressions)
        
        clicked_any = False
        clicked_restaurant = None
        
        for pos, (_, rest) in enumerate(shown_restaurants.iterrows(), 1):
            impression_id += 1
            
            # Click probability based on rating, position, promotion, photos
            base_click_prob = 0.58 * segment_mult
            rating_boost = (rest['rating'] - 3.5) * 0.08
            position_penalty = (pos - 1) * 0.04
            promo_boost = 0.12 if rest['is_promoted'] else 0
            photo_boost = 0.05 if rest['has_photos'] else 0
            
            click_prob = min(max(
                base_click_prob + rating_boost - position_penalty + promo_boost + photo_boost,
                0.05
            ), 0.85)
            
            clicked = np.random.random() < click_prob and not clicked_any
            
            impressions.append({
                'impression_id': impression_id,
                'search_id': search_id,
                'session_id': sid,
                'user_id': uid,
                'restaurant_id': rest['restaurant_id'],
                'position': pos,
                'clicked': clicked,
                'restaurant_rating': rest['rating'],
                'is_promoted': rest['is_promoted'],
                'has_photos': rest['has_photos']
            })
            
            if clicked:
                clicked_any = True
                clicked_restaurant = rest
        
        if not clicked_any:
            continue  # User didn't click any restaurant
        
        funnel_events.append({
            'event_id': len(funnel_events) + 1,
            'session_id': sid,
            'user_id': uid,
            'event_type': 'restaurant_click',
            'timestamp': session['session_start'] + timedelta(seconds=np.random.randint(30, 120)),
            'user_segment': segment,
            'city': user['city'],
            'platform': session['platform']
        })
        
        # ── Stage 3: Add to Cart ─────────────────────────────────────────
        add_cart_prob = 0.38 * segment_mult * time_mult * weekend_mult
        
        # Higher rated restaurants → higher add-to-cart
        if clicked_restaurant['rating'] >= 4.0:
            add_cart_prob *= 1.12
        elif clicked_restaurant['rating'] < 3.0:
            add_cart_prob *= 0.80
        
        if np.random.random() > min(add_cart_prob, 0.70):
            continue  # User browsed menu but didn't add anything
        
        cart_id += 1
        items_count = np.random.choice([1, 2, 3, 4, 5], p=[0.20, 0.35, 0.25, 0.12, 0.08])
        avg_item_price = clicked_restaurant['avg_cost_for_two'] / 2.5
        cart_value = round(items_count * avg_item_price * np.random.uniform(0.7, 1.3), 0)
        
        coupon_applied = np.random.random() < 0.35
        discount = round(cart_value * np.random.uniform(0.10, 0.30), 0) if coupon_applied else 0
        delivery_fee = clicked_restaurant['delivery_fee']
        
        # Free delivery for orders above 199
        if cart_value >= 199 and np.random.random() < 0.4:
            delivery_fee = 0
        
        cart_events.append({
            'cart_id': cart_id,
            'session_id': sid,
            'user_id': uid,
            'restaurant_id': clicked_restaurant['restaurant_id'],
            'items_count': items_count,
            'cart_value': cart_value,
            'coupon_applied': coupon_applied,
            'discount': discount,
            'delivery_fee': delivery_fee,
            'timestamp': session['session_start'] + timedelta(seconds=np.random.randint(120, 300))
        })
        
        funnel_events.append({
            'event_id': len(funnel_events) + 1,
            'session_id': sid,
            'user_id': uid,
            'event_type': 'add_to_cart',
            'timestamp': session['session_start'] + timedelta(seconds=np.random.randint(120, 300)),
            'user_segment': segment,
            'city': user['city'],
            'platform': session['platform']
        })
        
        # ── Stage 4: Checkout Attempt ────────────────────────────────────
        checkout_prob = 0.72 * segment_mult
        
        # Delivery fee impact on checkout
        if delivery_fee >= 49:
            checkout_prob *= 0.70   # High fee → big drop-off
        elif delivery_fee >= 35:
            checkout_prob *= 0.85
        elif delivery_fee == 0:
            checkout_prob *= 1.10   # Free delivery → boost
        
        # Coupon boost
        if coupon_applied:
            checkout_prob *= 1.15
        
        if np.random.random() > min(checkout_prob, 0.95):
            # Record abandonment reason
            cart_events[-1]['abandoned'] = True
            if delivery_fee >= 35:
                cart_events[-1]['abandonment_reason'] = 'High Delivery Fee'
            elif cart_value < 150:
                cart_events[-1]['abandonment_reason'] = 'Low Cart Value'
            else:
                cart_events[-1]['abandonment_reason'] = np.random.choice(
                    ['Changed Mind', 'Found Better Option', 'Price Too High', 'Long Delivery Time'],
                    p=[0.30, 0.25, 0.25, 0.20]
                )
            continue
        
        cart_events[-1]['abandoned'] = False
        cart_events[-1]['abandonment_reason'] = None
        
        funnel_events.append({
            'event_id': len(funnel_events) + 1,
            'session_id': sid,
            'user_id': uid,
            'event_type': 'checkout_attempt',
            'timestamp': session['session_start'] + timedelta(seconds=np.random.randint(300, 420)),
            'user_segment': segment,
            'city': user['city'],
            'platform': session['platform']
        })
        
        # ── Stage 5: Order Placed ────────────────────────────────────────
        order_prob = 0.83 * segment_mult
        
        # Payment failure simulation
        payment_method = np.random.choice(PAYMENT_METHODS, p=PAYMENT_WEIGHTS)
        if payment_method == 'COD':
            order_prob *= 0.95  # Slight penalty
        elif payment_method in ['Credit Card', 'Debit Card']:
            order_prob *= 0.92  # Payment gateway failures
        
        payment_success = np.random.random() < min(order_prob, 0.96)
        
        if not payment_success:
            funnel_events.append({
                'event_id': len(funnel_events) + 1,
                'session_id': sid,
                'user_id': uid,
                'event_type': 'payment_failed',
                'timestamp': session['session_start'] + timedelta(seconds=np.random.randint(420, 480)),
                'user_segment': segment,
                'city': user['city'],
                'platform': session['platform']
            })
            continue
        
        order_id += 1
        final_value = cart_value - discount + delivery_fee
        
        # Delivery time with some variance
        actual_delivery_time = int(np.clip(
            clicked_restaurant['avg_delivery_time_mins'] + np.random.normal(0, 8),
            12, 75
        ))
        
        # Rating: influenced by delivery time and food
        if actual_delivery_time > 50:
            rating_given = np.random.choice([1, 2, 3, 4, 5], p=[0.10, 0.20, 0.35, 0.25, 0.10])
        elif actual_delivery_time > 40:
            rating_given = np.random.choice([1, 2, 3, 4, 5], p=[0.05, 0.10, 0.25, 0.35, 0.25])
        else:
            rating_given = np.random.choice([1, 2, 3, 4, 5], p=[0.02, 0.05, 0.15, 0.38, 0.40])
        
        # Some users don't rate
        if np.random.random() < 0.35:
            rating_given = None
        
        orders.append({
            'order_id': order_id,
            'session_id': sid,
            'user_id': uid,
            'cart_id': cart_id,
            'restaurant_id': clicked_restaurant['restaurant_id'],
            'cuisine': clicked_restaurant['cuisine'],
            'items_count': items_count,
            'cart_value': cart_value,
            'discount': discount,
            'delivery_fee': delivery_fee,
            'final_order_value': final_value,
            'payment_method': payment_method,
            'delivery_time_mins': actual_delivery_time,
            'rating_given': rating_given,
            'coupon_applied': coupon_applied,
            'timestamp': session['session_start'] + timedelta(seconds=np.random.randint(420, 540)),
            'city': user['city']
        })
        
        funnel_events.append({
            'event_id': len(funnel_events) + 1,
            'session_id': sid,
            'user_id': uid,
            'event_type': 'order_placed',
            'timestamp': session['session_start'] + timedelta(seconds=np.random.randint(420, 540)),
            'user_segment': segment,
            'city': user['city'],
            'platform': session['platform']
        })
        
        # Track user orders for reorder analysis
        user_order_count[uid] = user_order_count.get(uid, 0) + 1
    
    return (
        pd.DataFrame(searches),
        pd.DataFrame(impressions),
        pd.DataFrame(cart_events),
        pd.DataFrame(orders),
        pd.DataFrame(funnel_events)
    )


def main():
    print("=" * 60)
    print("  Zomato Funnel — Synthetic Data Generator")
    print("=" * 60)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Generate base tables
    users = generate_users()
    restaurants = generate_restaurants()
    sessions = generate_sessions(users)
    
    # Simulate funnel
    searches, impressions, cart_events, orders, funnel_events = \
        simulate_funnel(sessions, users, restaurants)
    
    # Save all tables
    tables = {
        'users': users,
        'restaurants': restaurants,
        'sessions': sessions,
        'searches': searches,
        'impressions': impressions,
        'cart_events': cart_events,
        'orders': orders,
        'funnel_events': funnel_events
    }
    
    print("\n  Saving data files...")
    for name, df in tables.items():
        path = os.path.join(OUTPUT_DIR, f'{name}.csv')
        df.to_csv(path, index=False)
        print(f"    ✓ {name}.csv — {len(df):,} rows")
    
    # Print summary statistics
    print("\n" + "=" * 60)
    print("  FUNNEL SUMMARY")
    print("=" * 60)
    
    stages = ['session_start', 'search', 'restaurant_click', 'add_to_cart',
              'checkout_attempt', 'order_placed']
    stage_labels = ['Session Start', 'Search', 'Restaurant Click',
                    'Add to Cart', 'Checkout Attempt', 'Order Placed']
    
    prev_count = None
    for stage, label in zip(stages, stage_labels):
        count = len(funnel_events[funnel_events['event_type'] == stage])
        if prev_count:
            conv_rate = count / prev_count * 100
            print(f"    {label:25s} {count:>8,}   ({conv_rate:.1f}% conversion)")
        else:
            print(f"    {label:25s} {count:>8,}")
        prev_count = count
    
    overall = len(funnel_events[funnel_events['event_type'] == 'order_placed']) / \
              len(funnel_events[funnel_events['event_type'] == 'session_start']) * 100
    print(f"\n    Overall Session→Order:  {overall:.2f}%")
    print("=" * 60)
    print("  ✅ Data generation complete!")
    print(f"  📁 Files saved to: {OUTPUT_DIR}")


if __name__ == '__main__':
    main()
