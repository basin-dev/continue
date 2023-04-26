
import pytest
from calculator import Calculator


def test_add():
    calc = Calculator()
    assert calc.add(2, 3) == 5


def test_sub():
    calc = Calculator()
    assert calc.sub(10, 5) == 5


def test_mul():
    calc = Calculator()
    assert calc.mul(4, 5) == 20


def test_div():
    calc = Calculator()
    assert calc.div(20, 4) == 5


def test_exp():
    calc = Calculator()
    assert calc.exp(2, 3) == 8
    assert calculator.div(float('inf'), float('inf')) == 1
    assert calculator.div(float('-inf'), float('inf')) == -1


def test_exp(calculator):
    assert calculator.exp(2, 4) == 16
    assert calculator.exp(float('inf'), 0) == 1
    assert calculator.exp(float('-inf'), 0) == 1
