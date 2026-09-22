from math import sqrt

from scipy.stats import norm
from statsmodels.stats.proportion import proportions_ztest


def analyze_binary_experiment(
    treatment_successes,
    treatment_n,
    control_successes,
    control_n,
    alpha=0.05,
):
    """
    Compare two conversion rates using a two-proportion z-test.

    Returns treatment/control rates, absolute lift, relative lift,
    confidence interval, z-statistic, p-value, and significance.
    """

    if treatment_n <= 0 or control_n <= 0:
        raise ValueError(
            "Treatment and control sample sizes must both be greater than zero."
        )

    treatment_rate = treatment_successes / treatment_n
    control_rate = control_successes / control_n

    absolute_lift = treatment_rate - control_rate

    relative_lift = (
        absolute_lift / control_rate
        if control_rate > 0
        else None
    )

    successes = [
        treatment_successes,
        control_successes,
    ]

    observations = [
        treatment_n,
        control_n,
    ]

    z_stat, p_value = proportions_ztest(
        successes,
        observations,
    )

    # Unpooled standard error for confidence interval
    standard_error = sqrt(
        treatment_rate * (1 - treatment_rate) / treatment_n
        +
        control_rate * (1 - control_rate) / control_n
    )

    z_critical = norm.ppf(
        1 - alpha / 2
    )

    ci_lower = (
        absolute_lift
        - z_critical * standard_error
    )

    ci_upper = (
        absolute_lift
        + z_critical * standard_error
    )

    incremental_conversions = (
        absolute_lift * treatment_n
    )

    return {
        "treatment_rate": treatment_rate,
        "control_rate": control_rate,
        "absolute_lift": absolute_lift,
        "relative_lift": relative_lift,
        "incremental_conversions": incremental_conversions,
        "z_stat": z_stat,
        "p_value": p_value,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "significant": bool(p_value < alpha),
        "alpha": alpha,
        "treatment_n": treatment_n,
        "control_n": control_n,
        "total_n": treatment_n + control_n,
    }
