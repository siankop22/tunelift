import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from faker import Faker

from database import engine

fake = Faker()
Faker.seed(42)
random.seed(42)
np.random.seed(42)

NUM_LISTENERS = 10000
NUM_ARTISTS = 100
NUM_TRACKS = 300
NUM_CAMPAIGNS = 30

GENRES = [
    "Pop",
    "Hip-Hop",
    "Rock",
    "R&B",
    "Electronic",
    "Indie",
    "Country",
    "K-Pop",
]

COUNTRIES = [
    "US",
    "UK",
    "Canada",
    "Germany",
    "Brazil",
    "Mexico",
    "South Korea",
    "Japan",
]


def generate_listeners():
    listeners = []

    for listener_id in range(1, NUM_LISTENERS + 1):
        listeners.append(
            {
                "listener_id": listener_id,
                "country": random.choice(COUNTRIES),
                "age": random.randint(18, 55),
                "subscription_type": random.choices(
                    ["free", "premium"],
                    weights=[0.4, 0.6],
                )[0],
                "preferred_genre": random.choice(GENRES),
                "historical_stream_count": int(
                    np.random.lognormal(mean=5, sigma=1)
                ),
            }
        )

    return pd.DataFrame(listeners)


def generate_artists():
    artists = []

    for artist_id in range(1, NUM_ARTISTS + 1):
        artists.append(
            {
                "artist_id": artist_id,
                "artist_name": f"Artist {artist_id}",
                "genre": random.choice(GENRES),
                "monthly_listeners": random.randint(5000, 5000000),
                "follower_count": random.randint(1000, 2000000),
            }
        )

    return pd.DataFrame(artists)


def generate_tracks(artists_df):
    tracks = []

    start_date = datetime(2025, 1, 1)

    for track_id in range(1, NUM_TRACKS + 1):
        artist = artists_df.sample(1).iloc[0]

        tracks.append(
            {
                "track_id": track_id,
                "artist_id": int(artist["artist_id"]),
                "track_name": f"Track {track_id}",
                "genre": artist["genre"],
                "release_date": start_date
                + timedelta(days=random.randint(0, 500)),
                "popularity_score": random.randint(1, 100),
            }
        )

    return pd.DataFrame(tracks)


def generate_campaigns(tracks_df):
    campaigns = []

    campaign_tracks = tracks_df.sample(
        NUM_CAMPAIGNS,
        random_state=42,
    )

    for campaign_id, (_, track) in enumerate(
        campaign_tracks.iterrows(),
        start=1,
    ):
        start_date = datetime(2026, 6, 1) + timedelta(
            days=random.randint(0, 60)
        )

        campaigns.append(
            {
                "campaign_id": campaign_id,
                "track_id": int(track["track_id"]),
                "artist_id": int(track["artist_id"]),
                "start_date": start_date,
                "end_date": start_date + timedelta(days=14),
                "campaign_budget": random.randint(1000, 20000),
                "target_genre": track["genre"],
            }
        )

    return pd.DataFrame(campaigns)


def generate_experiment_events(
    listeners_df,
    tracks_df,
    campaigns_df,
):
    records = []

    impression_id = 1

    for _, campaign in campaigns_df.iterrows():

        track = tracks_df[
            tracks_df["track_id"] == campaign["track_id"]
        ].iloc[0]

        sampled_listeners = listeners_df.sample(
            n=1000,
            random_state=int(campaign["campaign_id"]),
        )

        for _, listener in sampled_listeners.iterrows():

            treatment = random.choice([0, 1])

            genre_match = (
                listener["preferred_genre"] == track["genre"]
            )

            base_stream_probability = 0.18

            if genre_match:
                base_stream_probability += 0.08

            if listener["subscription_type"] == "premium":
                base_stream_probability += 0.02

            if treatment:
                stream_probability = (
                    base_stream_probability + 0.06
                )
            else:
                stream_probability = base_stream_probability

            streamed = int(
                random.random() < stream_probability
            )

            skipped = 0
            saved = 0
            followed_artist = 0
            repeat_stream = 0
            playlist_add = 0

            if streamed:
                skip_probability = 0.25

                if genre_match:
                    skip_probability -= 0.07

                skipped = int(
                    random.random() < skip_probability
                )

                if not skipped:
                    saved = int(
                        random.random()
                        < (0.22 + (0.04 if treatment else 0))
                    )

                    followed_artist = int(
                        random.random()
                        < (0.08 + (0.02 if treatment else 0))
                    )

                    repeat_stream = int(
                        random.random()
                        < (0.18 + (0.03 if treatment else 0))
                    )

                    playlist_add = int(
                        random.random()
                        < (0.12 + (0.02 if treatment else 0))
                    )

            records.append(
                {
                    "impression_id": impression_id,
                    "campaign_id": int(
                        campaign["campaign_id"]
                    ),
                    "listener_id": int(
                        listener["listener_id"]
                    ),
                    "track_id": int(campaign["track_id"]),
                    "treatment_group": (
                        "treatment" if treatment else "control"
                    ),
                    "genre_match": int(genre_match),
                    "streamed": streamed,
                    "skipped": skipped,
                    "saved": saved,
                    "followed_artist": followed_artist,
                    "repeat_stream": repeat_stream,
                    "playlist_add": playlist_add,
                }
            )

            impression_id += 1

    return pd.DataFrame(records)


def save_table(df, table_name):
    df.to_sql(
        table_name,
        engine,
        if_exists="replace",
        index=False,
    )

    df.to_csv(
        f"data/generated/{table_name}.csv",
        index=False,
    )

    print(
        f"Saved {table_name}: {len(df):,} rows"
    )


def main():
    listeners_df = generate_listeners()

    artists_df = generate_artists()

    tracks_df = generate_tracks(artists_df)

    campaigns_df = generate_campaigns(tracks_df)

    experiment_df = generate_experiment_events(
        listeners_df,
        tracks_df,
        campaigns_df,
    )

    save_table(listeners_df, "listeners")
    save_table(artists_df, "artists")
    save_table(tracks_df, "tracks")
    save_table(campaigns_df, "campaigns")
    save_table(experiment_df, "experiment_events")

    print()
    print("TuneLift synthetic dataset generated.")
    print()

    print(
        experiment_df[
            [
                "treatment_group",
                "streamed",
                "saved",
                "followed_artist",
            ]
        ]
        .groupby("treatment_group")
        .mean()
        .round(4)
    )


if __name__ == "__main__":
    main()
