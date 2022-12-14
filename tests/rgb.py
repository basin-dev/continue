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


# For example, you might want to check that the above code works for RGB(0, 0, 0) and RGB(255, 255, 255).

def test_addition():
    assert RGB(255, 255, 255) == RGB(255, 255, 255) + RGB(0, 0, 0)

def test_subtraction():
    assert RGB(0, 0, 0) == RGB(0, 0, 0) - RGB(255, 255, 255)

def test_addition_overflow():
    assert RGB(255, 255, 255) == RGB(255, 255, 255) + RGB(255, 255, 255)

def test_subtraction_underflow():
    assert RGB(0, 0, 0) == RGB(0, 0, 0) - RGB(255, 255, 255)

# Now, create a class called Image.
# It should have a constructor that takes a single argument, a 2D array of RGB values.
# It should have a method called "invert" that returns a new image that is the inverse of the original.
# It should have a method called "lighten" that takes a single argument, a scalar, and returns a new image that is the original image with each color component increased by that scalar.
# It should have a method called "darken" that takes a single argument, a scalar, and returns a new image that is the original image with each color component decreased by that scalar.

class Image:
    def __init__(self, rgb_values):
        self.rgb_values = rgb_values
    
    def __str__(self):
        return f"Image({self.rgb_values})"
    
    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.rgb_values == other.rgb_values
    
    def invert(self):
        return Image([[RGB(255 - pixel.red, 255 - pixel.green, 255 - pixel.blue) for pixel in row] for row in self.rgb_values])
    
    def lighten(self, scalar):
