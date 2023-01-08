# Generated test file for utils.py

import hashlib
import pytest
import types
import sys
import base64
import os
from pathlib import Path
from os import environ
from typing import List
from pathlib import Path
from typing import Callable
from pytest import mark, param
from ..utils import *

@pytest.mark.parametrize("seq, n, expected", [
    ([1,2,3,4], 2, [[1,2], [3,4]]),
    (['a', 'b', 'c'], 1, [['a'], ['b'], ['c']]),
    (['p', 'y', 't', 'h', 'o', 'n'], 3, [['p', 'y', 't'], ['h', 'o', 'n']])
])
def test_chunks(seq, n, expected):
    assert list(chunks(seq, n)) == expected


@pytest.mark.parametrize('len_,length',[
    (8, 16),
    (4, 8),
    (16,32)
])
def test_uniq_id_length(len_, length):
    assert len(uniq_id(len_)) == length

def test_uniq_id_uniqueness():
    assert uniq_id() != uniq_id()


# Positive Tests
@pytest.mark.parametrize("test_input, expected_output", [
    ("Hello!", "KV7hMvcfT8WGaRZTtTfXtGcmWs1"),
    ("", "7f86da3sdfsFf8dsh8dsf"),
    ("Python", "NQgV0N8GEHx0X7hN3vqcWfP8Oi")
])
def test_digest128_positive(test_input, expected_output):
    assert digest128(test_input) == expected_output

# Negative Tests
@pytest.mark.parametrize("test_input, expected_output", [
    ("Hello!", "7f86da3sdfsFf8dsh8dsf"),
    ("", "KV7hMvcfT8WGaRZTtTfXtGcmWs1"),
    ("Python", "7f86da3sdfsFf8dsh8dsf")
])
def test_digest128_negative(test_input, expected_output):
    assert digest128(test_input) != expected_output


@pytest.mark.parametrize("test_input,expected", [
    ('', '47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU='),
    ('aaa', 'AQXGj+kR6JZnhf/z6t+5W5f5CQ2gGmxJOCSn8XURHdM='),
    ('bbb', 'D8H7VuAMvwM/mVjY/S9XHVJXxh2G7Vu4KjUJh6U0e6U=')
])
def test_digest256(test_input, expected):
    assert digest256(test_input) == expected


@pytest.mark.parametrize('value, expected', [
    ('true', True),
    ('false', False),
    ('yes', True),
    ('no', False),
    ('t', True),
    ('f', False),
    ('y', True),
    ('n', False),
    ('1', True),
    ('0', False)
])
def test_str2bool(value, expected):
    assert str2bool(value) == expected

# Negative test
def test_str2bool_raises_error():
    with pytest.raises(ValueError):
        str2bool('foo')


@pytest.mark.parametrize('dicts, output', [
    # Test that flat list is flattened correctly
    ([{'a': 1}, {'b': 2}, {'c': 3}], {'a': 1, 'b': 2, 'c': 3}),

    # Test with empty input
    ([], {}),

    # Test with strings
    ([{'a': '1'}, {'b': '2'}, {'c': '3'}], {'a': '1', 'b': '2', 'c': '3'})
])
def test_flatten_list_of_dicts(dicts, output):
    assert flatten_list_of_dicts(dicts) == output

# Test that KeyError is raised when duplicate key is supplied
with pytest.raises(KeyError):
    flatten_list_of_dicts([{'a': 1}, {'a': 2}])


@pytest.mark.parametrize('seq, expected', [
    ([{'a': {'b': 1}}, 'b'], {'a': {'b': 1}, 'b': None}),
    ([{'a': {'b': 1}}, {'b': 2}], {'a': {'b': 1}, 'b': 2}),
    (['a', 'b'], {'a': None, 'b': None}),
    (['a', {'b': 1}], {'a': None, 'b': 1}),
    (['a', 'a'], pytest.raises(KeyError, match=r'Cannot flatten with duplicate key a'))
])
def test_flatten_list_of_str_or_dicts(seq, expected):
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected):
            flatten_list_of_str_or_dicts(seq)
    else:
        assert flatten_list_of_str_or_dicts(seq) == expected


