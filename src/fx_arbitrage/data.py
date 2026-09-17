import dukascopy_python as dc
import pandas as pd
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


def download_data(pair: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
    """
    Downloads data from Dukascopy Python for a given pair and date range.

    Parameters
    ----------
        pair (str): The currency pair to download data for, e.g. 'EUR/USD'.
        start_date (datetime): The start date for the data download.
        end_date (datetime): The end date for the data download.

    Returns
    -------
        pd.DataFrame: The downloaded data.
    """
    if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):
        raise TypeError("start_date and end_date must be datetime objects.")
    if start_date.tzinfo != timezone.utc or end_date.tzinfo != timezone.utc:
        raise ValueError("start_date and end_date must use UTC timezone")
    if start_date >= end_date:
        raise ValueError("Start date must be before end date.")
    
    data = dc.fetch(
        instrument=pair,
        interval=dc.INTERVAL_TICK,
        offer_side=dc.OFFER_SIDE_BID,
        start=start_date,
        end=end_date
    )
    if data.empty:
        raise ValueError(f"No data returned for {pair} between {start_date} and {end_date}.")
    return data

def save_raw_data(data: pd.DataFrame, name: str) -> None:
    '''
    Saves raw data to a parquet file in the project's data/raw directory.
    
    Parameters
    ----------
        data (pd.DataFrame): The data to save.
        name (str): The name of the file to save.
    '''
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    data.to_parquet(RAW_DATA_DIR / f"{name}.parquet")
