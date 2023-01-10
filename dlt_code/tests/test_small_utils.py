from ..small_utils import *

def test_chunks():
    assert list(chunks("abcdefgh", 4)) == [
        "abcd",
        "efgh",
    ]