# Generated test file for file_storage.py

import pathvalidate
import pytest
import tempfile
import stat
import re
from ..file_storage import *
import os
import io





@pytest.fixture
def file_storage():
    return FileStorage('/tmp/test_storage', makedirs=True)

@pytest.mark.parametrize('file_type, expected_ext', [('j', '.json')])
def test_save_valid_file_types(file_storage, file_type, expected_ext):
    data = {'foo': 'bar'}
    relative_path = 'test'
    file_path = file_storage.save(relative_path, data, file_type=file_type)
    assert os.path.exists(file_path)
    assert file_path.endswith(expected_ext)





@pytest.fixture
def storage_path():
    return os.path.realpath('/tmp')

@pytest.fixture
def relative_path():
    return 'test.txt'

@pytest.fixture
def data():
    return 'This is a test.'

@pytest.fixture
def file_type():
    return 't'

@pytest.fixture
def makedirs():
    return False

def test_save_atomic_with_valid_input(storage_path, relative_path, data, file_type, makedirs):
    fs = FileStorage(storage_path, file_type, makedirs)
    dest_path = fs.save_atomic(storage_path, relative_path, data, file_type)
    assert os.path.isfile(dest_path)

def test_save_atomic_with_invalid_input(storage_path, relative_path, data, file_type, makedirs):
    fs = FileStorage(storage_path, file_type, makedirs)
    with pytest.raises(Exception):
        fs.save_atomic(storage_path, relative_path, data, 'x')

def test_save_atomic_with_invalid_storage_path(storage_path, relative_path, data, file_type, makedirs):
    fs = FileStorage(storage_path, file_type, makedirs)
    with pytest.raises(Exception):
        fs.save_atomic('/invalid/path', relative_path, data, file_type)

def test_save_atomic_with_invalid_relative_path(storage_path, relative_path, data, file_type, makedirs):
    fs = FileStorage(storage_path, file_type, makedirs)
    with pytest.raises(Exception):
        fs.save_atomic(storage_path, 'invalid/path', data, file_type)





@pytest.fixture
def file_storage():
    storage_path = './test_files/'
    file_type = 't'
    makedirs = True
    return FileStorage(storage_path, file_type, makedirs)

@pytest.mark.parametrize('relative_path, mode, expected_encoding', [('test.txt', 'r', 'utf-8'), ('test.txt', 'w', 'utf-8')])
def test_open_file(file_storage, relative_path, mode, expected_encoding):
    f = file_storage.open_file(relative_path, mode)
    assert f.encoding == expected_encoding
    assert os.path.exists(file_storage.make_full_path(relative_path))
    os.remove(file_storage.make_full_path(relative_path))





@pytest.fixture
def file_storage():
    storage_path = '/tmp/test_storage'
    return FileStorage(storage_path, file_type='t', makedirs=True)

def test_init(file_storage):
    assert file_storage.storage_path == os.path.realpath('/tmp/test_storage')
    assert file_storage.file_type == 't'

@pytest.mark.parametrize('delete, mode, file_type, expected_mode, expected_encoding', [(False, 'w', 'b', 'w+b', 'utf-8')])
def test_open_temp_parametrized(file_storage, delete, mode, file_type, expected_mode, expected_encoding):
    temp_file = file_storage.open_temp(delete=delete, mode=mode, file_type=file_type)
    assert temp_file is not None
    assert temp_file.name.startswith(file_storage.storage_path)
    assert temp_file.mode == expected_mode
    assert temp_file.encoding == expected_encoding




@pytest.fixture
def file_storage():
    return FileStorage('/tmp/test_storage', 'txt')

@pytest.mark.parametrize('relative_path, expected', [('/tmp/test_storage/file.txt', False), ('/tmp/test_storage/', True)])
def test_has_folder(file_storage, relative_path, expected):
    assert file_storage.has_folder(relative_path) == expected




@pytest.fixture
def file_storage():
    return FileStorage('/tmp/test_dir', 't', makedirs=True)

@pytest.mark.parametrize('relative_path, to_root, expected', [('', True, [])])
def test_list_folder_dirs(file_storage, relative_path, to_root, expected):
    result = file_storage.list_folder_dirs(relative_path, to_root)
    assert result == expected




