# Generated test file for utils.py

import os
from ...utils import *
from os import environ
from unittest.mock import patch
import base64
import hashlib
import secrets
import pytest




@pytest.fixture
def seq():
    return [1, 2, 3, 4, 5, 6, 7, 8, 9]

def test_chunks_length(seq):
    gen = chunks(seq, 3)
    assert len(list(gen)) == 3

def test_chunks_content(seq):
    gen = chunks(seq, 3)
    assert list(gen) == [[1, 2, 3], [4, 5, 6], [7, 8, 9]]




@pytest.fixture
def len_():
    return 16

def test_uniq_id(len_):
    expected_len = len_ * 2
    assert len(uniq_id(len_)) == expected_len

def test_uniq_id_is_hex(len_):
    assert all((c in '0123456789abcdef' for c in uniq_id(len_)))



@pytest.fixture
def input_str():
    return 'test string'

def test_digest128_returns_string(input_str):
    assert isinstance(digest128(input_str), str)





@pytest.fixture
def test_str():
    return 'test'

def test_digest256_type(test_str):
    assert type(digest256(test_str)) == str

def test_digest256_length(test_str):
    assert len(digest256(test_str)) == 44



@pytest.fixture
def true_values():
    return ['yes', 'true', 't', 'y', '1']

@pytest.fixture
def false_values():
    return ['no', 'false', 'f', 'n', '0']

def test_str2bool_true(true_values):
    for value in true_values:
        assert str2bool(value) == True

def test_str2bool_false(false_values):
    for value in false_values:
        assert str2bool(value) == False

def test_str2bool_err():
    with pytest.raises(ValueError):
        str2bool('test')



@pytest.fixture
def sample_dicts():
    return [{'a': {1: 'a'}}, {'b': {2: 'b'}}]

def test_flatten_list_of_dicts(sample_dicts):
    expected = {'a': {1: 'a'}, 'b': {2: 'b'}}
    assert flatten_list_of_dicts(sample_dicts) == expected

def test_flatten_list_of_dicts_with_duplicate_key(sample_dicts):
    sample_dicts.append({'a': {2: 'c'}})
    with pytest.raises(KeyError):
        flatten_list_of_dicts(sample_dicts)



@pytest.fixture
def list_of_str_or_dicts():
    return [{'a': 1}, 'b', {'c': 2}]

def test_flatten_list_of_str_or_dicts(list_of_str_or_dicts):
    expected = {'a': 1, 'b': None, 'c': 2}
    assert flatten_list_of_str_or_dicts(list_of_str_or_dicts) == expected



@pytest.fixture
def dict_of_dicts():
    return {'a': {'x': 1, 'y': 2}, 'b': {'x': 3, 'y': 4}}

def test_flatten_dicts_of_dicts(dict_of_dicts):
    expected = [{'key': 'a', 'x': 1, 'y': 2}, {'key': 'b', 'x': 3, 'y': 4}]
    actual = flatten_dicts_of_dicts(dict_of_dicts)
    assert actual == expected



@pytest.fixture
def dicts_list():
    return [{'key1': 'value1'}, {'key2': 'value2'}, {'key3': 'value3'}]

@pytest.fixture
def tuplified_dicts_list():
    return [{'key': 'key1', 'value': 'value1'}, {'key': 'key2', 'value': 'value2'}, {'key': 'key3', 'value': 'value3'}]

def test_tuplify_list_of_dicts_success(dicts_list, tuplified_dicts_list):
    assert tuplify_list_of_dicts(dicts_list) == tuplified_dicts_list

def test_tuplify_list_of_dicts_failure():
    with pytest.raises(ValueError):
        tuplify_list_of_dicts([{'key1': 'value1', 'key2': 'value2'}])



@pytest.fixture
def _iter():
    return [1, [2, 3], 4, [5, 6]]

@pytest.fixture
def _iter_single_item():
    return [1, 2, 3, 4, 5, 6]

def test_flatten_list_or_items_single_item(_iter_single_item):
    result = list(flatten_list_or_items(_iter_single_item))
    assert result == [1, 2, 3, 4, 5, 6]

def test_flatten_list_or_items(_iter):
    result = list(flatten_list_or_items(_iter))
    assert result == [1, 2, 3, 4, 5, 6]




@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv('TEST_VAR1', 'value1')
    monkeypatch.setenv('TEST_VAR2', 'value2')
    monkeypatch.setenv('TEST_VAR3', 'value3')

def test_filter_env_vars(mock_env):
    envs = ['TEST_VAR1', 'TEST_VAR2', 'TEST_VAR3']
    expected = {'test_var1': 'value1', 'test_var2': 'value2', 'test_var3': 'value3'}
    actual = filter_env_vars(envs)
    assert actual == expected

