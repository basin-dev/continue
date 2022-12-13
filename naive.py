class Rectangle:

    def __init__(self, width, height):
        self.width = width
        self.height = height
 
    def get_area(self):
        return self.width * self.height
 
    def set_width(self, width):
        self.width = width
 
    def set_height(self, height):
        self.height = height



import pytest

def test_get_area():
    rectangle = Rectangle(2, 3)
    assert rectangle.get_area() == 6

def test_set_width():
    rectangle = Rectangle(2, 3)
    rectangle.set_width(4)
    assert rectangle.width == 4

def test_set_height():
    rectangle = Rectangle(2, 3)
    rectangle.set_height(5)
    assert rectangle.height == 5

def test_set_width_and_height():
    rectangle = Rectangle(2, 3)
    rectangle.set_width(4)
    rectangle.set_height(5)
    assert rectangle.get_area() == 20

# Example of a failing test:

def test_set_width_and_height_fail():
    rectangle = Rectangle(2, 3)
    rectangle.set_width(4)
    rectangle.set_height(5)
    assert rectangle.get_area() == 21