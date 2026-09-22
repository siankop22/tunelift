def conversion_rate(successes, impressions):
    if impressions == 0:
        return 0.0

    return successes / impressions


def absolute_lift(treatment_rate, control_rate):
    return treatment_rate - control_rate


def relative_lift(treatment_rate, control_rate):
    if control_rate == 0:
        return 0.0

    return (
        treatment_rate - control_rate
    ) / control_rate


def incremental_conversions(
    treatment_rate,
    control_rate,
    treatment_impressions,
):
    lift = treatment_rate - control_rate

    return lift * treatment_impressions
