import pandas as pd

from database import engine


QUERY = """
SELECT
    e.listener_id,
    e.treatment_group,
    e.streamed,
    e.saved,
    e.followed_artist,
    e.repeat_stream,
    e.genre_match,
    l.country,
    l.subscription_type,
    l.preferred_genre,
    l.age
FROM experiment_events e
JOIN listeners l
    ON e.listener_id = l.listener_id
"""


def calculate_lift(group):
    treatment = group[
        group["treatment_group"] == "treatment"
    ]

    control = group[
        group["treatment_group"] == "control"
    ]

    if len(treatment) == 0 or len(control) == 0:
        return pd.Series(
            {
                "treatment_rate": None,
                "control_rate": None,
                "absolute_lift": None,
                "relative_lift": None,
            }
        )

    treatment_rate = treatment["streamed"].mean()
    control_rate = control["streamed"].mean()

    absolute_lift = (
        treatment_rate - control_rate
    )

    relative_lift = (
        absolute_lift / control_rate
        if control_rate > 0
        else None
    )

    return pd.Series(
        {
            "treatment_rate": treatment_rate,
            "control_rate": control_rate,
            "absolute_lift": absolute_lift,
            "relative_lift": relative_lift,
        }
    )


def main():
    df = pd.read_sql(QUERY, engine)

    print("\nLIFT BY GENRE")
    print("=============")

    genre_results = (
        df.groupby("preferred_genre")
        .apply(
            calculate_lift,
            include_groups=False,
        )
        .sort_values(
            "absolute_lift",
            ascending=False,
        )
    )

    print(
        genre_results.round(4)
    )

    print("\nLIFT BY SUBSCRIPTION TYPE")
    print("=========================")

    subscription_results = (
        df.groupby("subscription_type")
        .apply(
            calculate_lift,
            include_groups=False,
        )
    )

    print(
        subscription_results.round(4)
    )

    print("\nGENRE MATCH")
    print("===========")

    genre_match_results = (
        df.groupby("genre_match")
        .apply(
            calculate_lift,
            include_groups=False,
        )
    )

    print(
        genre_match_results.round(4)
    )


if __name__ == "__main__":
    main()