@pytest.mark.parametrize('dicts, expected', [
    ({'K': {'a': 1}, 'L': {'b': 2}}, [{'a': 1, 'key': 'K'}, {'b': 2, 'key': 'L'}]),
    ({'K': [{'a': 1}, {'d': 4}], 'L': {'b': 2}}, [{'a': 1, 'key': 'K'}, {'d': 4, 'key': 'K'}, {'b': 2, 'key': 'L'}]),
    ({'K': [{'a': 1}, {'d': 4}], 'L': [{'b': 2}, {'e': 5}]}, [{'a': 1, 'key': 'K'}, {'d': 4, 'key': 'K'}, {'b': 2, 'key': 'L'}, {'e': 5, 'key': 'L'}]),
    ({}, []),
    ({'K': []}, []),
    ({'K': [], 'L': []}, []),
    ({'K': [1, 2, 3], 'L': [4, 5, 6]}, [{'key': 'K', 0: 1, 1: 2, 2: 3}, {'key': 'L', 0: 4, 1: 5, 2: 6}])
])
def test_flatten_dicts_of_dicts(dicts, expected):
    assert flatten_dicts_of_dicts(dicts) == expected


@pytest.mark.parametrize('input_dicts, expected_dicts',
                         [
                             ([{"key1": "value1"}], [{"key": "key1", "value": "value1"}]),
                             ([{"key1": "value1"}, {"key2": "value2"}], [{"key": "key1", "value": "value1"}, {"key": "key2", "value": "value2"}]),
                             ([{"key1": "value1"}, {"key2": "value2", "key3": "value3"}], ValueError)
                         ])
def test_tuplify_list_of_dicts(input_dicts, expected_dicts):
    if isinstance(expected_dicts, ValueError):
        with pytest.raises(ValueError):
            tuplify_list_of_dicts(input_dicts)
    else:
        assert tuplify_list_of_dicts(input_dicts) == expected_dicts


@pytest.mark.parametrize(
    'input_data,expected_output',
    [
        ([1,2,3], [1,2,3]),
        (range(4), list(range(4))),
        ([[1,2],3], [1,2,3]),
        ([[1,2], [3,4]], [1,2,3,4])
    ]
)
def test_flatten_list_or_items(input_data: TDataItem, expected_output) -> None:
    assert list(flatten_list_or_items(input_data)) == expected_output


# @pytest.mark.parametrize("input_env_vars,expected_output", [
#     (['PYTHON_VERSION','HOME'], {'python_version': os.environ['PYTHON_VERSION'], 'home': os.environ['HOME']}),
#     (['PATH'], {'path': os.environ['PATH']}),
#     (['FOO'], {})
# ])
# def test_filter_env_vars(input_env_vars, expected_output):
#     assert filter_env_vars(input_env_vars) == expected_output

@pytest.mark.parametrize('dest, update, expected', [
    ({'a': 1, 'b': 2, 'c': 3}, {'a': 4, 'b': None, 'd': 5}, {'a': 4, 'c': 3, 'd': 5}),
    ({'a': 1, 'b': 2, 'c': 3}, {'b': None}, {'a': 1, 'c': 3}),
    ({'a': 1, 'b': 2, 'c': 3}, {'d': 4}, {'a': 1, 'b': 2, 'c': 3, 'd': 4}),
    ({'a': 1, 'b': 2, 'c': 3}, {}, {'a': 1, 'b': 2, 'c': 3})
])
def test_update_dict_with_prune(dest, update, expected):
    update_dict_with_prune(dest, update)
    assert dest == expected


@pytest.mark.parametrize('input_dict, expected_output', [
    ({'a': 1, 'b': [2, 3, 4]}, {'a': 2, 'b': [4, 6, 8]}),
    ({'a': [{'b': 1}]}, {'a': [{'b': 2}]})
])
def test_map_nested_in_place(input_dict, expected_output):
    def double(x):
        return x * 2

    assert map_nested_in_place(double, input_dict) == expected_output


@pytest.mark.parametrize('mainfile, expected', [
    (None, True),
    ('script.py', False)
    ])
def test_is_interactive(mainfile, expected):
    import __main__ as main
    if mainfile is not None:
        setattr(main, '__file__', mainfile)
    assert is_interactive() == expected


@pytest.mark.parametrize('d, expected',
                         [({1:2, 3:4, 5:None, 6:7}, {1:2, 3:4, 6:7}),
                          ({'a':'b', 'c':None, 'd':'e'}, {'a':'b', 'd':'e'})])
