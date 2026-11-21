"""Assume m rows and n columns; a left-aligned triangle includes both corners.

Discrete rows approximate a straight hypotenuse; narrow dimensions can repeat
widths. A single row contains n stars. Return strings for reuse and testing.
"""
from math import ceil


def triangle_mn(m: int, n: int) -> str:
    """Bonus: return m rows with maximum width n, for positive integers."""
    if type(m) is not int or type(n) is not int or min(m, n) <= 0:
        raise ValueError("m and n must be positive integers")
    return "\n".join("*" * (n if m == 1 else 1 + ceil(i * (n - 1) / (m - 1))) for i in range(m))


def triangle() -> str:
    """Required fixed-size triangle: 3 rows and a maximum width of 4."""
    return triangle_mn(3, 4)


if __name__ == "__main__":
    print(triangle())
