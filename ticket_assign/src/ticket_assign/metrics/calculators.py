from __future__ import annotations

from math import ceil


def safe_mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def safe_variance(values: list[float]) -> float:
    if not values:
        return 0.0
    mean_value = safe_mean(values)
    return sum((value - mean_value) ** 2 for value in values) / len(values)


def percentile_95(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, ceil(len(ordered) * 0.95) - 1)
    return float(ordered[index])

