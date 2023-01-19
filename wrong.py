from breakpoint import *

x = 5
num = 2

def greet(name):
    a = 5
    print(format_variables(get_variables(locals(), globals())), "\n\n")
    print("Hello, " + name + num)

def greet_nate():
    print(format_variables(get_variables(locals(), globals())), "\n\n")
    greet("Nate")

if __name__ == "__main__":
    print(format_variables(get_variables(locals(), globals())), "\n\n")
    greet_nate()