def find_max(items):
    """Return the maximum value in the given list of items."""
    max_value = items[0]
    for item in items:
        if item > max_value:
            max_value = item
    return max_value

def find_min(items):
    """Return the minimum value in the given list of items."""
    min_value = items[0]
    for item in items:
        if item < min_value:
            min_value = item
    return min_value

def fizz_buzz(n):
    """Return a list of numbers from 1 to n, replacing multiples of 3 with "Fizz", multiples of 5 with "Buzz", and multiples of 3 and 5 with "FizzBuzz"."""
    return ["FizzBuzz" if i % 3 == 0 and i % 5 == 0 else "Fizz" if i % 3 == 0 else "Buzz" if i % 5 == 0 else i for i in range(1, n + 1)]

def is_palindrome(s):
    """Return whether the given string is a palindrome."""
    return s == s[::-1]

def is_prime(n):
    """Return whether the given number is prime."""
    if n <= 1:
        return False
    for i in range(2, n):
        if n % i == 0:
            return False
    return True



def test_find_max():
    assert find_max([0, 1, 2, 3, 4]) == 4
    assert find_max([0, -1, -2, -3, -4]) == 0

def test_find_min():
    assert find_min([0, 1, 2, 3, 4]) == 0
    assert find_min([0, -1, -2, -3, -4]) == -4

def test_fizz_buzz():
    assert fizz_buzz(15) == [1, 2, "Fizz", 4, "Buzz", "Fizz", 7, 8, "Fizz", "Buzz", 11, "Fizz", 13, 14, "FizzBuzz"]

def test_is_palindrome():
    assert is_palindrome("racecar") == True
    assert is_palindrome("foo") == False

def test_is_prime():
    assert is_prime(1) == False
    assert is_prime(17) == True
    assert is_prime(15) == False
    assert is_prime(2) == True
    assert is_prime(11) == True
    assert is_prime(0) == False