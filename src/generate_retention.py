import random

import pandas as pd

from database import engine

random.seed(42)


def retention_probability(row, horizon):
    """
    Simulated probability that a listener is active again
    at a future retention checkpoint.
    """

    if row["streamed"] != 1:
        return 0.0

    base = {
        7: 0.28,
        14: 0.20,
        30: 0.13,
    }[horizon]

    # Listeners showing deeper engagement are more likely to return.
    if row["saved"] == 1:
        base += 0.10

    if row["repeat_stream"] == 1:
        base += 0.12

    if row["followed_artist"] == 1:
        base += 0.08

    if row["playlist_add"] == 1:
        base += 0.08

    # Simulated promotion effect on longer-term retention.
    if row["treatment_group"] == "treatment":
        boost = {
            7: 0.035,
            14: 0.025,
            30: 0.015,
        }[horizon]

        base += boost

    return min(base, 0.95)


def main():
    events = pd.read_sql(
        """
        SELECT
            impression_id,
            campaign_id,
            listener_id,
            track_id,
            treatment_group,
            streamed,
            saved,
            repeat_stream,
            followed_artist,
            playlist_add
        FROM experiment_events
        """,
        engine,
    )

    rows = []

    for _, row in events.iterrows():
        p7 = retention_probability(row, 7)
        p14 = retention_probability(row, 14)
        p30 = retention_probability(row, 30)

        rows.append(
            {
                "impression_id": int(row["impression_id"]),
                "campaign_id": int(row["campaign_id"]),
                "listener_id": int(row["listener_id"]),
                "track_id": int(row["track_id"]),
                "treatment_group": row["treatment_group"],
                "returned_7d": int(random.random() < p7),
                "returned_14d": int(random.random() < p14),
                "returned_30d": int(random.random() < p30),
            }
        )

    retention = pd.DataFrame(rows)

    retention.to_sql(
        "retention_events",
        engine,
        if_exists="replace",
        index=False,
    )

    retention.to_csv(
        "data/generated/retention_events.csv",
        index=False,
    )

    print(f"Created {len(retention):,} retention records.")
    print()
    print(
        retention.groupby("treatment_group")[
            [
                "returned_7d",
                "returned_14d",
                "returned_30d",
            ]
        ]
        .mean()
        .round(4)
    )


if __name__ == "__main__":
    main()
