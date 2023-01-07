class RGB:
    def __init__(self, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue
    
    def __str__(self):
        return f"RGB({self.red}, {self.green}, {self.blue})"
    
    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.red == other.red and self.green == other.green and self.blue == other.blue
    
    def __add__(self, other):
        return RGB(min(255, self.red + other.red), min(255, self.green + other.green), min(255, self.blue + other.blue))
    
    def __sub__(self, other):
        return RGB(max(0, self.red - other.red), max(0, self.green - other.green), max(0, self.blue - other.blue))

import pytest
from unittest.mock import Mock

from colours import RGB

pytestmark = pytest.mark.colour


def test_str_str(mock_str):
    assert mock_str("red") == "red"
    assert mock_str("green") == "green"
    assert mock_str("blue") == "blue"
    with pytest.raises(TypeError):
        mock_str("foo")


def test_str_eq(mock_str, str_str):
    assert mock_str("red") == str_str("red")
    assert mock_str("green") == str_str("green")
    assert mock_str("blue") == str_str("blue")


def test_str_eq_eq(mock_str, eq_str):
    assert mock_str("red") == eq_str("red")
    assert mock_str("green") == eq_str("green")
    assert mock_str("blue") == eq_str("blue")


def test_mock_str_str(mock_str):
    with pytest.raises(AttributeError):
        assert mock_str()

    with pytest.raises(TypeError):
            mock_str("foo")


def test_mock_str_eq(mock_str):
    assert mock_str() == "red"
    assert mock_str() == "green"
    assert mock_str() == "blue"


def test_mock_str_eq_eq(mock_str):
    assert mock_str() == eq_str("red")
    assert mock_str() == eq_str("green")
    assert mock_str() == eq_str("blue")


def test_eq_str(mock_str):
    assert mock_str == "red"
    assert mock_str == "green"
    assert mock_str == "blue"


def test_eq_eq(mock_str):
    assert mock_str == eq_str("red")
    assert mock_str == eq_str("green")
    assert mock_str == eq_str("blue")


def test_mock_str_eq_eq(mock_str):
    assert mock_str == eq_str("red")
    assert mock_str == eq_str("green")
    assert mock_str == eq_str("blue")
