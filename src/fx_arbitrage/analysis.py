import pandas as pd

def fresh_quote_mask(quote_ages: pd.DataFrame, max_age_ms: float) -> pd.Series:
    """
    Returns a boolean mask indicating which quotes are fresh based on the maximum age in milliseconds.

    Parameters
    ----------
        quote_ages (pd.DataFrame): A DataFrame containing the ages of quotes.
        max_age_ms (float): The maximum age in milliseconds for a quote to be considered fresh.

    Returns
    -------
        pd.Series: A boolean Series where True indicates a fresh quote and False indicates a stale quote.
    """
    if not isinstance(quote_ages, pd.DataFrame):
        raise TypeError("quote_ages must be a pandas DataFrame.")
    if not isinstance(max_age_ms, (int, float)):
        raise TypeError("max_age_ms must be an integer or float.")
    
    ages = quote_ages.xs('quote_age', level='field', axis=1)
    threshold = pd.Timedelta(milliseconds=max_age_ms)

    return (ages.notna() & ages.ge(pd.Timedelta(0)) & ages.le(threshold)).all(axis=1)


