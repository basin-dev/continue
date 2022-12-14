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



def test_binary_search():
    assert binary_search([1, 2, 3, 4, 5], 2) == 1
    assert binary_search([1, 2, 3, 4, 5], 3) == 2
    assert binary_search([1, 2, 3, 4, 5], 5) == 4
    assert binary_search([1, 2, 3, 4, 5], 6) == -1

def test_bubble_sort():
    assert bubble_sort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]
    assert bubble_sort([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5]

def test_insertion_sort():
    assert insertion_sort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]
    assert insertion_sort([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5]

def test_merge_sort():
    assert merge_sort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]
    assert merge_sort([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5]

def test_quick_sort():
    assert quick_sort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]
    assert quick_sort([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5]

def test_reverse():
    assert reverse("foobar") == "raboof"
    assert reverse("stressed") == "desserts"

def test_selection_sort():
    assert selection_sort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]
    assert selection_sort([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5]