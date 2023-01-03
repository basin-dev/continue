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

from bicolor import RGB
from .test_support import assert_red, assert_green, assert_blue

    def test_red():
        assert_red(RGB("0", 0, 0))

    def test_green():
        assert_green(RGB("0", 0, 0))

    def test_blue():
        assert_blue(RGB("0", 0, 0))

    def test_all():
        assert_red(RGB("255", 255, 0))
        assert_green(RGB("255", 255, 0))
        assert_blue(RGB("255", 255, 0))

    def test_invalid():
        assert_red(RGB("1", 1, 1))
        assert_green(RGB("1", 1, 1))
        assert_blue(RGB("1", 1, 1))

    def test_invalid_str():
        assert_red(str("")["0"])
        assert_green(str("")["0"])
        assert_blue(str("")["0"])

    def test_invalid_repr():
        assert_red(RGB("")).repr()
        assert_green(RGB("")).repr()
        assert_blue(RGB("")).repr()

    def test_invalid_eq():
        assert_red(RGB("1", 1, 1) + RGB("0", 0, 0) + RGB("0", 0, 0) + RGB("0", 0, 0))
        assert_green(RGB("1", 1, 1) + RGB("0", 0, 0) + RGB("0", 0, 0) + RGB("0", 0, 0) + RGB("255", 255, 255))
        assert_blue(RGB("1", 1, 1) + RGB("0", 0, 0) + RGB("0", 0, 0) + RGB("0", 0, 0) + RGB("0", 255, 255) + RGB("0", 0, 0))

    def test_invalid_add():
        assert_red(RGB("1", 1, 1) + RGB("0", 0, 0) + RGB("0", 0, 0) + RGB("0", 0, 0))
        assert_green(RGB("1", 1, 1) + RGB("0", 0, 0) + RGB("0", 0, 0) + RGB("0", 0, 0) + RGB("0", 0, 0) + RGB("255", 255, 255))
        assert_blue(RGB("1", 1, 1) + RGB("0", 0, 0) + RGB("0", 0, 0) + RGB("0", 0, 0) + RGB("0", 0, 255) + RGB("0", 0, 0) + RGB("0", 255, 255))

    def test_invalid_sub():
        assert_red(RGB("1", 1, 1) + RGB("0", 0, 0) + RGB("0", 0, 0) + RGB("0", 0, 0))
        assert_green(RGB("1", 1, 1) + RGB("0", 0, 0) + RGB("0", 0, 0) + RGB("0", 0, 0) + RGB("0", 0, 0) + RGB("0", 255, 255))
        assert_blue(RGB("1", 1, 1) + RGB("0", 0, 0) + RGB("0", 0, 0) + RGB("0", 0, 0) + RGB("0", 0, 0) + RGB("0", 255, 255) + RGB("0", 0, 0) + RGB("0", 0, 0) + RGB("0", 0, 0) + RGB("0", 0, 0) + RGB("0", 0, 0) + RGB("0", 0, 0) + RGB("0", 0, 0