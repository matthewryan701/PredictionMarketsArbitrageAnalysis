def expected_value(price, true_prob):
    return true_prob / (price - 1)

def kelly_fraction(price, true_prob):
    return max(0, (true_prob - price) / (1 - price))

examples = [
    (0.50, 0.60),
    (0.40, 0.45),
    (0.70, 0.65),
    (0.20, 0.30)
]

for price, true_prob in examples:
    ev = expected_value(price, true_prob)
    f = kelly_fraction(price, true_prob)
    print(f'price {price:.2f}, belief {true_prob:.2f} -> EV {ev:.1%}, Kelly {f:.1%}')