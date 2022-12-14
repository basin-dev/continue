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


# Run them from the command line using: pytest -v

# TODO: Add your tests here.

def test_width_and_height():
    r = Rectangle(10, 20)
    assert r.width == 10
    assert r.height == 20

def test_get_area():
    r = Rectangle(10, 20)
    assert r.get_area() == 200

def test_set_width():
    r = Rectangle(10, 20)
    r.set_width(100)
    assert r.width == 100

def test_set_height():
    r = Rectangle(10, 20)
    r.set_height(100)
    assert r.height == 100