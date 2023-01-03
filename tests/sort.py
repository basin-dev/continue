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


import pytest

from utils import quick_sort


@pytest.mark.parametrize('items', [
    (0, 'zero'),
        (1, 'one'),
        (2, 'two'),
        (3, 'three'),
        (4, 'four'),
        (5, 'five'),
        (6, 'six'),
        (7, 'seven'),
        (8, 'eight'),
        (9, 'nine'),
    ]
    )
    def test_quick_sort(items):
        assert quick_sort(items) == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        assert len(quick_sort(items)) == 8
        assert is_sorted(items)
        assert quick_sort(items) == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        assert len(quick_sort(items)) == 9
    ]