def test_dict_remove_nones_in_place(d, expected):
    assert dict_remove_nones_in_place(d) == expected


@pytest.mark.parametrize("env, expected_env", [
    ({'KEY1':'VALUE1', 'KEY2':'VALUE2'}, {'KEY1':'VALUE1', 'KEY2':'VALUE2'}),
    ({'KEY1':'VALUE1', 'KEY2':'VALUE2', 'KEY3':None}, {'KEY1':'VALUE1', 'KEY2':'VALUE2', 'KEY3':None})
])
def test_custom_environ(env, expected_env):
    with custom_environ(env):
        assert os.getenv('KEY1') == expected_env['KEY1']
        assert os.getenv('KEY2') == expected_env['KEY2']

@pytest.mark.parametrize("env, expected_env", [
    ({'KEY1':'VALUE1', 'KEY2':'VALUE2'}, {'KEY1':'OLD1', 'KEY2':'OLD2'}),
    ({'KEY1':'VALUE1', 'KEY2':'VALUE2', 'KEY3':None}, {'KEY1':'OLD1', 'KEY2':'OLD2', 'KEY3':'OLD3'})
])
def test_custom_environ_restore(env, expected_env):
    os.environ['KEY1'] = 'OLD1'
    os.environ['KEY2'] = 'OLD2'
    os.environ['KEY3'] = 'OLD3'
    with custom_environ(env):
        pass
    assert os.getenv('KEY1') == expected_env['KEY1']
    assert os.getenv('KEY2') == expected_env['KEY2']


def test_custom_environ():
    os.environ['TEST1'] = 'Test1'
    os.environ['TEST2'] = 'Test2'
    assert os.environ['TEST1'] == 'Test1'
    assert os.environ['TEST2'] == 'Test2'
    
    @with_custom_environ
    def test_func(a, b):
        return a + b
    
    assert test_func(1, 2) == 3
    assert os.environ['TEST1'] == 'Test1'
    assert os.environ['TEST2'] == 'Test2'

def test_custom_environ_2():
    os.environ['TEST1'] = 'Test1'
    os.environ['TEST2'] = 'Test2'
    assert os.environ['TEST1'] == 'Test1'
    assert os.environ['TEST2'] == 'Test2'
    
    @with_custom_environ
    def test_func_2(a, b):
        return a + b
    
    assert test_func_2(2, 3) == 5
    assert os.environ['TEST1'] == 'Test1'
    assert os.environ['TEST2'] == 'Test2'

def test_custom_environ_3():
    os.environ['TEST1'] = 'Test1'
    os.environ['TEST2'] = 'Test2'
    assert os.environ['TEST1'] == 'Test1'
    assert os.environ['TEST2'] == 'Test2'
    
    @with_custom_environ
    def test_func_3(a, b):
        return a + b
    
    assert test_func_3(3, 4) == 7
    assert os.environ['TEST1'] == 'Test1'
    assert os.environ['TEST2'] == 'Test2'


@pytest.mark.parametrize('mode, expected', [
    ('r', 'utf-8'),
    ('rb', None),
    ('w', 'utf-8'),
    ('wb', None)
])
def test_encoding_for_mode(mode: str, expected: Optional[str]):
    assert encoding_for_mode(mode) == expected

@pytest.mark.parametrize("argv, expected_result", [
    ([], None),
    ([""], None),
    (["file1.py"], "file1.py"),
    (["file2.py", "file3.py"], "file2.py")
])
def test_main_module_file_path(argv, expected_result):
    sys.argv = argv
    assert main_module_file_path() == expected_result

@pytest.mark.parametrize("path, expected_dir", [
    ("/home/user/foo/", "/home/user/foo"),
    ("/home/user/bar/", "/home/user/bar")
])
def test_set_working_dir(path, expected_dir):
    with set_working_dir(path):
        assert os.getcwd() == expected_dir

# Testing if the function is setting the directory back
@pytest.mark.parametrize("path, expected_dir", [
    ("/home/user/foo/", "/home/user/bar"),
    ("/home/user/bar/", "/home/user")
])
def test_set_working_dir_return(path, expected_dir):
    with set_working_dir(path):
        pass
    assert os.getcwd() == expected_dir

