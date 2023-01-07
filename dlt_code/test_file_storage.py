import pytest

from pathlib import Path
from mock import patch

from .file_storage import FileStorage

from .utils import mock_storage


@pytest.fixture
def fs(tmp_path):
    fs = FileStorage(Path(tmp_path / "storage").absolute, "my_file_type")
    yield fs

    if fs.has_folder("my_folder"):
        fs.delete_folder("my_folder")


def test_save_atomic(tmp_path):
    fs = mock_storage(tmp_path / "storage")
    fs.save_atomic("my_file_type", "data")
    assert fs.save("my_file_type", "data") == "my_folder/data"


def test_load_empty(tmp_path):
    fs = mock_storage(tmp_path / "storage")
    with pytest.raises(TypeError):
        fs.load("does_not_exist")

    fs.save_atomic("my_file_type", "data")
    with pytest.raises(FileStorage.ValidationError):
        fs.load("my_file_type")


def test_load_atomic(tmp_path):
    fs = mock_storage(tmp_path / "storage")
    fs.save_atomic("my_file_type", "data")
    data = "data"
    with pytest.raises(FileStorage.ValidationError):
        fs.load("my_file_type", None)
    assert fs.load("my_file_type", "data") == data


def test_load_file_type(tmp_path):
    fs = mock_storage(tmp_path / "storage")
    fs.save_atomic("my_file_type", "data")
    data = "data"
    with pytest.raises(FileStorage.ValidationError):
        fs.load("my_file_type", "does_not_exist")
    assert fs.load("my_file_type", "data") == data


def test_load_file_type_file(tmp_path):
    fs = mock_storage(tmp_path / "storage")
    fs.save_atomic("my_file_type", "data")
    data = "data"
    with pytest.raises(FileStorage.ValidationError):
        fs.load("my_file_type", "does_not_exist")
    assert fs.load("my_file_type", "data") == data


def test_load_file_type_folder(tmp_path):
    fs = mock_storage(tmp_path / "storage")
    fs.save_atomic("my_file_type", "data")
    data = "data"
    with pytest.raises(FileStorage.ValidationError):
        fs.load("my_file_type", "does_not_exist")
    assert fs.load("my_file_type", "data") == data


def test_load_folder(tmp_path):
    fs = mock_storage(tmp_path / "storage")
    fs.save_folder("my_folder")
    assert fs.has_folder("my_folder")
    assert fs.load("my_folder") is True
    assert fs.has_folder("my_folder") is True


def test_load_folder_with_file(tmp_path):
    fs = mock_storage(tmp_path / "storage")
    fs.save_folder("my_folder", "my_file")
    assert fs.has_folder("my_folder")
    assert fs.load("my_folder") is True
    assert fs.has_folder("my_folder") is True
    assert fs.load("my_folder", "my_file") is True
    assert fs.has_folder("my_folder") is True
