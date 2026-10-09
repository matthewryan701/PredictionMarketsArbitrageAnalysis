import pandas as pd
import numpy as np

df = pd.read_csv('candidates.csv')
if 'flipped' not in df.columns:
    df['flipped'] = 0

confirmed = df[df['confirmed'] == 1].copy()
flipped = confirmed['flipped'] == 1

confirmed['cost_1'] = np.where(
    flipped,
    confirmed['yes_ask_a'] + confirmed['yes_ask_b'],
    confirmed['yes_ask_a'] + confirmed['no_ask_b']
)

confirmed['cost_2'] = np.where(
    flipped,
    confirmed['no_ask_a'] + confirmed['no_ask_b'],
    confirmed['no_ask_a'] + confirmed['yes_ask_b']
)
confirmed['best_cost'] = np.minimum(confirmed['cost_1'], confirmed['cost_2'])
confirmed['arb_return'] = (1 - confirmed['best_cost']) / confirmed['best_cost']

print(confirmed[['platform_a', 'platform_b', 'question_a', 'best_cost', 'arb_return']]
      .sort_values('best_cost').to_string())