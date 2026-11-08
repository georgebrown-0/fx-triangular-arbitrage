from fx_arbitrage.alignment import align_quotes, calculate_quote_ages
import pandas as pd
import pytest

def test_align_quotes():
    times_1 = pd.to_datetime(
        [
            1759708800049,
            1759708800153,
            1759708800205,
            1759708800308,
            1759708800411,
        ],
        unit="ms",
        utc=True,
    )

    times_2 = pd.to_datetime(
        [
            1759708800134,
            1759708800248,
            1759708800404,
            1759708801706,
            1759708802372,
        ],
        unit="ms",
        utc=True,
    )

    times_3 = pd.to_datetime(
        [
            1759708800088,
            1759708800202,
            1759708800254,
            1759708800308,
            1759708800360,
        ],
        unit="ms",
        utc=True,
    )

    data_1 = pd.DataFrame(
        {
            "bidPrice": [175.186, 175.183, 175.183, 175.179, 175.177],
            "askPrice": [175.196, 175.188, 175.194, 175.194, 175.190],
        },
        index=times_1,
    )

    data_2 = pd.DataFrame(
        {
            "bidPrice": [1.17121, 1.17122, 1.17120, 1.17120, 1.17121],
            "askPrice": [1.17124, 1.17124, 1.17123, 1.17125, 1.17125],
        },
        index=times_2,
    )

    data_3 = pd.DataFrame(
        {
            "bidPrice": [149.580, 149.577, 149.572, 149.572, 149.568],
            "askPrice": [149.590, 149.587, 149.587, 149.582, 149.578],
        },
        index=times_3,
    )

    for data in [data_1, data_2, data_3]:
        data.index.name = "timestamp"

    result = align_quotes(
        ("data_1", data_1),
        ("data_2", data_2),
        ("data_3", data_3),
    )
    event_times = pd.to_datetime(
        [
            1759708800134,
            1759708800153,
            1759708800202,
            1759708800205,
            1759708800248,
            1759708800254,
            1759708800308,
            1759708800360,
            1759708800404,
            1759708800411,
            1759708801706,
            1759708802372,
        ],
        unit="ms",
        utc=True,
    )
    event_times.name = "event_time"

    expected = pd.DataFrame(
        {
            # ---------------- data_1 ----------------
            ("data_1", "quote_time"): [
                times_1[0], times_1[1], times_1[1], times_1[2],
                times_1[2], times_1[2], times_1[3], times_1[3],
                times_1[3], times_1[4], times_1[4], times_1[4],
            ],
            ("data_1", "bidPrice"): [
                175.186, 175.183, 175.183, 175.183,
                175.183, 175.183, 175.179, 175.179,
                175.179, 175.177, 175.177, 175.177,
            ],
            ("data_1", "askPrice"): [
                175.196, 175.188, 175.188, 175.194,
                175.194, 175.194, 175.194, 175.194,
                175.194, 175.190, 175.190, 175.190,
            ],
            ("data_1", "bid_change_time"): [
                pd.NaT, times_1[1], times_1[1], times_1[1],
                times_1[1], times_1[1], times_1[3], times_1[3],
                times_1[3], times_1[4], times_1[4], times_1[4],
            ],
            ("data_1", "ask_change_time"): [
                pd.NaT, times_1[1], times_1[1], times_1[2],
                times_1[2], times_1[2], times_1[2], times_1[2],
                times_1[2], times_1[4], times_1[4], times_1[4],
            ],

            # ---------------- data_2 ----------------
            ("data_2", "quote_time"): [
                times_2[0], times_2[0], times_2[0], times_2[0],
                times_2[1], times_2[1], times_2[1], times_2[1],
                times_2[2], times_2[2], times_2[3], times_2[4],
            ],
            ("data_2", "bidPrice"): [
                1.17121, 1.17121, 1.17121, 1.17121,
                1.17122, 1.17122, 1.17122, 1.17122,
                1.17120, 1.17120, 1.17120, 1.17121,
            ],
            ("data_2", "askPrice"): [
                1.17124, 1.17124, 1.17124, 1.17124,
                1.17124, 1.17124, 1.17124, 1.17124,
                1.17123, 1.17123, 1.17125, 1.17125,
            ],
            ("data_2", "bid_change_time"): [
                pd.NaT, pd.NaT, pd.NaT, pd.NaT,
                times_2[1], times_2[1], times_2[1], times_2[1],
                times_2[2], times_2[2], times_2[2], times_2[4],
            ],
            ("data_2", "ask_change_time"): [
                pd.NaT, pd.NaT, pd.NaT, pd.NaT,
                pd.NaT, pd.NaT, pd.NaT, pd.NaT,
                times_2[2], times_2[2], times_2[3], times_2[3],
            ],

            # ---------------- data_3 ----------------
            ("data_3", "quote_time"): [
                times_3[0], times_3[0], times_3[1], times_3[1],
                times_3[1], times_3[2], times_3[3], times_3[4],
                times_3[4], times_3[4], times_3[4], times_3[4],
            ],
            ("data_3", "bidPrice"): [
                149.580, 149.580, 149.577, 149.577,
                149.577, 149.572, 149.572, 149.568,
                149.568, 149.568, 149.568, 149.568,
            ],
            ("data_3", "askPrice"): [
                149.590, 149.590, 149.587, 149.587,
                149.587, 149.587, 149.582, 149.578,
                149.578, 149.578, 149.578, 149.578,
            ],
            ("data_3", "bid_change_time"): [
                pd.NaT, pd.NaT, times_3[1], times_3[1],
                times_3[1], times_3[2], times_3[2], times_3[4],
                times_3[4], times_3[4], times_3[4], times_3[4],
            ],
            ("data_3", "ask_change_time"): [
                pd.NaT, pd.NaT, times_3[1], times_3[1],
                times_3[1], times_3[1], times_3[3], times_3[4],
                times_3[4], times_3[4], times_3[4], times_3[4],
            ],
        },
        index=event_times,
    )

    expected.columns.names = ["pair", "field"]

    # Match the exact column ordering produced by align_quotes()
    expected = expected.reindex(columns=result.columns)
    

    pd.testing.assert_frame_equal(result, expected)
    



