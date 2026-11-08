import pandas as pd

def calculate_triangle_returns(data: pd.DataFrame, pair_1: str, pair_2: str, cross_pair: str) -> pd.DataFrame:
    '''
    Calculates triangle returns for a given data set with both triangular directions.

    Parameters
    ----------
        data (pd.DataFrame): The data to analyze.
        pair_1 (str): The first currency pair to analyze. Must represent A/B.
        pair_2 (str): The second currency pair to analyze. Must represent B/C.
        cross_pair (str): The currency pair to analyze the cross between pair_1 and pair_2. Must represent A/C.

    Returns
    _______
        pd.DataFrame: The triangle returns for the data.
            The index is the event time and the columns are the triangle returns.
    '''

    bid_1 = data[(pair_1, 'bidPrice')]
    bid_2 = data[(pair_2, 'bidPrice')]
    bid_cross = data[(cross_pair, 'bidPrice')]
    ask_1 = data[(pair_1, 'askPrice')]
    ask_2 = data[(pair_2, 'askPrice')]
    ask_cross = data[(cross_pair, 'askPrice')]

    forward_return = (bid_1*bid_2)/ask_cross -1
    reverse_return = bid_cross/(ask_1*ask_2) -1

    metrics = pd.DataFrame({'pair1_pair2_cross_return': forward_return,
                            'cross_pair2_pair1_return': reverse_return},
                            index=data.index)
    return metrics

def summarize_triangle_returns(metrics: pd.DataFrame) -> pd.DataFrame:
    '''
    Summarizes one or more triangle return series.

    Parameters
    ----------
        metrics (pd.DataFrame): The triangle returns to summarize.

    Returns
    _______
        pd.DataFrame: The summary of the triangle returns.
            The rows are the metrics and the columns are the triangle return types.
    '''
    summaries = {}

    for col in metrics.columns:
        returns = metrics[col]
        positive_mask = returns>0
        positive_returns = returns[positive_mask]
        n_episodes = (positive_mask & ~positive_mask.shift(1, fill_value=False)).sum()
    
        summaries[col] = {
            'n_obs': returns.count(),
            "n_positive": positive_mask.sum(),
            "positive_share": positive_returns.count() / returns.count(),
            "mean": returns.mean(),
            "median": returns.median(),
            "std": returns.std(),
            "min": returns.min(),
            "max": returns.max(),
            "max_abs_return": returns.abs().max(),
            "90th_percentile": returns.quantile(0.90),
            "99th_percentile": returns.quantile(0.99),
            "mean_positive_return": positive_returns.mean(),
            "median_positive_return": positive_returns.median(),
            "std_positive_return": positive_returns.std(),
            "n_distinct_positive_episodes": n_episodes
            }
    return pd.DataFrame(summaries)