def test_filter_env_vars_empty(monkeypatch):
    envs = ['TEST_VAR1', 'TEST_VAR2', 'TEST_VAR3']
    monkeypatch.delenv('TEST_VAR1', raising=False)
    monkeypatch.delenv('TEST_VAR2', raising=False)
    monkeypatch.delenv('TEST_VAR3', raising=False)
    expected = {}
    actual = filter_env_vars(envs)
    assert actual == expected



@pytest.fixture
def dest_dict():
    return {'a': 5, 'b': 7, 'c': 9}

@pytest.fixture
def update_dict():
    return {'a': 6, 'b': None, 'd': 10}

def test_update_dict_with_prune(dest_dict, update_dict):
    expected_dict = {'a': 6, 'c': 9, 'd': 10}
    update_dict_with_prune(dest_dict, update_dict)
    assert dest_dict == expected_dict



@pytest.fixture
def complex_dict():
    return {'a': 1, 'b': [2, 3, 4], 'c': {'d': 5, 'e': 6}}

def test_map_nested_in_place(complex_dict):

    def double(x):
        return x * 2
    expected_dict = {'a': 2, 'b': [4, 6, 8], 'c': {'d': 10, 'e': 12}}
    map_nested_in_place(double, complex_dict)
    assert complex_dict == expected_dict



def test_is_interactive_with_file():
    import __main__ as main
    main.__file__ = 'test.py'
    assert is_interactive() == False



@pytest.fixture
def empty_dict():
    return {}

@pytest.fixture
def none_dict():
    return {'a': None, 'b': None}

@pytest.fixture
def non_none_dict():
    return {'a': None, 'b': 1, 'c': 2}

def test_empty_dict(empty_dict):
    assert dict_remove_nones_in_place(empty_dict) == {}

def test_none_dict(none_dict):
    assert dict_remove_nones_in_place(none_dict) == {}

def test_non_none_dict(non_none_dict):
    assert dict_remove_nones_in_place(non_none_dict) == {'b': 1, 'c': 2}




@pytest.fixture
def env_setup():
    os.environ['TEST_VAR'] = 'test_value'
    yield
    del os.environ['TEST_VAR']

def test_with_custom_environ_preserves_env_vars(env_setup):

    @with_custom_environ
    def test_func():
        assert os.environ['TEST_VAR'] == 'test_value'
    test_func()

def test_with_custom_environ_restores_env_vars(env_setup):

    @with_custom_environ
    def test_func():
        os.environ['TEST_VAR'] = 'new_value'
    test_func()
    assert os.environ['TEST_VAR'] == 'test_value'



@pytest.fixture
def mode():
    return 'rb'

def test_encoding_for_mode_with_b(mode):
    assert encoding_for_mode(mode) == None

def test_encoding_for_mode_without_b(mode):
    mode = 'r'
    assert encoding_for_mode(mode) == 'utf-8'




@pytest.fixture
def mock_sys_argv(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['test_file.py'])

def test_main_module_file_path_valid(mock_sys_argv):
    with patch('os.path.isfile', return_value=True):
        result = main_module_file_path()
        assert result == 'test_file.py'

def test_main_module_file_path_invalid(mock_sys_argv):
    with patch('os.path.isfile', return_value=False):
        result = main_module_file_path()
        assert result == None




@pytest.fixture
def curr_dir():
    curr_dir = os.path.abspath(os.getcwd())
    return curr_dir

@pytest.fixture
def path():
    path = os.path.abspath('/home/user/')
    return path

def test_set_working_dir_no_path(curr_dir):
    with set_working_dir(None) as p:
        assert p == None
        assert os.getcwd() == curr_dir



@pytest.fixture
def test_function():

    def test_function_inner(x: int):
        return x * 2
    return test_function_inner

@pytest.fixture
def test_class():

    class TestClass:

        def test_method(self, x: int):
            return x * 2
    return TestClass

@pytest.fixture
def test_lambda():
    return lambda x: x * 2

def test_get_callable_name_function(test_function):
    name = get_callable_name(test_function)
    assert name == 'test_function_inner'

def test_get_callable_name_class(test_class):
    name = get_callable_name(test_class)
    assert name == 'TestClass'



def test_get_callable_name():

    def inner_func():
        pass
    assert get_callable_name(inner_func) == 'inner_func'

@pytest.mark.parametrize('f, expected', [(lambda x: x, '<lambda>'), (max, 'max'), (test_get_callable_name, 'test_get_callable_name')])
def test_get_callable_name_lambda(f, expected):
    assert get_callable_name(f) == expected