def test_calculate_quote_ages():
    event_times = pd.to_datetime(
        [
            "2025-10-06 08:00:00.100",
            "2025-10-06 08:00:00.200",
            "2025-10-06 08:00:00.300",
        ],
        utc=True,
    )
    event_times.name = "event_time"

    columns = pd.MultiIndex.from_tuples(
        [
            ("EUR_USD", "quote_time"),
            ("EUR_USD", "bid_change_time"),
            ("EUR_USD", "ask_change_time"),
            ("USD_JPY", "quote_time"),
            ("USD_JPY", "bid_change_time"),
            ("USD_JPY", "ask_change_time"),
        ],
        names=["pair", "field"],
    )

    aligned_data = pd.DataFrame(
        [
            [
                event_times[0], event_times[0], event_times[0],
                event_times[0], event_times[0], event_times[0],
            ],
            [
                event_times[1], event_times[0], event_times[1],
                event_times[0], event_times[0], event_times[0],
            ],
            [
                event_times[1], event_times[0], event_times[1],
                event_times[2], event_times[2], event_times[0],
            ],
        ],
        index=event_times,
        columns=columns,
    )

    result = calculate_quote_ages(aligned_data)

    expected_columns = pd.MultiIndex.from_product(
        [
            ["EUR_USD", "USD_JPY"],
            ["quote_age", "bid_age", "ask_age"],
        ],
        names=["pair", "field"],
    )

    expected = pd.DataFrame(
        [
            [
                pd.Timedelta(milliseconds=0),
                pd.Timedelta(milliseconds=0),
                pd.Timedelta(milliseconds=0),
                pd.Timedelta(milliseconds=0),
                pd.Timedelta(milliseconds=0),
                pd.Timedelta(milliseconds=0),
            ],
            [
                pd.Timedelta(milliseconds=0),
                pd.Timedelta(milliseconds=100),
                pd.Timedelta(milliseconds=0),
                pd.Timedelta(milliseconds=100),
                pd.Timedelta(milliseconds=100),
                pd.Timedelta(milliseconds=100),
            ],
            [
                pd.Timedelta(milliseconds=100),
                pd.Timedelta(milliseconds=200),
                pd.Timedelta(milliseconds=100),
                pd.Timedelta(milliseconds=0),
                pd.Timedelta(milliseconds=0),
                pd.Timedelta(milliseconds=200),
            ],
        ],
        index=event_times,
        columns=expected_columns,
    )

    pd.testing.assert_frame_equal(result, expected)


def test_calculate_quote_ages_preserves_unknown_change_times():
    event_times = pd.to_datetime(
        [
            "2025-10-06 08:00:00.100",
            "2025-10-06 08:00:00.200",
        ],
        utc=True,
    )
    event_times.name = "event_time"

    columns = pd.MultiIndex.from_tuples(
        [
            ("EUR_USD", "quote_time"),
            ("EUR_USD", "bid_change_time"),
            ("EUR_USD", "ask_change_time"),
        ],
        names=["pair", "field"],
    )

    aligned_data = pd.DataFrame(
        [
            [event_times[0], pd.NaT, pd.NaT],
            [event_times[1], pd.NaT, event_times[1]],
        ],
        index=event_times,
        columns=columns,
    )
    aligned_data[("EUR_USD", "bid_change_time")] = pd.Series(
    pd.array([pd.NaT, pd.NaT], dtype="datetime64[ms, UTC]"),
    index=event_times,
    )

    result = calculate_quote_ages(aligned_data)

    assert pd.isna(result.loc[event_times[0], ("EUR_USD", "bid_age")])
    assert pd.isna(result.loc[event_times[0], ("EUR_USD", "ask_age")])
    assert pd.isna(result.loc[event_times[1], ("EUR_USD", "bid_age")])

    assert (
        result.loc[event_times[1], ("EUR_USD", "ask_age")]
        == pd.Timedelta(0)
    )


def test_calculate_quote_ages_rejects_negative_age():
    event_times = pd.to_datetime(
        ["2025-10-06 08:00:00.100"],
        utc=True,
    )
    event_times.name = "event_time"

    future_time = pd.Timestamp(
        "2025-10-06 08:00:00.200",
        tz="UTC",
    )

    columns = pd.MultiIndex.from_tuples(
        [
            ("EUR_USD", "quote_time"),
            ("EUR_USD", "bid_change_time"),
            ("EUR_USD", "ask_change_time"),
        ],
        names=["pair", "field"],
    )

    aligned_data = pd.DataFrame(
        [
            [
                future_time,
                event_times[0],
                event_times[0],
            ]
        ],
        index=event_times,
        columns=columns,
    )

    with pytest.raises(ValueError, match="Negative ages found"):
        calculate_quote_ages(aligned_data)