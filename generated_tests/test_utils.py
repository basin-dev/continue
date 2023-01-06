

import pytest

@pytest.mark.parametrize('seq, n, output', [
    ([1,2,3,4], 2, [[1,2], [3,4]]),
    ([1,2,3,4,5], 3, [[1,2,3], [4,5]]),
    ([1,2,3,4], 5, [[1,2,3,4]])
])
def test_chunks(seq, n, output):
    assert list(chunks(seq, n)) == output

import pytest

@pytest.mark.parametrize(
    "seq, n, expected",
    [
        ([1, 2, 3, 4, 5, 6], 2, [[1, 2], [3, 4], [5, 6]]),
        (['a', 'b', 'c', 'd', 'e', 'f'], 3, [['a', 'b', 'c'], ['d', 'e', 'f']])
    ]
)
def test_chunks(seq, n, expected):
    assert list(chunks(seq, n)) == expected
import pytest

@pytest.mark.parametrize("seq, n, expected_chunks", [
    ([1, 2, 3, 4], 2, [[1, 2], [3, 4]]),
    ([1, 2, 3, 4, 5], 3, [[1, 2, 3], [4, 5]]),
    ([1, 2, 3, 4, 5], 2, [[1, 2], [3, 4], [5]]),
    ([], 2, []),
])
def test_chunks(seq, n, expected_chunks):
    assert list(chunks(seq, n)) == expected_chunks

@pytest.mark.parametrize('len_', [2, 4, 8, 16, 32, 64])
def test_uniq_id_length(len_):
    assert len(uniq_id(len_)) == len_ * 2

@pytest.mark.parametrize('len_', [2, 4, 8, 16, 32, 64])
def test_uniq_id_contains_no_letters(len_):
    assert not any(c.isalpha() for c in uniq_id(len_))

@pytest.mark.parametrize('len_', [2, 4, 8, 16, 32, 64])
def test_uniq_id_contains_only_hex_characters(len_):
    assert all(c in string.hexdigits for c in uniq_id(len_))

import pytest

@pytest.mark.parametrize("v, expected", [
    ("", "7f9c2ba4e88f827d6160455076058a75"),
    ("hello", "f7fc8f8d2b5a5b5f5b5a8a5e5d5f5f5b"),
    ("hello world", "e6d073a27e9e2f096a8f7c1e6f2ee7b1"),
    ("hello world, hello", "5b9a5b5a8a5f5d5f5f5b5e5d5b5f5f5b"),
    ("hello world, hello world", "7b2f3f3e2f2e2b2f3b2e2b3f3b2e2f2e")
])
def test_digest128(v, expected):
    assert digest128(v) == expected
import pytest

@pytest.mark.parametrize('v, expected', [
    ('', '47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU='),
    ('hello', 'Kq+3JzVbEtPJAmLj+Yt1pHmI7VuXd+fgn7VuFZsqE/I='),
    ('Hello', 'mTcT/q3xV9XC++h/2VptJ/0bEP+VF/zR+YtV/NtEm5E='),
    ('H3ll0', 'g1fq3BwH6eL+WQ2yvnH4GGQF4Xd4nM8GvZM4E6UwzS4='),
    ('1234567890', 'Q2m4+dgsOxl8bO/U6mwUiSjzYhC8gvYU6iN5X9R5Wg8='),
    ('ąśćżź', '2vlM0/3qHxX9E3kH2QWhAqnIHITt83zRtY+DtYnYt6E=')
])
def test_digest256(v, expected):
    assert digest256(v) == expected
import pytest

@pytest.mark.parametrize("test_input,expected", [
    ("yes", True),
    ("true", True),
    ("t", True),
    ("y", True),
    ("1", True),
    ("no", False),
    ("false", False),
    ("f", False),
    ("n", False),
    ("0", False),
    (True, True),
    (False, False)
])
def test_str2bool(test_input, expected):
    assert str2bool(test_input) == expected

def test_str2bool_err():
    with pytest.raises(ValueError):
        str2bool('maybe')

import pytest


@pytest.mark.parametrize('dicts, expected', [
    ([], {}),
    ([{'a': 1}], {'a': 1}),
    ([{'a': 1}, {'b': 2}], {'a': 1, 'b': 2}),
    ([{'a': 1}, {'a': 2}], pytest.raises(KeyError))
])
def test_flatten_list_of_dicts(dicts, expected):
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected):
            flatten_list_of_dicts(dicts)
    else:
        assert flatten_list_of_dicts(dicts) == expected

