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

import pytest

from .utils import find_max, find_min

def test_find_max(n):
    assert find_max(n) == n

    def test_find_min(n):
        assert find_min(n) == n


def test_fizz_buzz(n):
        assert fizz_buzz(n) == [n for n in range(1, n + 1) if n % 3 == 0 and n % 5 == 0]

def test_is_prime(n):
    assert not is_prime(n)
    assert not is_prime(n)
    assert is_prime(n)
    assert is_prime(n)

def test_is_palindrome(s):
    assert not is_palindrome(s)
    assert is_palindrome(s)

def test_is_palindrome2(s):
    assert is_palindrome2(s)
