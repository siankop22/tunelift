from statsmodels.stats.proportion import proportions_ztest


def compare_rate(
    treatment_successes,
    treatment_n,
    control_successes,
    control_n,
):
    if treatment_n <= 0 or control_n <= 0:
        return {
            "treatment_rate": 0.0,
            "control_rate": 0.0,
            "absolute_change": 0.0,
            "p_value": 1.0,
            "significant": False,
        }

    treatment_rate = treatment_successes / treatment_n
    control_rate = control_successes / control_n

    z_stat, p_value = proportions_ztest(
        [
            treatment_successes,
            control_successes,
        ],
        [
            treatment_n,
            control_n,
        ],
    )

    return {
        "treatment_rate": treatment_rate,
        "control_rate": control_rate,
        "absolute_change": (
            treatment_rate - control_rate
        ),
        "z_stat": z_stat,
        "p_value": p_value,
        "significant": p_value < 0.05,
    }


def analyze_guardrails(df):
    treatment = df[
        df["treatment_group"] == "treatment"
    ]

    control = df[
        df["treatment_group"] == "control"
    ]

    treatment_streams = treatment[
        treatment["streamed"] == 1
    ]

    control_streams = control[
        control["streamed"] == 1
    ]

    metrics = {
        "Skip Rate": "skipped",
        "Save Rate": "saved",
        "Repeat Listening": "repeat_stream",
        "Artist Follow Rate": "followed_artist",
        "Playlist Add Rate": "playlist_add",
    }

    results = {}

    for label, column in metrics.items():
        results[label] = compare_rate(
            treatment_successes=int(
                treatment_streams[column].sum()
            ),
            treatment_n=len(treatment_streams),
            control_successes=int(
                control_streams[column].sum()
            ),
            control_n=len(control_streams),
        )

    return results