import pytest

@pytest.mark.parametrize('input_list, expected', [
    ([{'a': {'b': 1, 'c': 2}}, 'd'], {'a': {'b': 1, 'c': 2}, 'd': None}),
    ([{'a': {'b': 1, 'c': 2}, 'd': 5], {'a': {'b': 1, 'c': 2}, 'd': 5}),
    ([{'a': {'b': 1, 'c': 2}, 'd': {'e': 3}], {'a': {'b': 1, 'c': 2}, 'd': {'e': 3}})
])
def test_flatten_list_of_str_or_dicts_success(input_list: Sequence[Union[StrAny, str]], expected: StrAny):
    result = flatten_list_of_str_or_dicts(input_list)
    assert result == expected

@pytest.mark.parametrize('input_list', [
    [{'a': {'b': 1, 'c': 2}, 'a': 5],
    [{'a': 'b'}, {'a': 'c'}]
])
def test_flatten_list_of_str_or_dicts_fail(input_list: Sequence[Union[StrAny, str]]):
    with pytest.raises(KeyError):
        flatten_list_of_str_or_dicts(input_list)

import pytest

@pytest.mark.parametrize("input_dict,expected_output",[
    ({"key1": {"a":1,"b":2}, "key2": {"c":3,"d":4}}, [{"a":1,"b":2,"key":"key1"},{"c":3,"d":4,"key":"key2"}]),
    ({"key1": [{"a":1,"b":2},{"c":3,"d":4}], "key2": {"c":3,"d":4}}, [{"a":1,"b":2,"key":"key1"},{"c":3,"d":4,"key":"key1"},{"c":3,"d":4,"key":"key2"}]),
    ({"key1": [{"a":1,"b":2},{"c":3,"d":4},{"e":5,"f":6}], "key2": [{"g":7,"h":8},{"i":9,"j":10}]}, [{"a":1,"b":2,"key":"key1"},{"c":3,"d":4,"key":"key1"},{"e":5,"f":6,"key":"key1"},{"g":7,"h":8,"key":"key2"},{"i":9,"j":10,"key":"key2"}])
])
def test_flatten_dicts_of_dicts(input_dict, expected_output):
    assert flatten_dicts_of_dicts(input_dict) == expected_output
import pytest

@pytest.mark.parametrize('dicts, expected', [
    ([{'a': 1, 'b': 2}, {'c': 3}, {'d': 4}, {'e': 5}], [{'key': 'a', 'value': 1}, {'key': 'c', 'value': 3}, {'key': 'd', 'value': 4}, {'key': 'e', 'value': 5}]),
    ([], []),
    ([{'a': 1}], [{'key': 'a', 'value': 1}])
])
def test_tuplify_list_of_dicts(dicts, expected):
    assert tuplify_list_of_dicts(dicts) == expected

def test_tuplify_list_of_dicts_exception():
    with pytest.raises(ValueError) as e:
        tuplify_list_of_dicts([{'a': 1, 'b': 2, 'c': 3}])
    assert 'Tuplify requires one key dicts' in str(e.value)
import pytest

@pytest.mark.parametrize('_iter, expected', [
    ([[1, 2], 3], [1, 2, 3]),
    ([[1, 2], [3, 4]], [1, 2, 3, 4]),
    ([[[1]], [[2]]], [1, 2]),
    ([], []),
    (['abc', [[[1, 2]]], [3, 4], ['def']],  ['abc', 1, 2, 3, 4, 'def']),
])
def test_flatten_list_or_items(_iter, expected):
    assert list(flatten_list_or_items(_iter)) == expected

import pytest

@pytest.mark.parametrize("envs, expected", [
    (['TEST_ENV'], {'test_env': 'value'}),
    (['TEST_ENV', 'OTHER_ENV'], {'test_env': 'value', 'other_env': 'value2'}),
    (['OTHER_ENV'], {'other_env': 'value2'})
])
def test_filter_env_vars(monkeypatch, envs, expected):
    monkeypatch.setenv("TEST_ENV", "value")
    monkeypatch.setenv("OTHER_ENV", "value2")
    assert filter_env_vars(envs) == expected
@pytest.mark.parametrize("dest, update, expected", [
    ({'a': 1, 'b': 2, 'c': 3}, {'a': None, 'b': 4, 'd': 5}, {'c': 3, 'b': 4, 'd': 5}),
    ({'a': 1, 'b': 2, 'c': 3}, {'a': 3, 'b': 4, 'd': None}, {'a': 3, 'b': 4, 'c': 3})
])
def test_update_dict_with_prune(dest, update, expected):
    update_dict_with_prune(dest, update)
    assert dest == expected


@pytest.mark.parametrize(
    "func, _complex, expected",
    [
        (lambda x: x + 2, {'a': 1, 'b': [1, 2, 3]}, {'a': 3, 'b': [3, 4, 5]}),
        (lambda x: x * 2, [1, 2, {'a': 3, 'b': [4, 5]}], [2, 4, {'a': 6, 'b': [8, 10]}]),
        (lambda x: x * x, {'a': [1, 2], 'b': 3}, {'a': [1, 4], 'b': 9})
    ]
)
def test_map_nested_in_place(func, _complex, expected):
    result = map_nested_in_place(func, _complex)
    assert result == expected

import pytest


@pytest.mark.parametrize('input,expected',
                         [(False, False),
                          (True, True),
                          (None, False),
                          (0, False),
                          (1, False)])
def test_is_interactive(input, expected):
    main = type('', (), {'__file__': input})
    assert is_interactive() == expected

import pytest

# Test Case 1: Empty Dictionary
def test_empty_dict():
    assert dict_remove_nones_in_place({}) == {}

# Test Case 2: Dictionary with only None values
@pytest.mark.parametrize("dict_input", [{1: None, 2: None, 3: None}, {'a': None, 'b': None, 'c': None}])
def test_none_values(dict_input):
    assert dict_remove_nones_in_place(dict_input) == {}

# Test Case 3: Dictionary with None and some other values
@pytest.mark.parametrize("dict_input,expected_output", [({1: None, 2: 4, 3: None}, {2: 4}), ({'a': None, 'b': 'hello', 'c': None}, {'b': 'hello'})])
def test_mixed_values(dict_input, expected_output):
    assert dict_remove_nones_in_place(dict_input) == expected_output

import os
import pytest

@pytest.mark.parametrize("env_values, expected_environ", [
    ({
        "TEST_ENV_VAR_1": "1",
        "TEST_ENV_VAR_2": "2"
    }, {
        "TEST_ENV_VAR_1": "1",
        "TEST_ENV_VAR_2": "2"
    }),
    ({
        "TEST_ENV_VAR_3": "3",
        "TEST_ENV_VAR_4": "4"
    }, {
        "TEST_ENV_VAR_3": "3",
        "TEST_ENV_VAR_4": "4"
    }),
])
def test_custom_environ_sets_env_vars(env_values, expected_environ):
    env_before = os.environ.copy()
    with custom_environ(env_values):
        assert os.environ == {**env_before, **expected_environ}
    assert os.environ == env_before

@pytest.mark.parametrize("env_values, expected_environ", [
    ({
        "TEST_ENV_VAR_1": "1",
        "TEST_ENV_VAR_2": "2"
    }, {
        "TEST_ENV_VAR_3": None,
        "TEST_ENV_VAR_4": None
    }),
    ({
        "TEST_ENV_VAR_3": "3",
        "TEST_ENV_VAR_4": "4"
    }, {
        "TEST_ENV_VAR_1": None,
        "TEST_ENV_VAR_2": None
    }),
])
def test_custom_environ_restores_env_vars(env_values, expected_environ):
    env_before = os.environ.copy()
    with custom_environ(env_values):
        pass
    assert os.environ == {

import pytest
import os

@pytest.mark.parametrize('kwargs', [
    {'key1': 'value1'},
    {'key2': 'value2', 'key3': 'value3'}
])
def test_with_custom_environ(kwargs):
    env = os.environ.copy()
    os.environ.update(kwargs)
    @with_custom_environ
    def func():
        pass
    func()
    assert os.environ == env

@pytest.mark.parametrize('kwargs', [
    {},
    {'key1': 'value1', 'key2': 'value2'}
])
def test_with_custom_environ_without_args(kwargs):
    env = os.environ.copy()
    os.environ.update(kwargs)
    @with_custom_environ
    def func():
        pass
    func()
    assert os.environ == env

import pytest

@pytest.mark.parametrize('mode, expected', [
    ('r', 'utf-8'),
    ('w', 'utf-8'),
    ('rb', None),
    ('wb', None),
])
def test_encoding_for_mode(mode, expected):
    assert encoding_for_mode(mode) == expected

@pytest.mark.parametrize("arg, expected", [
    (['/home/user/main_file.py'], '/home/user/main_file.py'),
    (['/home/user/main_file.py', 'arg1'], '/home/user/main_file.py'),
    (['/home/user/main_file.py', 'arg1', 'arg2'], '/home/user/main_file.py'),
    (['/home/user/main_file'], None)
])
def test_main_module_file_path(arg, expected):
    sys.argv = arg
    assert main_module_file_path() == expected
import pytest

@pytest.mark.parametrize("path, expected_dir", [
    ('/home/user/documents', '/home/user/documents'),
    ('/tmp/', '/tmp/'),
    ('', os.path.abspath(os.getcwd())),
    (None, os.path.abspath(os.getcwd()))
])
def test_set_working_dir(path, expected_dir):
    with set_working_dir(path) as wd:
        assert wd == path
    assert os.getcwd() == expected_dir

import pytest

@pytest.mark.parametrize('f,name_attr,expected', [
    (lambda: None, '__name__', '<lambda>'),
    (int, '__name__', 'int'),
    (int, '__class__', 'type'),
    (int, 'foo', None)
])
def test_get_callable_name(f, name_attr, expected):
    assert get_callable_name(f, name_attr) == expected

import pytest

@pytest.mark.parametrize(
    'f, expected', [
        (lambda x: x+1, False),
        (lambda x: x-1, False),
        (lambda x: x*2, False),
        (lambda x: x/2, False),
        (lambda x, y: x+y, False),
        (lambda: None, False),
        (lambda x: inner_func(x), True)
    ]
)
def test_is_inner_callable(f, expected):
    assert is_inner_callable(f) == expected

import pytest
import base64

@pytest.mark.parametrize('pseudo_secret, pseudo_key, expected', [
    ('Secret1', b'Key1', 'dVZvUz0='),
    ('Secret2', b'Key2', 'Rm1wVzM='),
    ('Secret3', b'Key3', 'Vl5rVjU='),
    ('Secret4', b'Key4', 'UnBmVzg=')
])
def test_obfuscate_pseudo_secret(pseudo_secret, pseudo_key, expected):
    assert obfuscate_pseudo_secret(pseudo_secret, pseudo_key) == expected

import pytest
import base64

@pytest.mark.parametrize('obfuscated_secret, pseudo_key, expected_output',
                         [('Qjy4fR1XSX5JfS5+fSZ8', b'\x00', 'Hello World!'),
                          ('Qjy4fR1XSX5JfS5+fSZ8', b'\x55', 'Fdk{Kj~dKj}dKj{dKj~e'),
                          ('Qjy4fR1XSX5JfS5+fSZ8', b'\xFF', '>ho#=jq#=jp#=jq$=jq#'),
                          ('Qjy4fR1XSX5JfS5+fSZ8', b'\x00\xFF', 'Hello World!>ho#=jq#=jp#=jq$=jq#')])
def test_reveal_pseudo_secret(obfuscated_secret, pseudo_key, expected_output):
    assert expected_output == reveal_pseudo_secret(obfuscated_secret, pseudo_key)

import pytest

@pytest.mark.parametrize('env_vars_input', [
    ({'A': 'a', 'B': 'b', 'C': 'c'}),
    ({'1': 'one', '2': 'two', '3': 'three'}),
    ({'apple': 'fruit', 'carrot': 'vegetable', 'cucumber': 'vegetable'})
])
def test_wrap_env_vars_saved(env_vars_input):
    os.environ.clear()
    os.environ.update(env_vars_input)
    _wrap()
    assert os.environ == env_vars_input

@pytest.mark.parametrize('args_input, kwargs_input', [
    ((), {}),
    ((1, 'two', 3), {'four': 4}),
    (('apple', 'banana', 'cucumber'), {'durian': 'smelly'})
])
def test_wrap_args_kwargs_passed(args_input, kwargs_input):
    mock = Mock()
    _wrap(mock, *args_input, **kwargs_input)
    mock.assert_called_once_with(*args_input, **kwargs_input)