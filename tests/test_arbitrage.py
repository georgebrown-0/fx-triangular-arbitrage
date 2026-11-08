import pandas as pd
import pytest

from fx_arbitrage.arbitrage import calculate_triangle_returns, summarize_triangle_returns


def test_calculate_triangle_returns():
    event_times = pd.to_datetime(
        [
            "2025-10-06 08:00:00.100",
            "2025-10-06 08:00:00.200",
        ],
        utc=True,
    )

    columns = pd.MultiIndex.from_tuples(
        [
            ("EUR_USD", "bidPrice"),
            ("EUR_USD", "askPrice"),
            ("USD_JPY", "bidPrice"),
            ("USD_JPY", "askPrice"),
            ("EUR_JPY", "bidPrice"),
            ("EUR_JPY", "askPrice"),
        ],
        names=["pair", "field"],
    )

    data = pd.DataFrame(
        [
            [1.10, 1.11, 150.0, 151.0, 164.0, 165.0],
            [1.10, 1.11, 150.0, 151.0, 166.0, 167.0],
        ],
        index=event_times,
        columns=columns,
    )

    result = calculate_triangle_returns(
        data,
        pair_1="EUR_USD",
        pair_2="USD_JPY",
        cross_pair="EUR_JPY",
    )

    expected = pd.DataFrame(
        {
            "pair1_pair2_cross_return": [
                (1.10 * 150.0) / 165.0 - 1,
                (1.10 * 150.0) / 167.0 - 1,
            ],
            "cross_pair2_pair1_return": [
                164.0 / (1.11 * 151.0) - 1,
                166.0 / (1.11 * 151.0) - 1,
            ],
        },
        index=event_times,
    )

    pd.testing.assert_frame_equal(result, expected)

def test_calculate_triangle_returns_does_not_depend_on_column_order():
    event_times = pd.to_datetime(
        ["2025-10-06 08:00:00.100"],
        utc=True,
    )

    columns = pd.MultiIndex.from_tuples(
        [
            ("EUR_JPY", "askPrice"),
            ("USD_JPY", "bidPrice"),
            ("EUR_USD", "askPrice"),
            ("EUR_JPY", "bidPrice"),
            ("EUR_USD", "bidPrice"),
            ("USD_JPY", "askPrice"),
        ],
        names=["pair", "field"],
    )

    data = pd.DataFrame(
        [[165.0, 150.0, 1.11, 164.0, 1.10, 151.0]],
        index=event_times,
        columns=columns,
    )

    result = calculate_triangle_returns(
        data,
        pair_1="EUR_USD",
        pair_2="USD_JPY",
        cross_pair="EUR_JPY",
    )

    expected_forward = (1.10 * 150.0) / 165.0 - 1
    expected_reverse = 164.0 / (1.11 * 151.0) - 1

    assert result.loc[event_times[0], "pair1_pair2_cross_return"] == expected_forward
    assert result.loc[event_times[0], "cross_pair2_pair1_return"] == expected_reverse

def test_summarize_triangle_returns():
    metrics = pd.DataFrame({
        "pair1_pair2_cross_return": [-0.002, 0.001, 0.002, -0.001, 0.003],
        "cross_pair2_pair1_return": [-0.003, -0.002, 0.001, 0.002, -0.001],
    })

    result = summarize_triangle_returns(metrics)

    assert result.loc["n_obs", "pair1_pair2_cross_return"] == 5
    assert result.loc["n_positive", "pair1_pair2_cross_return"] == 3
    assert result.loc["positive_share", "pair1_pair2_cross_return"] == 0.6
    assert result.loc["n_distinct_positive_episodes", "pair1_pair2_cross_return"] == 2
    assert result.loc["max", "pair1_pair2_cross_return"] == pytest.approx(0.003)
    assert result.loc["mean_positive_return", "pair1_pair2_cross_return"] == pytest.approx(0.002)

    assert result.loc["n_positive", "cross_pair2_pair1_return"] == 2
    assert result.loc["positive_share", "cross_pair2_pair1_return"] == 0.4
    assert result.loc["n_distinct_positive_episodes", "cross_pair2_pair1_return"] == 1

def test_return_formulae_negative():
    pairs = ["EUR_USD", "USD_JPY", "EUR_JPY"]
    fields = ["bidPrice", "askPrice"]
    columns = pd.MultiIndex.from_product([pairs, fields], names=["pair", "field"])
    data = pd.DataFrame([[1.1, 1.11, 150, 151, 166, 167]], columns=columns)
    returns = calculate_triangle_returns(data, "EUR_USD", "USD_JPY", "EUR_JPY")
    expected_forward = (1.10 * 150.0) / 167.0 - 1
    expected_reverse = 166.0 / (1.11 * 151.0) - 1
    assert returns['pair1_pair2_cross_return'].iloc[0] == pytest.approx(expected_forward)
    assert returns['cross_pair2_pair1_return'].iloc[0] == pytest.approx(expected_reverse)

def test_return_formulae_positive():
    pairs = ["EUR_USD", "USD_JPY", "EUR_JPY"]
    fields = ["bidPrice", "askPrice"]
    columns = pd.MultiIndex.from_product([pairs, fields], names=["pair", "field"])
    data = pd.DataFrame([[1.1, 1.11, 150, 151, 163, 164]], columns=columns)
    returns = calculate_triangle_returns(data, "EUR_USD", "USD_JPY", "EUR_JPY")
    expected_forward = (1.10 * 150.0) / 164.0 - 1
    expected_reverse = 163.0 / (1.11 * 151.0) - 1
    assert returns['pair1_pair2_cross_return'].iloc[0] == pytest.approx(expected_forward)
    assert returns['cross_pair2_pair1_return'].iloc[0] == pytest.approx(expected_reverse)
