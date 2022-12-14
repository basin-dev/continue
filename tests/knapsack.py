def solve_knapsack_problem(items, capacity):
    # sort the items by value
    items = sorted(items, key=lambda x: x.value, reverse=True)
    # initialize the memoization table
    memo = [[0 for _ in range(capacity + 1)] for _ in range(len(items) + 1)]
    # fill the memoization table
    for i in range(1, len(items) + 1):
        for j in range(1, capacity + 1):
            if items[i - 1].weight <= j:
                memo[i][j] = max(memo[i - 1][j], memo[i - 1][j - items[i - 1].weight] + items[i - 1].value)
            else:
                memo[i][j] = memo[i - 1][j]
    # find the items that were selected
    selected = []
    i = len(items)
    j = capacity
    while i > 0 and j > 0:
        if memo[i][j] != memo[i - 1][j]:
            selected.append(items[i - 1])
            j -= items[i - 1].weight
        i -= 1
    return selected


# I will be running your code with a different set of inputs from what you test with.

# Test the class
item1 = Item('item1', 2, 3)
item2 = Item('item2', 1, 2)
item3 = Item('item3', 1, 2)
item4 = Item('item4', 2, 4)
item5 = Item('item5', 10, 10)
item6 = Item('item6', 4, 5)
item7 = Item('item7', 3, 3)
item8 = Item('item8', 2, 2)
item9 = Item('item9', 5, 6)
item10 = Item('item10', 1, 1)

# Test the solve_knapsack_problem function
def test_solve_knapsack_problem():
    # Test 1
    items = [item1, item2, item3, item4, item5]
    capacity = 5
    selected = solve_knapsack_problem(items, capacity)
    assert selected == [item1, item2, item3]
    # Test 2
    items = [item6, item7, item8, item9, item10]
    capacity = 5
    selected = solve_knapsack_problem(items, capacity)
    assert selected == [item6, item8, item10]
    # Test 3
    items = [item1, item2, item3, item4, item5]
    capacity = 15
    selected = solve_knapsack_problem(items, capacity)
    assert selected == [item5]

def test_Item():
    assert item1.name == 'item1'
    assert item1.weight == 2
    assert item1.value == 3

    assert item2.name == 'item2'
    assert item2.weight == 1
    assert item2.value == 2

    assert item3.name == 'item3'
    assert item3.weight == 1
    assert item3.value == 2

    assert item4.name == 'item4'
    assert item4.weight == 2
    assert item4.value == 4

    assert item5.name == 'item5'
