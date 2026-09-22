import random

import numpy as np
import pandas as pd
from faker import Faker

from database import engine

fake = Faker()
Faker.seed(42)
random.seed(42)
np.random.seed(42)

NUM_LISTENERS = 10000

genres = [
    "Pop",
    "Hip-Hop",
    "Rock",
    "R&B",
    "Electronic",
    "Indie",
    "Country",
    "K-Pop",
]

countries = [
    "US",
    "UK",
    "Canada",
    "Germany",
    "Brazil",
    "Mexico",
    "South Korea",
    "Japan",
]

subscription_types = ["free", "premium"]

listeners = []

for listener_id in range(1, NUM_LISTENERS + 1):
    listeners.append(
        {
            "listener_id": listener_id,
            "country": random.choice(countries),
            "age": random.randint(18, 55),
            "subscription_type": random.choices(
                subscription_types,
                weights=[0.4, 0.6],
            )[0],
            "preferred_genre": random.choice(genres),
            "historical_stream_count": int(
                np.random.lognormal(mean=5, sigma=1)
            ),
        }
    )

df = pd.DataFrame(listeners)

df.to_csv(
    "data/generated/listeners.csv",
    index=False,
)

df.to_sql(
    "listeners",
    engine,
    if_exists="replace",
    index=False,
)

print(df.head())
print()
print(f"Generated {len(df):,} listeners.")
print("Saved listeners to PostgreSQL.")
