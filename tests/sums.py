def sum_of_digits(n):
    """Return the sum of the digits of the given number."""
    return sum(int(digit) for digit in str(n))

def sum_of_squares(n):
    """Return the sum of the squares of the numbers from 1 to n."""
    return sum(i ** 2 for i in range(1, n + 1))

def sum_of_squares_of_digits(n):
    """Return the sum of the squares of the digits of the given number."""
    return sum(int(digit) ** 2 for digit in str(n))

import pytest

from .test_sum_of_squares_of_digits import test_sum_of_squares_of_digits


@pytest.mark.parametrize("n", [2, 3, 4, 5, 6, 7, 8, 9])
def test_sum_of_squares_of_digits(n):
    assert test_sum_of_squares_of_digits(n) == n * n
