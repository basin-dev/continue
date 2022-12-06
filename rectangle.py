import pytest

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


class TestGetAreaRectangle:

    def test_normal_case(self):
        rectangle = Rectangle(2, 3)
        assert rectangle.get_area() == 6, "incorrect area"

    """
    Generate  more unit tests for this code
    """
    def test_zero_width(self):
        rectangle = Rectangle(0, 3)
        assert rectangle.get_area() == 0, "incorrect area"

    def test_zero_height(self):
        rectangle = Rectangle(2, 0)
        assert rectangle.get_area() == 0, "incorrect area"

    def test_zero_width_and_height(self):
        rectangle = Rectangle(0, 0)
        assert rectangle.get_area() == 0, "incorrect area"

    def test_negative_width(self):
        rectangle = Rectangle(-2, 3)
        assert rectangle.get_area() == -6, "incorrect area"

    def test_negative_height(self):
        rectangle = Rectangle(2, -3)
        assert rectangle.get_area() == -6, "incorrect area"

    def test_negative_width_and_height(self):
        rectangle = Rectangle(-2, -3)
        assert rectangle.get_area() == 6, "incorrect area"

    def test_float_width(self):
        rectangle = Rectangle(2.5, 3)
        assert rectangle.get_area() == 7.5, "incorrect area"

    def test_float_height(self):
        rectangle = Rectangle(2, 3.5)
        assert rectangle.get_area() == 7, "incorrect area"

    def test_float_width_and_height(self):
        rectangle = Rectangle(2.5, 3.5)
        assert rectangle.get_area() == 8.75, "incorrect area"

    def test_string_width(self):
        rectangle = Rectangle("2", 3)
        assert rectangle.get_area() == 6, "incorrect area"

    def test_string_height(self):
        rectangle = Rectangle(2, "3")
        assert rectangle.get_area() == 6, "incorrect area"

    def test_string_width_and_height(self):
        rectangle = Rectangle("2", "3")
        assert rectangle.get_area() == 6, "incorrect area"

    def test_string_width_and_float_height(self):
        rectangle = Rectangle("2", 3.5)
        assert rectangle.get_area() == 7, "incorrect area"

    def test_float_width_and_string_height(self):
        rectangle = Rectangle(2.5, "3")
        assert rectangle.get_area() == 7.5, "incorrect area"

    def test_string_width_and_negative_height(self):
        rectangle = Rectangle("2", -3)
        assert rectangle.get_area() == -6, "incorrect area"

    def test_negative_width_and_string_height(self):
        rectangle = Rectangle(-2, "3")
        assert rectangle.get_area() == -6, "incorrect area"

    def test_string_width_and_zero_height(self):
        rectangle = Rectangle("2", 0)
        assert rectangle.get_area() == 0, "incorrect area"

    def test_zero_width_and_string_height(self):
        rectangle = Rectangle(0, "3")
        assert rectangle.get_area() == 0, "incorrect area"

    def test_string_width_and_string_height(self):
        rectangle = Rectangle("2", "3")
        assert rectangle.get_area() == 6, "incorrect area"

    def test_string_width_and_string_height_with_spaces(self):
        rectangle = Rectangle(" 2 ", " 3 ")
        assert rectangle.get_area() == 6, "incorrect area"

    def test_string_width_and_string_height_with_spaces_and_tabs(self):
        rectangle = Rectangle(" 2 \t", " 3 \t")
        assert rectangle.get_area() == 6, "incorrect area"

    def test_string_width_and_string_height_with_spaces_and_tabs_and_new_lines(self):
        rectangle = Rectangle(" 2 \t\n", " 3 \t\n")
        assert rectangle.get_area() == 6, "incorrect area"
