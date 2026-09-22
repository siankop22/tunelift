import pandas as pd

from src.retention import (
    calculate_retention,
    calculate_retention_lift,
)


def test_retention_calculation():
    df = pd.DataFrame(
        {
            "treatment_group": [
                "treatment",
                "treatment",
                "control",
                "control",
            ],
            "streamed": [1, 1, 1, 1],
            "returned_7d": [1, 1, 1, 0],
            "returned_14d": [1, 0, 0, 0],
            "returned_30d": [1, 0, 0, 0],
        }
    )

    result = calculate_retention_lift(df)

    seven_day = result[
        result["period"] == "7 Day"
    ].iloc[0]

    assert seven_day["treatment"] == 1.0
    assert seven_day["control"] == 0.5
    assert seven_day["absolute_lift"] == 0.5
