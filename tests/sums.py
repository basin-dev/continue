def sum_of_digits(n):
    """Return the sum of the digits of the given number."""
    return sum(int(digit) for digit in str(n))

def sum_of_squares(n):
    """Return the sum of the squares of the numbers from 1 to n."""
    return sum(i ** 2 for i in range(1, n + 1))

def sum_of_squares_of_digits(n):
    """Return the sum of the squares of the digits of the given number."""
    return sum(int(digit) ** 2 for digit in str(n))



# Tests should be in module tests so they can be imported from other tests

import pytest

# Test the functions work as expected

@pytest.mark.parametrize(
    "n",
    [10, 100, 1000, 10000],
    )
def test_sum_of_squares_of_digits(n):
    """Test the sum_of_squares_of_digits function works as expected."""
    assert sum_of_squares_of_digits(n) == 1100
    assert sum_of_squares_of_digits(1000) == 900
    assert sum_of_squares_of_digits(100) == 50
    assert sum_of_squares_of_digits(10) == 1

def test_sum_of_digits(n):
    """Test the sum_of_digits function works as expected."""
    assert int(str(n)) == sum_of_digits(n)

def test_sum_of_squares(n):
    """Test the sum_of_squares function works as expected."""
    assert sum(1, 2, 3, 4) == sum_of_squares(n)

def test_sum_of_squares_of_digits(n):
    """Test the sum_of_squares_of_digits function works as expected."""
    assert sum(int(str(n)), int(str(n)), int(str(n)), int(str(n))) ==
        sum_of_squares_of_digits(n)


def test_sum_of_squares_of_digits_with_negative_n(n):
    """Test the sum_of_squares_of_digits function works as expected."""
    assert sum_of_squares_of_digits(-1) == -1100

def test_sum_of_squares_of_digits_with_invalid_digit(n