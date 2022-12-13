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
 
 
@pytest.fixture
def rectangle():
    return Rectangle(5, 10)
 
 
def test_get_area(rectangle):
    assert rectangle.get_area() == 50
 
 
def test_set_width(rectangle):
    rectangle.set_width(20)
    assert rectangle.width == 20
 
 
def test_set_height(rectangle):
    rectangle.set_height(30)
    assert rectangle.height == 30

# To run the tests, use the following command:

# pytest test_rectangle.py

# The output should be:

# ========================= test session starts =========================
# platform linux -- Python 3.6.9, pytest-5.4.1, py-1.8.1, pluggy-0.13



def test_rectangle_initialization():
    rectangle = Rectangle(10, 20)
    assert rectangle.width == 10
    assert rectangle.height == 20
 
def test_rectangle_area():
    rectangle = Rectangle(10, 20)
    assert rectangle.get_area() == 200
 
def test_rectangle_set_width():
    rectangle = Rectangle(10, 20)
    rectangle.set_width(30)
    assert rectangle.width == 30
 
def test_rectangle_set_height():
    rectangle = Rectangle(10, 20)
    rectangle.set_height(30)
    assert rectangle.height == 30
 
def test_rectangle_set_negative_width():
    rectangle = Rectangle(10, 20)
    with pytest.raises(ValueError):
        rectangle.set_