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
from decimal import Decimal

@pytest.mark.parametrize(
    "input,expected",
    [
        (Decimal("42"), 6),
        (Decimal("42"), 12),
        (Decimal("1000000"), 200),
        (Decimal("1.5"), 150),
        (Decimal("1.5"), 225),
        (Decimal("0"), 0),
        (Decimal("5"), 5),
        (Decimal("5"), 10),
        (Decimal("5.2"), 620),
        (Decimal("5.2"), 880),
        (Decimal("1.6"), 170),
        (Decimal("1.6"), 250),
    ]
    )
    @pytest.mark.parametrize(
    "input,expected",
    [
        (Decimal("42"), 6),
        (Decimal("42"), 12),
        (Decimal("1000000"), 200),
        (Decimal("1.5"), 150),
        (Decimal("1.5"), 225),
        (Decimal("5"), 10),
        (Decimal("5.2"), 620),
        (Decimal("5.2"), 880),
        (Decimal("1.6"), 170),
        (Decimal("1.6"), 250),
        (Decimal("0"), 0),
        (Decimal("5.2"), 880),
        (Decimal("1.6"), 250),
        (Decimal("0"), 0),
        (Decimal("5.2"), 880),
        (Decimal("1.6"), 250),
    ]
    )
    def test_sum_of_digits(input, expected):
        assert sum_of_digits(input) == expected

@pytest.mark.parametrize(
    "input,expected",
    [
        (Decimal("42"), 6),
        (Decimal("42"), 12),
        (Decimal("1000000"), 200),
        (Decimal("1.5"), 150),
        (Decimal("1.5"), 225),
        (Decimal("0"), 0),
        (Decimal("5"), 10),
        (Decimal("5.2"), 620),
        (Decimal("5.2"), 880),
        (Decimal("1.6"), 170),
        (Decimal("1.6"), 250),
        (Decimal("0"), 0),
        (Decimal("5.2"), 880),
        (Decimal("1.6"), 250),
        (Decimal("0"), 0),
        (Decimal("5.2"), 880),
        (Decimal("1.6"), 250),
    ]
    )
    def test_sum_of_squares(input, expected):
        assert sum_of_squares(input) == expected

def test_sum_of_squares_of_digits(input, expected):
    """
    Test the sum_of_squares_of_digits