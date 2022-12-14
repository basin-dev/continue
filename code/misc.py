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

def is_sorted(items):
    """Return whether the given list of items is sorted."""
    for i in range(len(items) - 1):
        if items[i] > items[i + 1]:
            return False
    return True

def merge_sort(items):
    """Return the given list of items, sorted."""
    if len(items) <= 1:
        return items
    mid = len(items) // 2
    left = merge_sort(items[:mid])
    right = merge_sort(items[mid:])
    return merge(left, right)

def merge(left, right):
    """Return the given lists of items, sorted."""
    result = []
    while len(left) > 0 and len(right) > 0:
        if left[0] < right[0]:
            result.append(left.pop(0))
        else:
            result.append(right.pop(0))
    result.extend(left)
    result.extend(right)
    return result

def quick_sort(items):
    """Return the given list of items, sorted."""
    if len(items) <= 1:
        return items
    pivot = items.pop()
    left = []
    right = []
    for item in items:
        if item < pivot:
            left.append(item)
        else:
            right.append(item)
    return quick_sort(left) + [pivot] + quick_sort(right)

def reverse(s):
    """Return the given string reversed."""
    return s[::-1]

def selection_sort(items):
    """Return the given list of items, sorted."""
    for i in range(len(items) - 1):
        min_index = i
        for j in range(i + 1, len(items)):
            if items[j] < items[min_index]:
                min_index = j
        items[i], items[min_index] = items[min_index], items[i]
    return items

def sum_of_digits(n):
    """Return the sum of the digits of the given number."""
    return sum(int(digit) for digit in str(n))

def sum_of_squares(n):
    """Return the sum of the squares of the numbers from 1 to n."""
    return sum(i ** 2 for i in range(1, n + 1))

def sum_of_squares_of_digits(n):
    """Return the sum of the squares of the digits of the given number."""
    return sum(int(digit) ** 2 for digit in str(n))