def calculate_pi(n_terms: int = 10_000_000) -> float:
    # ряд Лейбница — простой, но очень медленно сходится
    total = 0.0
    for k in range(n_terms):
        total += (-1) ** k / (2 * k + 1)
    return 4 * total


def circle_circumference(r: float) -> float:
    return 2 * calculate_pi() * r
