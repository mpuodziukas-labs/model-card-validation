from math import sqrt
from statistics import NormalDist


def rate(k, n):
    return k / n


def wilson(k, n, confidence):
    """Wilson score interval, recomputed from k and n."""
    z = NormalDist().inv_cdf((1 + confidence) / 2)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def fmt(x):
    return "%.4f" % x
