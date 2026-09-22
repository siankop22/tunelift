import pandas as pd
from scipy.stats import norm
from statsmodels.stats.proportion import proportions_ztest

from database import engine


def load_data():
    query = """
    SELECT *
    FROM experiment_events
    """

    return pd.read_sql(query, engine)


def summarize_experiment(df):
    summary = (
        df.groupby("treatment_group")
        .agg(
            impressions=("listener_id", "count"),
            streams=("streamed", "sum"),
            saves=("saved", "sum"),
            follows=("followed_artist", "sum"),
            repeat_streams=("repeat_stream", "sum"),
            skips=("skipped", "sum"),
        )
    )

    summary["stream_rate"] = (
        summary["streams"] / summary["impressions"]
    )

    summary["save_rate"] = (
        summary["saves"] / summary["impressions"]
    )

    summary["follow_rate"] = (
        summary["follows"] / summary["impressions"]
    )

    summary["repeat_rate"] = (
        summary["repeat_streams"]
        / summary["impressions"]
    )

    return summary


def stream_z_test(df):
    treatment = df[
        df["treatment_group"] == "treatment"
    ]

    control = df[
        df["treatment_group"] == "control"
    ]

    successes = [
        treatment["streamed"].sum(),
        control["streamed"].sum(),
    ]

    observations = [
        len(treatment),
        len(control),
    ]

    z_stat, p_value = proportions_ztest(
        successes,
        observations,
    )

    treatment_rate = treatment["streamed"].mean()
    control_rate = control["streamed"].mean()

    absolute_lift = (
        treatment_rate - control_rate
    )

    relative_lift = (
        absolute_lift / control_rate
    )

    return {
        "treatment_rate": treatment_rate,
        "control_rate": control_rate,
        "absolute_lift": absolute_lift,
        "relative_lift": relative_lift,
        "z_stat": z_stat,
        "p_value": p_value,
    }


def confidence_interval(
    treatment_rate,
    control_rate,
    treatment_n,
    control_n,
):
    standard_error = (
        treatment_rate
        * (1 - treatment_rate)
        / treatment_n
        +
        control_rate
        * (1 - control_rate)
        / control_n
    ) ** 0.5

    difference = (
        treatment_rate - control_rate
    )

    z = norm.ppf(0.975)

    lower = difference - z * standard_error
    upper = difference + z * standard_error

    return lower, upper


def main():
    df = load_data()

    summary = summarize_experiment(df)

    print("\nEXPERIMENT SUMMARY")
    print("==================")
    print(summary.round(4))

    results = stream_z_test(df)

    treatment_n = len(
        df[df["treatment_group"] == "treatment"]
    )

    control_n = len(
        df[df["treatment_group"] == "control"]
    )

    lower, upper = confidence_interval(
        results["treatment_rate"],
        results["control_rate"],
        treatment_n,
        control_n,
    )

    print("\nSTREAM CONVERSION EXPERIMENT")
    print("============================")

    print(
        f"Treatment conversion: "
        f"{results['treatment_rate']:.2%}"
    )

    print(
        f"Control conversion:   "
        f"{results['control_rate']:.2%}"
    )

    print(
        f"Absolute lift:        "
        f"{results['absolute_lift']:.2%}"
    )

    print(
        f"Relative lift:        "
        f"{results['relative_lift']:.2%}"
    )

    print(
        f"95% CI:               "
        f"[{lower:.2%}, {upper:.2%}]"
    )

    print(
        f"Z-statistic:          "
        f"{results['z_stat']:.4f}"
    )

    print(
        f"P-value:              "
        f"{results['p_value']:.6f}"
    )

    if results["p_value"] < 0.05:
        print(
            "\nResult: statistically significant."
        )
    else:
        print(
            "\nResult: not statistically significant."
        )


if __name__ == "__main__":
    main()
