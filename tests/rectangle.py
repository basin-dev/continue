

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

# Unit tests for the above code using pytest. Make sure they are concise and complete.

def test_rectangles():
    rectangles = Rectangle(0, 0, 10, 10)
    assert rectangles.get_area() == (0, 0, 10, 10)
    assert rectangles.get_width() == 10
    assert rectangles.get_height() == 10
    assert rectangles.get_area() == (0, 0, 10, 10)
    assert rectangles.get_width() == 10
    assert rectangles.get_height() == 10
    assert rectangles.get_area() == (0, 0, 10, 10)
    assert rectangles.get_width() == 10
    assert rectangles.get_height() == 10
    assert rectangles.get_area() == (0, 0, 10, 10)
    assert rectangles.get_width() == 10
    assert rectangles.get_height() == 10
    assert rectangles.get_area() == (0, 0, 10, 10)
    assert rectangles.get_width() == 10
    assert rectangles.get_height() == 10
    assert rectangles.get_area() == (0, 0, 10, 10)
    assert rectangles.get_width() == 10
    assert rectangles.get_height() == 10
    assert rectangles.get_area() == (0, 0, 10, 10)
    assert rectangles.get_width() == 10
    assert rectangles.get_height() == 10
    assert rectangles.get_area() == (0, 0, 10, 10)
    assert rectangles.get_width() == 10
    assert rectangles.get_height() == 10
    assert rectangles.get_area() == (0, 0, 10, 10)
    assert rectangles.get_width() == 10
    assert rectangles.get_height() == 10
    assert rectangles.get_area() == (