import pytest
import sys
from boltons import tbutils
sys.path.append("..")

from fault_loc import fl2
from debug import parse_traceback
from virtual_filesystem import VirtualFilesystem

def test_fl2():
    stacktrace = parse_traceback("Traceback (most recent call last):\n  File \"test.py\", line 2, in <module>\n    print(1/0)\nZeroDivisionError: division by zero")
    description = "ZeroDivisionError: division by zero"
    filesystem = VirtualFilesystem({"test.py": "print(1/0)"})

    most_sus_frames = fl2(stacktrace, description, filesystem=filesystem)

    assert type(most_sus_frames) == list
    assert len(most_sus_frames) == 1
    assert most_sus_frames[0]['filepath'] == "test.py"