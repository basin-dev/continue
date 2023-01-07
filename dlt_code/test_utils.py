import pytest
from utils import *

@pytest.mark.parametrize("seq, n, expected_chunks", [
    ((1,2,3,4,5,6,7,8), 2, [(1,2), (3,4), (5,6), (7,8)]),
    ((1,2,3,4,5,6,7,8), 3, [(1,2,3), (4,5,6), (7,8)]),
    ((1,2,3,4,5,6,7,8), 4, [(1,2,3,4), (5,6,7,8)])
])
def test_chunks(seq, n, expected_chunks):
    assert list(chunks(seq, n)) == expected_chunks




@pytest.mark.parametrize("len_, expected_len", [
    (0, 0),
    (1, 2),
    (2, 4),
    (3, 6),
    (4, 8),
    (8, 16)
])
def test_uniq_id_len(len_, expected_len):
    assert len(uniq_id(len_)) == expected_len

def test_uniq_id_unique():
    # Generate two ids
    id1 = uniq_id()
    id2 = uniq_id()
    # Assert they are not equal
    assert id1 != id2




@pytest.mark.parametrize("v, expected", [
    ('foo', '2V8iEArZG2VHq3bzCgInFA'),
    ('bar', '6mSx6Bi1T6EuZ6Q4F4Yq6Q'),
    ('', '9XMrU6jOZ6pfT6TvE6TKzA')
])
def test_digest128(v, expected):
    assert digest128(v) == expected




@pytest.mark.parametrize("value, result", [
    ("", "47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU="),
    ("Hello World!", "2jmj7l5rSw0yVb/vlWAYkK/YBwk=".rstrip()),
    ("{Hello World!}", "Rt1+yJpfjq3j+Vd3q9zQ2Vf3ZjH2uV7KjfDyFV7yOuo=")
])
def test_digest256(value, result):
    assert digest256(value) == result



@pytest.mark.parametrize('value, expected', [
    ('yes', True),
    ('true', True),
    ('t', True),
    ('y', True),
    ('1', True),
    ('no', False),
    ('false', False),
    ('f', False),
    ('n', False),
    ('0', False),
    (True, True),
    (False, False),
])
def test_str2bool(value, expected):
    assert str2bool(value) == expected

def test_str2bool_raises_value_error():
    with pytest.raises(ValueError):
        str2bool('invalid')





@pytest.mark.parametrize('inputs, expected', [
    ([], {}),
    ([{'a': 1}], {'a': 1}),
    ([{'a': 1}, {'b': 2}], {'a': 1, 'b': 2})
])
def test_flatten_list_of_dicts(inputs, expected):
    assert flatten_list_of_dicts(inputs) == expected


def test_flatten_list_of_dicts_with_duplicate_key():
    with pytest.raises(KeyError):
        flatten_list_of_dicts([{'a': 1}, {'a': 2}])

