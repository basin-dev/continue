import pytest
from ..small_utils import *


def test_chunks():
    assert chunks("a b c d e f g h i j k l m n o p q r s t u v w x y z", 5) == [
        "a b c d e",
        "f g h i j",
        "k l m n o",
        "p q r s t",
        "u v w x y",
    ]