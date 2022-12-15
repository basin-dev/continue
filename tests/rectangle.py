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



# Test the get_area method

def test_get_area_works():
    assert Rectangle(1, 2).get_area() == 3

# Test the set_width method

def test_set_width_works():
    assert Rectangle(1, 2).set_width(3) == Rectangle(3, 2)

# Test the set_height method

def test_set_height_works():
    assert Rectangle(1, 2).set_height(3) == Rectangle(3, 2)

# Test the constructor

def test_constructor_works():
    assert Rectangle(1, 2) == Rectangle(1, 2, width=1, height=2)

# Test the get_area method

def test_get_area_works():
    assert Rectangle(1, 2).get_area() == 3

# Test the set_width method

def test_set_width_works():
    assert Rectangle(1, 2).set_width(3) == Rectangle(3, 2)

# Test the set_height method

def test_set_height_works():
    assert Rectangle(1, 2).set_height(3) == Rectangle(3, 2)

# Test the constructor

def test_constructor_works():
    assert Rectangle(1, 2) == Rectangle(1, 2, width=1, height=2)

# Test the get_area method

def test_get_area_works():
    assert Rectangle(1, 2).get_area() == 3

# Test the set_width method

def test_set_width_works():
    assert Rectangle(1, 2).set_width(3) == Rectangle(3, 2)

# Test the set_height method

def test_set_height_works():
    assert Rectangle(1, 2).set_height(3) == Rectangle(3, 2)

# Test the constructor

def test_constructor_works():
    assert Rect