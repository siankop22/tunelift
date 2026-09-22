from scipy.stats import chisquare
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize


def sample_ratio_mismatch(treatment_n, control_n):
    """
    Tests whether assignment differs materially from the expected 50/50 split.
    """
    total = treatment_n + control_n

    if total == 0:
        raise ValueError("Experiment must contain observations.")

    expected = [total / 2, total / 2]
    observed = [treatment_n, control_n]

    chi2, p_value = chisquare(
        f_obs=observed,
        f_exp=expected,
    )

    return {
        "chi2": chi2,
        "p_value": p_value,
        "has_srm": p_value < 0.05,
    }


def experiment_power(
    treatment_rate,
    control_rate,
    treatment_n,
    control_n,
    alpha=0.05,
):
    """
    Approximate achieved statistical power for a two-proportion experiment.
    """

    effect_size = proportion_effectsize(
        treatment_rate,
        control_rate,
    )

    ratio = control_n / treatment_n

    analysis = NormalIndPower()

    power = analysis.power(
        effect_size=effect_size,
        nobs1=treatment_n,
        alpha=alpha,
        ratio=ratio,
        alternative="two-sided",
    )

    return power


def minimum_detectable_effect(
    baseline_rate,
    n_per_group,
    alpha=0.05,
    target_power=0.80,
):
    """
    Approximate minimum detectable absolute effect.
    """

    analysis = NormalIndPower()

    effect_size = analysis.solve_power(
        effect_size=None,
        nobs1=n_per_group,
        alpha=alpha,
        power=target_power,
        ratio=1.0,
        alternative="two-sided",
    )

    low = baseline_rate

    # Convert Cohen's h back to a second probability.
    from math import asin, sin, sqrt

    transformed = (
        effect_size
        + 2 * asin(sqrt(low))
    ) / 2

    detectable_rate = sin(transformed) ** 2

    return detectable_rate - baseline_rate
