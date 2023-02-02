import importme

def test(inp: int) -> int:
    a = importme.exportme(inp)
    return a + 1

def second(inp: int) -> int:
    b = test(1)
    c = b + 1
    return c

if __name__ == "__main__":
    print(second(1))