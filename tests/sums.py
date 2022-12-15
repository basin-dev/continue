def sum_of_digits(n):
    """Return the sum of the digits of the given number."""
    return sum(int(digit) for digit in str(n))

def sum_of_squares(n):
    """Return the sum of the squares of the numbers from 1 to n."""
    return sum(i ** 2 for i in range(1, n + 1))

def sum_of_squares_of_digits(n):
    """Return the sum of the squares of the digits of the given number."""
    return sum(int(digit) ** 2 for digit in str(n))


    def test_sum_of_digits():
    assert sum_of_digits(1) == 1
    assert sum_of_digits(2) == 2
    assert sum_of_digits(3) == 5
    assert sum_of_digits(4) == 10
    assert sum_of_digits(5) == 15

#    def test_sum_of_squares():
    assert sum_of_squares(1) == 1
    assert sum_of_squares(2) == 4
    assert sum_of_squares(3) == 9
    assert sum_of_squares(4) == 16
    assert sum_of_squares(5) == 25

#    def test_sum_of_squares_of_digits():
    assert sum_of_squares_of_digits(1) == 1
    assert sum_of_squares_of_digits(2) == 4
    assert sum_of_squares_of_digits(3) == 5
    assert sum_of_squares_of_digits(4) == 10
    assert sum_of_squares_of_digits(5) == 15

#    def test_sum_of_squares_of_digits_with_leading_zero():
    assert sum_of_squares_of_digits_with_leading_zero(1) == 1
    assert sum_of_squares_of_digits_with_leading_zero(2) == 4
    assert sum_of_squares_of_digits_with_leading_zero(3) == 5
    assert sum_of_squares_of_digits_with_leading_zero(4) == 10
    assert sum_of_squares_of_digits_with_leading_zero(5) == 15

#    def test_sum_of_squares_of_digits_with