@pytest.fixture
def test_storage():
    return FileStorage(storage_path='/tmp/test_storage', file_type='t', makedirs=True)

def test_atomic_rename_success(test_storage):
    from_relative_path = 'file1.txt'
    to_relative_path = 'file2.txt'
    test_storage.atomic_rename(from_relative_path, to_relative_path)
    assert os.path.exists(os.path.join(test_storage.storage_path, to_relative_path))

@pytest.mark.parametrize('from_relative_path, to_relative_path', [('file5.txt', 'file6.txt')])
def test_atomic_rename_parametrized(test_storage, from_relative_path, to_relative_path):
    test_storage.atomic_rename(from_relative_path, to_relative_path)
    assert os.path.exists(os.path.join(test_storage.storage_path, to_relative_path))




@pytest.fixture
def file_storage():
    return FileStorage('/tmp', 't')

def test_in_storage_valid_path(file_storage):
    assert file_storage.in_storage('/tmp/file.txt') == True

def test_in_storage_invalid_path(file_storage):
    assert file_storage.in_storage('/tmp2/file.txt') == False

def test_in_storage_none_path(file_storage):
    with pytest.raises(AssertionError):
        file_storage.in_storage(None)

@pytest.mark.parametrize('makedirs', [True, False])
def test_in_storage_makedirs(makedirs):
    file_storage = FileStorage('/tmp', 't', makedirs)
    assert file_storage.in_storage('/tmp/file.txt') == True




@pytest.fixture
def file_storage():
    return FileStorage('/tmp/files', file_type='t', makedirs=True)

def test_in_storage_true(file_storage):
    path = os.path.join(file_storage.storage_path, 'test.txt')
    assert file_storage.in_storage(path) == True

def test_in_storage_false(file_storage):
    path = os.path.join('/tmp/other', 'test.txt')
    assert file_storage.in_storage(path) == False

def test_to_relative_path_valid(file_storage):
    path = os.path.join(file_storage.storage_path, 'test.txt')
    assert file_storage.to_relative_path(path) == 'test.txt'

def test_to_relative_path_invalid(file_storage):
    path = os.path.join('/tmp/other', 'test.txt')
    with pytest.raises(ValueError):
        file_storage.to_relative_path(path)




@pytest.fixture
def storage_path():
    return '/tmp/file_storage'

@pytest.fixture
def file_type():
    return 't'

@pytest.fixture
def makedirs():
    return False

@pytest.fixture
def file_path():
    return '/tmp/file_storage/test.txt'

def test_init_storage_path(storage_path):
    fs = FileStorage(storage_path)
    assert fs.storage_path == os.path.realpath(storage_path)

def test_init_file_type(storage_path, file_type):
    fs = FileStorage(storage_path, file_type)
    assert fs.file_type == file_type

def test_init_makedirs(storage_path, file_type, makedirs):
    fs = FileStorage(storage_path, file_type, makedirs)
    assert os.path.exists(storage_path)

def test_get_file_name_from_file_path(file_path):
    file_name = FileStorage.get_file_name_from_file_path(file_path)
    assert file_name == 'test.txt'






FILE_COMPONENT_INVALID_CHARACTERS = re.compile('[.%{}]')

@pytest.fixture
def file_storage():
    return FileStorage('/tmp')

def test_validate_file_name_component_valid(file_storage):
    file_storage.validate_file_name_component('valid_name')

def test_validate_file_name_component_invalid(file_storage):
    with pytest.raises(pathvalidate.error.InvalidCharError):
        file_storage.validate_file_name_component('invalid.name')

def test_init_makedirs(tmpdir):
    storage_path = str(tmpdir.join('test_dir'))
    file_storage = FileStorage(storage_path, makedirs=True)
    assert os.path.exists(storage_path)

def test_init_no_makedirs(tmpdir):
    storage_path = str(tmpdir.join('test_dir'))
    file_storage = FileStorage(storage_path, makedirs=False)
    assert not os.path.exists(storage_path)





@pytest.fixture
def file_storage():
    return FileStorage('test_storage_path', 't', True)

def test_init_file_storage(file_storage):
    assert file_storage.storage_path == os.path.realpath('test_storage_path')
    assert file_storage.file_type == 't'
    assert os.path.exists('test_storage_path')

