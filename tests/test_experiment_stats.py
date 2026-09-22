from src.experiment_stats import analyze_binary_experiment


def test_positive_treatment_lift():
    result = analyze_binary_experiment(
        treatment_successes=300,
        treatment_n=1000,
        control_successes=200,
        control_n=1000,
    )

    assert result["treatment_rate"] == 0.30
    assert result["control_rate"] == 0.20
    assert round(result["absolute_lift"], 2) == 0.10
    assert round(result["relative_lift"], 2) == 0.50
    assert result["significant"] is True


def test_no_difference():
    result = analyze_binary_experiment(
        treatment_successes=200,
        treatment_n=1000,
        control_successes=200,
        control_n=1000,
    )

    assert result["absolute_lift"] == 0
    assert result["significant"] is False
    assert result["ci_lower"] <= 0 <= result["ci_upper"]
