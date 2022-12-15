

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
        if memo[i][j]!= memo[i - 1][j]:
            selected.append(items[i - 1])
            j -= items[i - 1].weight
        i -= 1
    return selected

# Unit tests for the above code using pytest. Make sure they are concise and complete.

def test_knapsack_problem_1():
    items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101