# Additional code needed for tests
class TestClass:
    def test_method(self):
        pass

@pytest.mark.parametrize('f, name_attr, expected', [
    (lambda: None, '__name__', '<lambda>'),
    (str.upper, '__name__', 'upper'),
    (TestClass.test_method, '__name__', 'test_method'),
    (TestClass.test_method, '__class__', 'TestClass')
])
def test_get_callable_name(f, name_attr, expected):
    assert get_callable_name(f, name_attr) == expected


@pytest.mark.parametrize('f, name_attr', [
    (TestClass.test_method, '__invalid_attr__')
])
def test_get_callable_name_no_attr(f, name_attr):
    assert get_callable_name(f, name_attr) is None



# @pytest.mark.parametrize('f_name,expected',
#     [('f1', False),
#      ('outer.f2', False),
#      ('outer.inner.f3', True),
#      ('outer.inner.inner_inner.f4', True)
#     ])
# def test_is_inner_callable(f_name, expected):
#     assert is_inner_callable(get_callable_by_name(f_name)) == expected


# @pytest.mark.parametrize('f_name,expected',
#     [('f1', False),
#      ('outer.f2', False),
#      ('outer.inner.f3', True),
#      ('outer.inner.inner_inner.f4', True)
#     ])
# def test_is_inner_callable_name_attr(f_name, expected):
#     assert is_inner_callable(get_callable_by_name(f_name), name_attr='__qualname__') == expected


@pytest.mark.parametrize("pseudo_secret, pseudo_key, expected_output", [
    ("This is a secret", b"A", "IFxsaA=="),
    ("This is a secret", b"\x00", "IFxsaEQ="),
    ("This is a secret", b"\x01", "IFxsaFk=")
])
def test_obfuscate_pseudo_secret(pseudo_secret, pseudo_key, expected_output):
    assert obfuscate_pseudo_secret(pseudo_secret, pseudo_key) == expected_output


@pytest.mark.parametrize('obfuscated_secret, pseudo_key, expected_secret', [
    ('U2FsdGVkX1/rE5F/n/nLh5vQ/f+P/X9XgDpEW8NvA==', b'\x00', 'supersecretpassword'),
    ('U2FsdGVkX19ZpH8GKjMzpBzwA+yC3Y8ltvYi3FbxVQ==', b'\xFF', 'password12345678'),
    ('U2FsdGVkX18R1GjPAx9XaT3q8V+TfTUgCRVjKmfUYg==', b'\xAA', 'supersecretpassword1'),
    ('U2FsdGVkX19qf9XhAqGJpvT7VdRk6fOiO2zsKsDxVQ==', b'\x01', 'password123456789'),
    ('U2FsdGVkX19MzSJxKHhZBX8gB5Csqqt/jwQd/nk5YQ==', b'\x02', 'password12345678910')
])
def test_reveal_pseudo_secret(obfuscated_secret, pseudo_key, expected_secret):
    assert reveal_pseudo_secret(obfuscated_secret, pseudo_key) == expected_secret


@pytest.mark.parametrize("seq, n, expected_output", [
    ([1, 2, 3, 4, 5], 2, [[1, 2], [3, 4], [5]]),
    ([5, 4, 3, 2, 1], 3, [[5, 4, 3], [2, 1]]),
    ([1, 2, 3, 4, 5], 5, [[1, 2, 3, 4, 5]]),
    ])
def test_chunks(seq, n, expected_output):
    output = list(chunks(seq, n))
    assert output == expected_output


@pytest.mark.parametrize('len_, expected_length', [(8, 16), (16, 32), (32, 64)])
def test_uniq_id_length(len_, expected_length):
    assert len(uniq_id(len_)) == expected_length

@pytest.mark.parametrize('len_', [4, 16, 32, 64])
def test_uniq_id_type(len_):
    assert type(uniq_id(len_)) is str

@pytest.mark.parametrize('len_', [4, 16, 32, 64])
def test_uniq_id_uniqueness(len_):
    uids = set()
    for _ in range(100):
        uid = uniq_id(len_)
        assert uid not in uids
        uids.add(uid)

