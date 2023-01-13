def sum(a, b):
    if type(a) == str or type(b) == str:
        return 'Error: one of the arguments is a string'
    else:
        return a + b
first = 1
second = '2'
sum(first, second)