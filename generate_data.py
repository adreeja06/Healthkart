import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta

# Initialize Faker and seed for reproducibility
fake = Faker()
Faker.seed(42)
np.random.seed(42)
random.seed(42)

# --- 1. Generate Influencers Data ---
influencer_count = 50
influencers_data = []
for i in range(1, influencer_count + 1):
    category = random.choice(['Fitness', 'Wellness', 'Nutrition', 'Bodybuilding', 'Yoga'])
    platform = random.choice(['Instagram', 'YouTube'])
    followers = random.randint(5000, 500000) if category != 'Bodybuilding' else random.randint(100000, 1000000)
    influencers_data.append({
        'influencer_id': i,
        'name': fake.name(),
        'category': category,
        'gender': random.choice(['Male', 'Female']),
        'follower_count': followers,
        'platform': platform
    })
influencers_df = pd.DataFrame(influencers_data)

# --- 2. Generate Posts Data ---
posts_data = []
post_id_counter = 1
for _, influencer in influencers_df.iterrows():
    num_posts = random.randint(2, 8)
    for _ in range(num_posts):
        post_date = fake.date_time_between(start_date='-6M', end_date='now')
        reach = int(influencer['follower_count'] * random.uniform(0.1, 0.75))
        likes = int(reach * random.uniform(0.02, 0.15))
        comments = int(likes * random.uniform(0.01, 0.05))
        posts_data.append({
            'post_id': post_id_counter,
            'influencer_id': influencer['influencer_id'],
            'platform': influencer['platform'],
            'post_date': post_date,
            'post_url': f"http://{influencer['platform'].lower()}.com/post/{post_id_counter}",
            'caption': fake.sentence(nb_words=15),
            'reach': reach,
            'likes': likes,
            'comments': comments
        })
        post_id_counter += 1
posts_df = pd.DataFrame(posts_data)

# --- 3. Generate Tracking Data ---
tracking_data = []
tracking_id_counter = 1
products = {
    'MB_Whey_Launch': {'id': 'P001', 'price': 4000},
    'HKVitals_Skin_Radiance': {'id': 'P002', 'price': 1200},
    'Gritzo_SuperMilk': {'id': 'P003', 'price': 800},
    'MB_PreWorkout': {'id': 'P004', 'price': 2500}
}
campaigns = list(products.keys())

for _, post in posts_df.iterrows():
    if random.random() < 0.7: # 70% chance a post generates some orders
        num_tracked_events = random.randint(5, int(post['likes'] * 0.05) + 5)
        for _ in range(num_tracked_events):
            campaign_name = random.choice(campaigns)
            product_info = products[campaign_name]
            orders = random.randint(1, 3)
            tracking_data.append({
                'tracking_id': tracking_id_counter,
                'source': 'influencer',
                'campaign': campaign_name,
                'influencer_id': post['influencer_id'],
                'user_id': fake.uuid4(),
                'product_id': product_info['id'],
                'order_date': post['post_date'] + timedelta(days=random.randint(0, 7)),
                'orders': orders,
                'revenue': orders * product_info['price'] * random.uniform(0.9, 1.1)
            })
            tracking_id_counter += 1
tracking_df = pd.DataFrame(tracking_data)

# --- 4. Generate Payouts Data ---
payouts_data = []
payout_id_counter = 1
for _, influencer in influencers_df.iterrows():
    basis = random.choice(['per_post', 'per_order'])
    rate = random.randint(5000, 50000) if basis == 'per_post' else random.uniform(100, 500)
    payouts_data.append({ 'payout_id': payout_id_counter, 'influencer_id': influencer['influencer_id'], 'basis': basis, 'rate': round(rate, 2) })
    payout_id_counter += 1
payouts_df = pd.DataFrame(payouts_data)

# --- Save to CSV ---
influencers_df.to_csv('influencers.csv', index=False)
posts_df.to_csv('posts.csv', index=False)
tracking_df.to_csv('tracking_data.csv', index=False)
payouts_df.to_csv('payouts.csv', index=False)

print("✅ Fresh data generation complete. 4 new CSV files have been created.")