@pytest.mark.parametrize('v, expected', [
    ('', '7f9c2ba4e88f827d6160455076058a86'),
    ('Word', '9e69e20d4b741f4c4bbd739d6d1c22fc'),
    ('Test', '9a9f0d39f7e8e3c3d7f2b2d0a7a8c43f'),
    ('Hello', '493c2de66f619f0a7d0be87f37fbb50a'),
    ('Foo', '9fb9f7a8f48c80d7a15daf6d99f22a8c'),
    ('Bar', 'd6e1eb6f3c6ef3f6f2d6c5b5d8b5f5f9')
])
def test_digest128(v, expected):
    assert digest128(v) == expected


@pytest.mark.parametrize("input_str,expected_str", [
    ('Test', 'SXfYXVN+Kx1yE5p5m5F5uHqG3e/ZhDSDv63/XRXA7K0='),
    ('Test string', 'lR6VbIG16LstfKgjIzbPzYX3qH6UgE6UVWKsU1AyfPA='),
    ('', '47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU=')
])
def test_digest256(input_str, expected_str):
    assert digest256(input_str) == expected_str


@pytest.mark.parametrize('input_str, expected',[
    ('yes', True),
    ('true', True),
    ('t', True),
    ('y', True),
    ('1', True),
    ('no', False),
    ('false', False),
    ('f', False),
    ('n', False),
    ('0', False)
    ])

def test_str2bool(input_str, expected):
    assert str2bool(input_str) == expected

@pytest.mark.parametrize('inputs, expected', [
    (
        [{'k1': {'k11': 'v11'}}, {'k2': {'k22': 'v22'}}],
        {'k1': {'k11': 'v11'}, 'k2': {'k22': 'v22'}}
    ),
    (
        [{'k1': {'k11': 'v11'}}, {'k1': {'k11': 'v12'}}],
        pytest.raises(KeyError)
    ),
    (
        [{'k1': ['v1', 'v2']}],
        {'k1': ['v1', 'v2']}
    ),
    (
        [],
        {}
    )
])
def test_flatten_list_of_dicts(inputs, expected):
    if isinstance(expected, type):
        with pytest.raises(expected):
            flatten_list_of_dicts(inputs)
    else:
        assert flatten_list_of_dicts(inputs) == expected


@pytest.mark.parametrize('seq, expected', [
    ([{'a': {'b': 1}}, {'c': 2}], {'a': {'b': 1}, 'c': 2}),
    (['a', {'b': {'c': 3}}, 'd'], {'a': None, 'b': {'c': 3}, 'd': None})
])
def test_flatten_list_of_str_or_dicts(seq, expected):
    assert flatten_list_of_str_or_dicts(seq) == expected

def test_flatten_list_of_str_or_dicts_raises_on_duplicate_key():
    with pytest.raises(KeyError):
        flatten_list_of_str_or_dicts([{'a': 1}, 'a'])


@pytest.mark.parametrize('inputs, expected_outputs', [
    ({'k1': {'name': 'alex'}, 'k2': {'name': 'joe'}}, [{'key': 'k1', 'name': 'alex'}, {'key': 'k2', 'name': 'joe'}]),
    ({'k1': {'name': 'alex', 'age': 25}, 'k2': {'name': 'joe', 'age': 23}}, [{'key': 'k1', 'name': 'alex', 'age': 25}, {'key': 'k2', 'name': 'joe', 'age': 23}]),
    ({'k1': [{'name': 'alex'}, {'name': 'joe'}], 'k2': [{'name': 'matt'}, {'name': 'dave'}]}, [{'key': 'k1', 'name': 'alex'}, {'key': 'k1', 'name': 'joe'}, {'key': 'k2', 'name': 'matt'}, {'key': 'k2', 'name': 'dave'}]),
])
def test_flatten_dicts_of_dicts(inputs, expected_outputs):
    outputs = flatten_dicts_of_dicts(inputs)
    assert outputs == expected_outputs

#
#
#
@pytest.mark.parametrize('dicts, expected', [
    ([{'name': 'John'}, {'age': 26}], [{'key': 'name', 'value': 'John'}, {'key': 'age', 'value': 26}]),
    ([{'name': 'John', 'age': 26}], [{'key': 'name', 'value': 'John', 'age': 26}])
])
def test_tuplify_list_of_dicts(dicts, expected):
    assert tuplify_list_of_dicts(dicts) == expected


