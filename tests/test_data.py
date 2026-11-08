from fx_arbitrage.data import download_data, save_raw_data
import dukascopy_python as dc
import pandas as pd
from datetime import datetime, timezone, timedelta
from unittest.mock import patch
import pytest

def test_download_data():
    data = download_data(
        pair='EUR/USD',
        start_date=datetime(2025, 1, 15, 8, 0, 0, tzinfo=timezone.utc),
        end_date=datetime(2025, 1, 15, 9, 0, 0, tzinfo=timezone.utc)
    )
    assert isinstance(data, pd.DataFrame)

def test_download_data_non_utc_dates():
    with pytest.raises(ValueError):
        download_data(pair='EUR/USD', start_date=datetime(2025, 1, 15, 8, 0, 0, tzinfo=timezone(timedelta(hours=1))),
                                                          end_date=datetime(2025, 1, 16, 9, 0, 0, tzinfo=timezone.utc))

def test_download_data_invalid_date_range():
    with pytest.raises(ValueError):
        download_data(
            pair='EUR/USD',
            start_date=datetime(2025, 1, 15, 8, 0, 0, tzinfo=timezone.utc),
            end_date=datetime(2025, 1, 15, 8, 0, 0, tzinfo=timezone.utc)
        )

def test_download_data_empty_data():
    with patch('dukascopy_python.fetch', return_value=pd.DataFrame()):
        with pytest.raises(ValueError):
            download_data('EUR/USD', datetime(2025, 1, 15, 8, 0, 0, tzinfo=timezone.utc), datetime(2025, 1, 15, 9, 0, 0, tzinfo=timezone.utc))


def test_save_raw_data(tmp_path, monkeypatch):
    raw_data_dir = tmp_path / "data" / "raw"
    monkeypatch.setattr("fx_arbitrage.data.RAW_DATA_DIR", raw_data_dir)
    data = pd.DataFrame(
        {"bid": [1.03, 1.04], "volume": [100, 200]},
        index=pd.date_range("2025-01-15", periods=2, tz="UTC", name="timestamp"),
    )

    save_raw_data(data, "eur_usd")

    output_path = raw_data_dir / "eur_usd_2025-01-15_2025-01-16.parquet"
    assert output_path.is_file()
    pd.testing.assert_frame_equal(pd.read_parquet(output_path), data, check_freq=False)
