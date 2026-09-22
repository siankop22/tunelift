import pandas as pd


RETENTION_COLUMNS = {
    "7 Day": "returned_7d",
    "14 Day": "returned_14d",
    "30 Day": "returned_30d",
}


def calculate_retention(df):
    """
    Calculate retention among listeners who streamed the track.
    """

    streamed = df[
        df["streamed"] == 1
    ].copy()

    rows = []

    for period, column in RETENTION_COLUMNS.items():

        for group in [
            "control",
            "treatment",
        ]:
            subset = streamed[
                streamed["treatment_group"] == group
            ]

            rate = (
                subset[column].mean()
                if len(subset) > 0
                else 0
            )

            rows.append(
                {
                    "period": period,
                    "treatment_group": group,
                    "retention_rate": rate,
                    "listeners": len(subset),
                }
            )

    return pd.DataFrame(rows)


def calculate_retention_lift(df):
    retention = calculate_retention(df)

    pivot = retention.pivot(
        index="period",
        columns="treatment_group",
        values="retention_rate",
    ).reset_index()

    if (
        "treatment" in pivot.columns
        and "control" in pivot.columns
    ):
        pivot["absolute_lift"] = (
            pivot["treatment"]
            - pivot["control"]
        )

        pivot["relative_lift"] = (
            pivot["absolute_lift"]
            / pivot["control"].replace(0, pd.NA)
        )

    return pivot