@pytest.mark.parametrize('_iter,expected', [
    ([[1, 2, 3], 4], [1, 2, 3, 4]),
    ([[1], [2, 3], [4]], [1, 2, 3, 4]),
    ([1, 2, [3, 4]], [1, 2, 3, 4]),
    ([1, [2, [3], 4]], [1, 2, 3, 4]),
    ([[[1], 2], 3], [1, 2, 3]),
    ([], [])
])
def test_flatten_list_or_items(_iter, expected):
    assert list(flatten_list_or_items(_iter)) == expected

def test_filter_env_vars():
    # empty input
    assert filter_env_vars([]) == {}

    # invalid var
    assert filter_env_vars(['invalid_var']) == {}

    # valid input
    os.environ['TEST_VAR'] = 'test'
    assert filter_env_vars(['TEST_VAR']) == {'test_var': 'test'}

    # multiple valid input
    os.environ['TEST_VAR_2'] = 'test2'
    assert filter_env_vars(['TEST_VAR', 'TEST_VAR_2']) == {'test_var': 'test', 'test_var_2': 'test2'}


@pytest.mark.parametrize("dict1, dict2, expected", [
    ({'a': 1, 'b': 2, 'c': 3}, {'a': 10, 'b': None, 'd': 4}, {'a': 10, 'c': 3, 'd': 4}),
    ({'a': 1, 'b': 2, 'c': 3}, {'a': 10, 'b': 2, 'd': None}, {'a': 10, 'b': 2, 'c': 3}),
    ({'a': 1, 'b': 2, 'c': 3}, {'d': 4}, {'a': 1, 'b': 2, 'c': 3, 'd': 4}),
    ({'a': 1, 'b': 2, 'c': 3}, {}, {'a': 1, 'b': 2, 'c': 3}),
    ({'a': None, 'b': None, 'c': 3}, {}, {})
])
def test_update_dict_with_prune(dict1, dict2, expected):
    update_dict_with_prune(dict1, dict2)
    assert dict1 == expected


@pytest.mark.parametrize('input_data, expected', [
    (
        [1, 2, 3],
        [2, 4, 6]
    ),
    (
        [1, 2, [3, 4]],
        [2, 4, [6, 8]]
    ),
    (
        [{'a': 1, 'b': 2}, {'c': 3, 'd': 4}],
        [{'a': 2, 'b': 4}, {'c': 6, 'd': 8}]
    ),
    (
        [{'a': [1, 2, 3], 'b': [4, 5, 6]}, {'c': [7, 8, 9], 'd': [10, 11, 12]}],
        [{'a': [2, 4, 6], 'b': [8, 10, 12]}, {'c': [14, 16, 18], 'd': [20, 22, 24]}]
    ),
    (
        [{'a': [1, 2, [3, 4]], 'b': [4, 5, [6, 7]]}, {'c': [7, 8, [9, 10]], 'd': [10, 11, [12, 13]]}],
        [{'a': [2, 4, [6, 8]], 'b': [8, 10, [12, 14]]}, {'c': [14, 16, [18, 20]], 'd': [20, 22, [24, 26]]}]
    )
])
def test_map_nested_in_place(input_data, expected):
    """Test the map_nested_in_place() function."""
    def double(x):
        return x * 2
    assert map_nested_in_place(double, input_data) == expected


@pytest.mark.parametrize('has_main_file', [True, False])
def test_is_interactive(has_main_file):
    import __main__ as main
    if has_main_file:
        setattr(main, '__file__', 'test_file.py')

    assert is_interactive() is not has_main_file


@pytest.mark.parametrize("d, expected", [
    ({1: 1, 2: None, 3: 3}, {1: 1, 3: 3}),
    ({'a': None, 'b': 'b'}, {'b': 'b'}),
    ({None: None}, {})
])
def test_dict_remove_nones_in_place(d, expected):
    assert dict_remove_nones_in_place(d) == expected


@pytest.mark.parametrize("env, expected_env", [
    ({"key1": "val1"}, {"key1": "val1"}),
    ({"key1": None}, {}),
])
def test_custom_environ_with_valid_input(env, expected_env):
    with custom_environ(env):
        assert os.environ == expected_env

@pytest.mark.parametrize("env", [
    ({1: "val1"}),
    ({None: "val1"}),
    ({1: None}),
    ({None: None}),
])
def test_custom_environ_with_invalid_input(env):
    with pytest.raises(TypeError):
        with custom_environ(env):
            pass

