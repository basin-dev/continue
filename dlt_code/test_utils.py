
from .test_util import str2bool, str2int, str2float
import pytest

from .utils import (
    flatten_list_of_str_or_dicts,
    flatten_dicts_of_dicts,
    tuplify_list_of_dicts,
    main_module_file_path,
    set_working_dir,
    get_callable_name,
    is_inner_callable,
)


@pytest.mark.parametrize("str", [True, False, "hello world", "1", "2", "3", "str", "str", "str", "str", "str", "str",])
def test_str2bool(str) -> None:
    assert str2bool(str)


@pytest.mark.parametrize("str", [True, False, "hello world", "1", "2", "3", "str", "str", "str", "str", "str", "str",])
def test_str2int(str) -> None:
    assert str2int(str)


@pytest.mark.parametrize("str", [True, False, "hello world", "1", "2", "3", "str", "str", "str", "str", "str", "str",])
def test_str2float(str) -> None:
    assert str2float(str)


@pytest.mark.parametrize("str", [True, False, "hello world", "1", "2", "3", "str", "str", "str", "str", "str", "str",])
def test_str2bool_empty(str) -> None:
    with pytest.raises(ValueError):
        str2bool(str)


def test_str2bool_non_string(self) -> None:
    assert not str2bool("hello world")


def test_str2bool_not_true(self) -> None:
    assert not str2bool(True)


def test_str2bool_not_false(self) -> None:
    assert str2bool(False)


def test_str2bool_not_int(self) -> None:
    assert not str2bool(1)


def test_str2bool_not_float(self) -> None:
    assert not str2bool(3.14)


def test_str2bool_not_non_string(self) -> None:
    assert not str2bool("hello")


def test_str2bool_not_int_or_float(self) -> None:
    assert not str2bool(1.2)
    assert not str2bool(3.14)


def test_str2bool_not_non_string_or_int(self) -> None:
    assert not str2bool("hello world")
    assert not str2bool(1)


def test_str2bool_not_non_string_or_float(self) -> None:
    assert not str2bool("hello world")
    assert not str2bool(3.14)


def test_str2bool_not_non_string_or_int_or_float(self) -> None:
    assert not str2bool("hello world")
    assert not str2bool(1)
    assert not str2bool(3.14)


def test_str2bool_non_string_or_int_or_float(self) -> None:
    assert not str2bool("hello world")
    assert not str2bool(1)
    assert not str2bool(3.14)
