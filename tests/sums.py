

def sum_of_digits(n):
    """Return the sum of the digits of the given number."""
    return sum(int(digit) for digit in str(n))

def sum_of_squares(n):
    """Return the sum of the squares of the numbers from 1 to n."""
    return sum(i ** 2 for i in range(1, n + 1))

def sum_of_squares_of_digits(n):
    """Return the sum of the squares of the digits of the given number."""
    return sum(int(digit) ** 2 for digit in str(n))

# Unit tests for the above code using pytest. Make sure they are concise and complete.

def test_sum_of_digits():
    assert sum_of_digits(1) == 1
    assert sum_of_digits(2) == 2
    assert sum_of_digits(3) == 3
    assert sum_of_digits(4) == 4
    assert sum_of_digits(5) == 5
    assert sum_of_digits(6) == 6
    assert sum_of_digits(7) == 7
    assert sum_of_digits(8) == 8
    assert sum_of_digits(9) == 9
    assert sum_of_digits(10) == 10
    assert sum_of_digits(11) == 11
    assert sum_of_digits(12) == 12
    assert sum_of_digits(13) == 13
    assert sum_of_digits(14) == 14
    assert sum_of_digits(15) == 15
    assert sum_of_digits(16) == 16
    assert sum_of_digits(17) == 17
    assert sum_of_digits(18) == 18
    assert sum_of_digits(19) == 19
    assert sum_of_digits(20) == 20
    assert sum_of_digits(21) == 21
    assert sum_of_digits(22) == 22
    assert sum_of_digits(23) == 23
    assert sum_of_digits(24) == 24
    assert sum_of_digits(25) == 25
    assert sum_of_digits(26) == 26
    assert sum_of_digits(27) == 27
    assert sum_of_digits(28) == 28
    assert