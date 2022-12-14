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