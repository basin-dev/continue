import os

def get_dir_path():
    return os.path.dirname(os.path.realpath(__file__))
dir_path = get_dir_path()
print(dir_path)