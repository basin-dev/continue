import pytest

def test_sum():
    assert sum(1, 2) == 3
    assert sum(1, "two") == 3

def test_abc():
    assert True