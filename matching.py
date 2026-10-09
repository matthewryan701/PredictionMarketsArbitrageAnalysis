import pandas as pd
from data import fetch_polymarket, fetch_kalshi, fetch_manifold
import numpy as np
from rapidfuzz import fuzz, process, utils
from itertools import combinations

# Normalising data into pandas DataFrame columns: platform, question, yes_ask, no_ask
# Polymarket
def normalise_polymarket(markets):
    rows = []
    for market in markets:
        if market.get('bestAsk') is None or market.get('bestBid') is None:
            continue
        rows.append({
            'platform': 'polymarket',
            'question': market['question'],
            'yes_ask': float(market['bestAsk']),
            'no_ask': 1 - float(market['bestBid'])
        })
    return rows

# Kalshi (filtering to FED and BTC decision series)
kalshi_markets = []
for series in ['KXFEDDECISION', 'KXFED', 'KXBTCD']:
    batch = fetch_kalshi(series_ticker=series)
    kalshi_markets += batch

def normalise_kalshi(markets):
    rows = []
    for market in markets:
        rows.append({
            'platform': 'kalshi',
            'question': market['title'],
            'yes_ask': float(market['yes_ask_dollars']),
            'no_ask': float(market['no_ask_dollars'])
        })
    return rows

# Manifold
def normalise_manifold(markets):
    rows = []
    for market in markets:
        rows.append({
            'platform': 'manifold',
            'question': market['question'],
            'yes_ask': market['probability'],
            'no_ask': 1 - float(market['probability'])
        })
    return rows

rows = (
    normalise_polymarket(fetch_polymarket(limit=500))
    + normalise_kalshi(kalshi_markets)
    + normalise_manifold(fetch_manifold())
)
df = pd.DataFrame(rows)

tradeable = (df['yes_ask'] > 0) & (df['yes_ask'] < 1) & (df['no_ask'] > 0) & (df['no_ask'] < 1)
df = df[tradeable]

# Fuzzy matching on question column
COLUMNS = ['platform_a', 'question_a', 'yes_ask_a', 'no_ask_a',
           'platform_b', 'question_b', 'yes_ask_b', 'no_ask_b', 
           'score']

def find_candidates(df, platform_a, platform_b, threshold=70):
    a = df[df['platform'] == platform_a].reset_index(drop=True)
    b = df[df['platform'] == platform_b].reset_index(drop=True)
    if a.empty or b.empty:
        return pd.DataFrame(columns=COLUMNS)
    scores = process.cdist(
        a['question'], b['question'],
        scorer=fuzz.token_sort_ratio, processor=utils.default_process, workers=-1,
    )
    pairs = np.argwhere(scores >= threshold)
    rows = [{
        'platform_a': platform_a, 'question_a': a.loc[i, 'question'],
        'yes_ask_a': a.loc[i, 'yes_ask'], 'no_ask_a': a.loc[i, 'no_ask'],
        'platform_b': platform_b, 'question_b': b.loc[j, 'question'],
        'yes_ask_b': b.loc[j, 'yes_ask'], 'no_ask_b': b.loc[j, 'no_ask'],
        'score': scores[i, j]
    } for i, j in pairs]
    return pd.DataFrame(rows, columns=COLUMNS).sort_values('score', ascending=False)

topics = 'fed|interest rate|bitcoin|btc|election|president'
topic_df = df[df['question'].str.contains(topics, case=False)]

platforms = ['polymarket', 'kalshi', 'manifold']
candidates = pd.concat(
    [find_candidates(topic_df, a, b) for a, b in combinations(platforms, 2)],
    ignore_index=True
)
candidates['confirmed'] = 0
candidates.to_csv('candidates.csv', index=False)
print(candidates.groupby(['platform_a', 'platform_b']).size())