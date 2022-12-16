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

def test_get_area(Rectangle):
    assert Rectangle.get_area() == 24

def test_set_width(Rectangle, width):
    assert Rectangle.set_width(width)
    assert width == 24
 
    def test_set_height(Rectangle, height):
        assert Rectangle.set_height(height)
        assert height == 24

def test_set_width_height(Rectangle, width, height):
        assert Rectangle.set_width_height(width, height)

def test_get_area_height(Rectangle):
    assert Rectangle.get_area() == 24
    assert Rectangle.get_height() == 24

def test_set_width_height_area(Rectangle, width, height, area):
    assert Rectangle.set_width_height_area(width, height, area)
    assert area == 24
    assert height * width == area

def test_get_area_width(Rectangle):
    assert Rectangle.get_area() == 24
    assert Rectangle.get_width() == 24

def test_set_height_area_width(Rectangle, height, area, width, height):
    assert Rectangle.set_height_area_width(height, area, width)
    assert width * height == area
    assert height == 24
    assert width * height == area
 
    assert width * height == area

def test_get_area_width_height(Rectangle):
    assert Rectangle.get_area() == 24
    assert Rectangle.get_height() == 24
    assert Rectangle.get_width() == 24
    assert Rectangle.get_height() * height == 24
    assert height * height == 24

def test_get_area_height_width(Rectangle):
    assert Rectangle.get_area