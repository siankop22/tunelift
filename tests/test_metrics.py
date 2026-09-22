from src.metrics import (
    absolute_lift,
    conversion_rate,
    incremental_conversions,
    relative_lift,
)


def test_conversion_rate():
    assert conversion_rate(
        250,
        1000,
    ) == 0.25


def test_zero_impressions():
    assert conversion_rate(
        0,
        0,
    ) == 0.0


def test_absolute_lift():
    result = absolute_lift(
        0.30,
        0.20,
    )

    assert round(result, 2) == 0.10


def test_relative_lift():
    result = relative_lift(
        0.30,
        0.20,
    )

    assert round(result, 2) == 0.50


def test_incremental_conversions():
    result = incremental_conversions(
        treatment_rate=0.30,
        control_rate=0.20,
        treatment_impressions=1000,
    )

    assert round(result) == 100
