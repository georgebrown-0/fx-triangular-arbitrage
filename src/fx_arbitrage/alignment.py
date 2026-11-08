import pandas as pd

def align_quotes(source_1, source_2, source_3):
    '''
    Aligns quotes from three different data sources.
    Parameters
    ----------
        source_1 (tuple): A tuple containing the name of the first data source and the data source itself.
        source_2 (tuple): A tuple containing the name of the second data source and the data source itself.
        source_3 (tuple): A tuple containing the name of the third data source and the data source itself.

    Returns
    -------
        pd.DataFrame: The aligned data.
            Each row is the most recent quote across the data with the most recent available data for the three data sources.
            The time of the most recent bid and ask quotes are also included.
        
    Assumes that the data sources contain the same columns
    '''
    pairs = [source_1[0], source_2[0], source_3[0]]
    datasets = [source_1[1], source_2[1], source_3[1]]

    if not isinstance(datasets[0], pd.DataFrame) or not isinstance(datasets[1], pd.DataFrame) or not isinstance(datasets[2], pd.DataFrame):
        raise TypeError("data_1, data_2, and data_3 must be pandas DataFrames.")
    if not (datasets[0].columns.equals(datasets[1].columns) and datasets[0].columns.equals(datasets[2].columns)):
        raise ValueError("All data sources must have the same columns.")
    
    first_data = max(datasets[0].index[0], datasets[1].index[0], datasets[2].index[0])
    combined_index = pd.DatetimeIndex(datasets[0].index.union(datasets[1].index).union(datasets[2].index), name = 'event_time') 

    fields = datasets[0].columns
    all_fields = ['quote_time', *fields, 'bid_change_time', 'ask_change_time']
    columns = pd.MultiIndex.from_product([pairs, all_fields], names=['pair', 'field'])

    aligned_data = pd.DataFrame(index=combined_index, columns=columns)

    for name, data in zip(pairs, datasets):
        original_quote_times = pd.Series(data.index, index=data.index)
        aligned_times = original_quote_times.reindex(combined_index)
        quote_times = aligned_times.ffill()
        aligned_data[(name, 'quote_time')] = quote_times

        for field in data.columns:
            original = data[field]
            aligned = original.reindex(combined_index).ffill()
            aligned_data[(name, field)] = aligned

        for fieldname, field in {'bid': 'bidPrice', 'ask': 'askPrice'}.items():
            quote_mask = data[field].ne(data[field].shift(1))
            quote_mask.iloc[0] = False
            change_times = pd.Series(data.index, index = data.index)
            change_times = change_times.where(quote_mask)
            aligned_change_times = change_times.reindex(combined_index).ffill()
            aligned_data[(name, f'{fieldname}_change_time')] = aligned_change_times

    return aligned_data.loc[first_data:]


def calculate_quote_ages(aligned_data: pd.DataFrame) -> pd.DataFrame:
    '''
    Calculates the time since the latest pair update and time since the latest observed bid/ask price changes.
    
    Parameters
    ----------
        aligned_data (pd.DataFrame): The aligned data.
    Returns
    -------
        pd.DataFrame: The age of each quote in the aligned data.
            The index is the event time and the columns are a two-level MultiIndex with the pair and the field.
            Values are timedeltas representing time since the relevant update/change.
    '''
    pairs = aligned_data.columns.get_level_values('pair').unique()
    columns = pd.MultiIndex.from_product([pairs, ['quote_age', 'bid_age', 'ask_age']], names=['pair', 'field'])
    quote_ages = pd.DataFrame(index=aligned_data.index, columns=columns)
    for p in pairs:
        quote_ages[(p, 'quote_age')] = aligned_data.index-aligned_data[(p, 'quote_time')]
        quote_ages[(p, 'bid_age')] = aligned_data.index-aligned_data[(p, 'bid_change_time')]
        quote_ages[(p, 'ask_age')] = aligned_data.index-aligned_data[(p, 'ask_change_time')]
        
    positive = not (quote_ages < pd.Timedelta(0)).any().any()
    if positive:
        return quote_ages
    else:
        raise ValueError("Negative ages found.")