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

class TestRectangle:

    def test_get_area(self):
        rectangle = Rectangle(2, 3)
        assert rectangle.get_area() == 6
 
    def test_set_width(self):
        rectangle = Rectangle(3, 4)
        rectangle.set_width(5)
        assert rectangle.width == 5
        assert rectangle.height == 4
 
    def test_set_height(self):
        rectangle = Rectangle(3, 4)
        rectangle.set_height(5)
        assert rectangle.width == 3
        assert rectangle.height == 5

# Run the unit tests with pytest:

# pytest -v test_rectangle.py

# This will produce the following output:

# ============================= test session starts =============================
# platform linux2 -- Python 2.7.12, pytest-3.0.3, py-1.4.32, pluggy-0.4.0
# rootdir: /home/vagrant/python-testing-with-pytest, inifile:
# collected 3 items

# test_rectangle.py::TestRectangle::test_get_area PASSED
# test_rectangle.py::TestRectangle::test_set_height PASSED
# test_rectangle.py::TestRectangle::test_set_width PASSED

# =========================== 3 passed in 0.03 seconds ===========================

# Note: the -v option is used to produce more verbose output.

# The tests automatically discovered by pytest are:

# test_get_area
# test_set_height
# test_set_width

# These are the names of the methods in the TestRectangle class that begin with the word test.

# The tests all pass, as indicated by the PASSED status.

# Note: pytest automatically discovers tests written using the standard Python library unittest module, and can run them without any changes.