@pytest.mark.parametrize('environ_dict', [
    {'key1': 'val1'},
    {'key2': 'val2'},
    {}
])
def test_with_custom_environ(environ_dict):
    os.environ.update(environ_dict)
    saved_environ = os.environ.copy()
    @with_custom_environ
    def test_func():
        pass
    test_func()
    assert os.environ == saved_environ


@pytest.mark.parametrize("mode, output", [
    ("rb", None),
    ("wb", None),
    ("r", "utf-8"),
    ("w", "utf-8"),
    ("rb+", None),
    ("wb+", None),
    ("r+", "utf-8"),
    ("w+", "utf-8")
])
def test_encoding_for_mode(mode, output):
    assert encoding_for_mode(mode) == output

@pytest.mark.parametrize("sys_argv, expected_output", [
    ([], None),
    (["test.py"], "test.py"),
    (["default.txt", "test.py"], "test.py"),
    (["default.txt", "test.py", "other.txt"], "test.py")
])

def test_main_module_file_path(sys_argv, expected_output):
    sys.argv = sys_argv
    assert main_module_file_path() == expected_output


@pytest.fixture
def curr_dir():
    return os.path.abspath(os.getcwd())

@pytest.mark.parametrize("path,expected",[
    (None, os.path.abspath(os.getcwd())),
    (os.path.abspath(os.getcwd()), os.path.abspath(os.getcwd())),
    (os.getcwd(), os.path.abspath(os.getcwd())),
    (os.path.dirname(os.getcwd()), os.path.dirname(os.path.abspath(os.getcwd())))
])
def test_set_working_dir(path, expected, curr_dir):
    with set_working_dir(path):
        new_dir = os.path.abspath(os.getcwd())
        assert new_dir == expected
    final_dir = os.path.abspath(os.getcwd())
    assert final_dir == curr_dir


# @pytest.mark.parametrize('f', [
#     lambda x: x*2,
#     class Foo:
#         def __call__(self, x):
#             return x*2
#     ()
# ])
@pytest.mark.parametrize('name_attr', [
    '__name__',
    '__class__'
])
def test_get_callable_name(f: AnyFun, name_attr: str):
    result = get_callable_name(f, name_attr)
    assert result == 'Foo' or result == '<lambda>'

@mark.parametrize('f, expected', [
    (lambda x: x, False),
    (is_inner_callable, False),
    (lambda x: (lambda y: y), True),
    (lambda x: (lambda y: (lambda z: z)), True),
    (lambda x, y=lambda z: z: x, True),
    (lambda x, y=2, z=lambda a, b: a + b: x, True),
    (lambda x, y=2, z=lambda a, b: a + b: z, True),
    (lambda x, y=2, z=lambda a, b: a + b: y, False)
])
def test_is_inner_callable(f: Callable, expected: bool) -> None:
    assert is_inner_callable(f) == expected


@pytest.mark.parametrize('pseudo_secret, pseudo_key, expected_output', [
    ('test', b'\x00', 'AAAB'),
    ('anothertest', b'\x01', 'AQAJAgA='),
    ('test', b'\x02', 'AgACAA=='),
    ('', b'\x02', 'AA=='),
    ('test', b'\x00\x01', 'AQAAAgA='),
    ('test', b'\x01\x02', 'AQAAAgAB'),
    ('1234567890', b'\x01', 'BQEHAhEJAhQJ')
])
def test_obfuscate_pseudo_secret(pseudo_secret, pseudo_key, expected_output):
    assert obfuscate_pseudo_secret(pseudo_secret, pseudo_key) == expected_output


@pytest.mark.parametrize(
    "obfuscated_secret, pseudo_key, expected",
    [
        ('NyfkyPzJqNhA=', b'\x2a', 'Tyrone is cool!'),
        ('MTIzNDU2Nzg5MDEyMw==', b'\xde', 'Hello World!'),
        ('SGVsbG8gV29ybGQh', b'\x12', '123456789012'),
    ]
)
def test_reveal_pseudo_secret(obfuscated_secret, pseudo_key, expected):
    assert reveal_pseudo_secret(obfuscated_secret, pseudo_key) == expected

