def sum_of_digits(n):
    """Return the sum of the digits of the given number."""
    return sum(int(digit) for digit in str(n))

def sum_of_squares(n):
    """Return the sum of the squares of the numbers from 1 to n."""
    return sum(i ** 2 for i in range(1, n + 1))

def sum_of_squares_of_digits(n):
    """Return the sum of the squares of the digits of the given number."""
    return sum(int(digit) ** 2 for digit in str(n))


# Try to test every possible case.

def test_sum_of_digits():
    assert sum_of_digits(12) == 3
    assert sum_of_digits(123456789) == 45
    assert sum_of_digits(0) == 0
    assert sum_of_digits(-1) == 1
    assert sum_of_digits(10) == 1

def test_sum_of_squares():
    assert sum_of_squares(1) == 1
    assert sum_of_squares(2) == 5
    assert sum_of_squares(3) == 14
    assert sum_of_squares(4) == 30
    assert sum_of_squares(5) == 55

def test_sum_of_squares_of_digits():
    assert sum_of_squares_of_digits(1) == 1
    assert sum_of_squares_of_digits(12) == 5
    assert sum_of_squares_of_digits(123) == 14
    assert sum_of_squares_of_digits(1234) == 30
    assert sum_of_squares_of_digits(12345) == 55