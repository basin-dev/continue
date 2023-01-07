import pytest

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

@pytest.mark.parametrize(
    "items,capacity",
    [
        pytest.param(get_random_values("item_list", 3), 1),
        pytest.param(get_random_values("item_list", 5, 10), 10),
        pytest.param(get_random_values("item_list", 8, 12, 15, 20), 12),
    ],
)
def test_solve_knapsack_problem(items, capacity):
    assert solve_knapsack_problem(items, capacity) == items


@pytest.mark.parametrize(
    "items,capacity",
    [
        pytest.param(get_random_values("item_list", 3, 5), 5),
        pytest.param(get_random_values("item_list", 8), 10),
    ],
)
def test_solve_knapsack_problem_bad_item_count(items, capacity):
    with pytest.raises(SystemExit):
        solve_knapsack_problem(items, capacity)
