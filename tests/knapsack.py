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


# We use the following convention for imports:
#    from knapsack import solve_knapsack_problem


def test_solve_knapsack_problem():
    items = [[1, 2, 3],
                                                                                                                                                                                                                                                                                                                                                                          ]
    assert len(solve_knapsack_problem(items, 10)) == 10
