@pytest.fixture
def calculator():
    return Calculator()


def test_add(calculator):
    assert calculator.add(2, 3) == 5
    assert calculator.add(2, 0) == 2
    assert calculator.add(-2, -3) == -5
    assert calculator.add(0, 0) == 0
    assert calculator.add(100, 200) == 300
    assert calculator.add(float('inf'), float('inf')) == float('inf')
    assert calculator.add(float('-inf'), float('inf')) == float('-inf')


def test_sub(calculator):
    assert calculator.sub(4, 2) == 2
    assert calculator.sub(float('inf'), float('inf')) == 0
    assert calculator.sub(float('-inf'), float('inf')) == float('-inf')


def test_mul(calculator):
    assert calculator.mul(3, 4) == 12
    assert calculator.mul(float('inf'), 0) == 0
    assert calculator.mul(float('-inf'), 0) == 0


def test_div(calculator):
    assert calculator.div(6, 3) == 2
    assert calculator.div(float('inf'), float('inf')) == 1
    assert calculator.div(float('-inf'), float('inf')) == -1


def test_exp(calculator):
    assert calculator.exp(2, 4) == 16
    assert calculator.exp(float('inf'), 0) == 1
    assert calculator.exp(float('-inf'), 0) == 1
