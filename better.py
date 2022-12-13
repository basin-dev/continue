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
 
def test_rectangle_area():
    rectangle = Rectangle(10, 5)
    assert rectangle.get_area() == 50
 
def test_rectangle_set_width():
    rectangle = Rectangle(10, 5)
    rectangle.set_width(20)
    assert rectangle.get_area() == 100
 
def test_rectangle_set_height():
    rectangle = Rectangle(10, 5)
    rectangle.set_height(20)
    assert rectangle.get_area() == 200



def test_rectangle():
    rectangle = Rectangle(5, 10)
    assert rectangle.width == 5
    assert rectangle.height == 10
    assert rectangle.get_area() == 50
    rectangle.set_height(20)
    rectangle.set_width(10)
    assert rectangle.width == 10
    assert rectangle.height == 20
    assert rectangle.get_area() == 200