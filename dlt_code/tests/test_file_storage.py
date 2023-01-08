# Generated test file for file_storage.py

import shutil
import pathvalidate
import os 
import json
import pytest
import re
import stat
import tempfile
import io
from unittest import mock
from typing import IO, Any
from ..file_storage import *

@pytest.fixture
def file_storage():
    file_storage = FileStorage(tempfile.mkdtemp(), makedirs=True)
    return file_storage

@pytest.mark.parametrize('file_type', ['t', 'b'])
def test_file_type(file_storage, file_type):
    file_storage.file_type = file_type
    assert file_storage.file_type == file_type

def test_init(file_storage):
    # Check that the storage_path exists
    assert os.path.exists(file_storage.storage_path) 

# @pytest.mark.parametrize('relative_path, data, expected_path', [
#     ('test1.txt', 'some data', os.path.join(file_storage.storage_path, 'test1.txt')),
#     ('test2.txt', 'some other data', os.path.join(file_storage.storage_path, 'test2.txt'))
# ])
# def test_save(file_storage, relative_path, data, expected_path):
#     # Check that the file is saved
#     assert file_storage.save(relative_path, data) == expected_path
#     assert os.path.exists(expected_path) 
#     # Check that the data is written correctly
#     with open(expected_path, 'r') as f:
#         assert f.read() == data


@pytest.fixture
def file_storage():
    return FileStorage('/tmp', 't', True)

def test_save_atomic_file_type(file_storage):
    assert file_storage.file_type == 't'

def test_save_atomic_makedirs(file_storage):
    assert os.path.isdir(file_storage.storage_path)

def test_save_atomic_file_created(file_storage):
    data = 'test'
    relative_path = 'test.txt'
    storage_path = file_storage.storage_path
    dest_path = file_storage.save_atomic(storage_path, relative_path, data)
    assert os.path.isfile(dest_path)
    os.remove(dest_path)

def test_save_atomic_file_not_created(file_storage):
    data = 'test'
    relative_path = 'test.txt'
    storage_path = file_storage.storage_path
    dest_path = file_storage.save_atomic(storage_path, relative_path, None)
    assert not os.path.isfile(dest_path)


@pytest.fixture
def fs_instance():
    return FileStorage('/home/jane/test_files', 't', True)

def test_load_with_valid_input(fs_instance):
    test_data = '{"name": "Jane Doe"}'
    relative_path = '/home/jane/test_files/test_file.json'
    with open(relative_path, 'w') as f:
        f.write(test_data)
    result = fs_instance.load(relative_path)
    assert result == test_data

def test_load_with_invalid_input(fs_instance):
    with pytest.raises(FileNotFoundError):
        fs_instance.load('/home/jane/invalid/path/test_file.json')

@pytest.mark.parametrize('file_type, expected', [
    ('t', 'text'),
    ('b', 'binary'),
    ('f', 'file'),
    ('i', 'image')
])
def test_file_type(fs_instance, file_type, expected):
    fs_instance.file_type = file_type
    assert fs_instance.file_type == expected


@pytest.fixture
def temp_dir():
    dir_path = tempfile.mkdtemp()
    yield dir_path
    shutil.rmtree(dir_path)

@pytest.fixture
def file_storage(temp_dir):
    file_storage = FileStorage(temp_dir)
    yield file_storage

@pytest.mark.parametrize('relative_path', [
    'file1.txt',
    'file2.txt',
    'file3.txt',
    'subdir1/file1.txt',
    'subdir1/file2.txt',
    'subdir2/file1.txt',
    'subdir2/file2.txt',
    ])
def test_delete(file_storage, relative_path):
    file_path = file_storage.make_full_path(relative_path)
    open(file_path, 'w').close()
    file_storage.delete(relative_path)
    assert not os.path.exists(file_path)

def test_delete_nonexistent_file(file_storage):
    with pytest.raises(FileNotFoundError):
        file_storage.delete('nonexistent_file.txt')


@pytest.fixture
def file_storage(tmpdir):
    storage_path = str(tmpdir)
    return FileStorage(storage_path)

def test_delete_folder_non_existent(file_storage):
    with pytest.raises(NotADirectoryError):
        file_storage.delete_folder("test_folder")

def test_delete_folder_not_empty(file_storage):
    test_folder = os.path.join(file_storage.storage_path, "test_folder")
    os.mkdir(test_folder)
    with open(os.path.join(test_folder, "test_file.txt"), "w+") as f:
        f.write("test")
    with pytest.raises(OSError):
        file_storage.delete_folder("test_folder")

def test_delete_folder_recursively(file_storage):
    test_folder = os.path.join(file_storage.storage_path, "test_folder")
    os.mkdir(test_folder)
    with open(os.path.join(test_folder, "test_file.txt"), "w+") as f:
        f.write("test")
    file_storage.delete_folder("test_folder", recursively=True)
    assert not os.path.exists(test_folder)

def test_delete_folder_read_only(file_storage):
    test_folder = os.path.join(file_storage.storage_path, "test_folder")
    os.mkdir(test_folder)
    os.chmod(test_folder, 0o444)
    with open(os.path.join(test_folder, "test_file.txt"), "w+") as f:
        f.write("test")
    file_storage.delete_folder("test_folder", recursively=True, delete_ro=True)
    assert not os.path.exists(test_folder)


@pytest.fixture
def file_storage():
    return FileStorage("./test_files", makedirs=True)
    
@pytest.mark.parametrize("file_name, mode, expected_result", [
    ("test.txt", "r", io.TextIOWrapper),
    ("test.txt", "w", io.TextIOWrapper),
    ("test.txt", "a", io.TextIOWrapper),
    ("test.bin", "rb", io.BufferedReader),
    ("test.bin", "wb", io.BufferedWriter),
    ("test.bin", "ab", io.BufferedWriter),
])
def test_open_file(file_name, mode, expected_result, file_storage):
    result = file_storage.open_file(file_name, mode)
    assert isinstance(result, expected_result)
    assert result.mode == mode + file_storage.file_type
    os.remove(file_storage.make_full_path(file_name))

def test_open_file_no_file_type(file_storage):
    result = file_storage.open_file("test2.txt", "r")
    assert isinstance(result, io.TextIOWrapper)
    assert result.mode == "r" + file_storage.file_type
    os.remove(file_storage.make_full_path("test2.txt"))


@pytest.fixture
def file_storage():
    return FileStorage('/test/path', file_type='txt', makedirs=True)

def test_file_storage_path(file_storage):
    assert file_storage.storage_path == os.path.realpath('/test/path')

def test_file_storage_file_type(file_storage):
    assert file_storage.file_type == 'txt'

def test_open_temp_default_mode(file_storage):
    f = file_storage.open_temp()
    assert f.mode == "wt"
    f.close()

def test_open_temp_delete_true(file_storage):
    f = file_storage.open_temp(delete=True)
    assert f.delete == True
    f.close()

def test_open_temp_mode_r(file_storage):
    f = file_storage.open_temp(mode="r")
    assert f.mode == "rt"
    f.close()

def test_open_temp_file_type_json(file_storage):
    f = file_storage.open_temp(file_type="json")
    assert f.mode == "wtjson"
    f.close()


@pytest.fixture
def storage():
    storage_path = "./storage_test"
    return FileStorage(storage_path, makedirs=True)

@pytest.mark.parametrize("relative_path,expected_result", [
    ("test.txt", True),
    ("test/test.txt", True),
    ("test/test2.txt", True),
    ("test/test3.txt", False)
])
def test_has_file(storage, relative_path, expected_result):
    result = storage.has_file(relative_path)
    assert result == expected_result


@pytest.fixture
def storage_path():
    return '/tmp/stor'

@pytest.fixture
def file_type():
    return 't'

@pytest.fixture
def makedirs():
    return False

def test_has_folder_when_path_exists(storage_path, file_type, makedirs):
    fs = FileStorage(storage_path, file_type, makedirs)
    os.makedirs(storage_path)
    assert fs.has_folder(storage_path)

def test_has_folder_when_path_does_not_exist(storage_path, file_type, makedirs):
    fs = FileStorage(storage_path, file_type, makedirs)
    assert not fs.has_folder(storage_path)

def test_has_folder_with_relative_path(storage_path, file_type, makedirs):
    fs = FileStorage(storage_path, file_type, makedirs)
    os.makedirs(os.path.join(storage_path, 'relative_path'))
    assert fs.has_folder('relative_path')

def test_has_folder_with_invalid_relative_path(storage_path, file_type, makedirs):
    fs = FileStorage(storage_path, file_type, makedirs)
    assert not fs.has_folder('invalid_relative_path')


@pytest.fixture
def fs():
    return FileStorage('/tmp/test', makedirs=True)

def test_list_folder_files(fs):
    os.makedirs('/tmp/test/test_dir', exist_ok=True)
    os.makedirs('/tmp/test/test_dir/sub_dir', exist_ok=True)
    with open('/tmp/test/test_dir/file1.txt', 'w') as f:
        f.write("test")
    with open('/tmp/test/test_dir/sub_dir/file2.txt', 'w') as f:
        f.write("test")
    # Test to_root=True
    assert fs.list_folder_files('/tmp/test/test_dir', to_root=True) == ['/tmp/test/test_dir/file1.txt', '/tmp/test/test_dir/sub_dir/file2.txt']
    # Test to_root=False
    assert fs.list_folder_files('/tmp/test/test_dir', to_root=False) == ['file1.txt', 'file2.txt']


@pytest.fixture
def file_storage():
    return FileStorage('/tmp/storage', file_type='t', makedirs=True)

@pytest.mark.parametrize('relative_path, to_root, expected', [
    ('/test', True, ['/test/a']),
    ('/test', False, ['a']),
])
def test_list_folder_dirs(file_storage, relative_path, to_root, expected):
    os.makedirs('/tmp/storage/test/a')
    result = file_storage.list_folder_dirs(relative_path, to_root)
    assert result == expected


@pytest.fixture
def file_storage():
    return FileStorage("test_path", "t", False)

@pytest.mark.parametrize("relative_path,exists_ok", [
    ("relative_path1", True),
    ("relative_path2", False)
])
def test_create_folder(file_storage, relative_path, exists_ok):
    file_storage.create_folder(relative_path, exists_ok)
    assert os.path.exists(file_storage.make_full_path(relative_path))

def test_create_folder_wrong_relative_path(file_storage):
    with pytest.raises(FileNotFoundError):
        file_storage.create_folder("")


@pytest.fixture
def filestorage():
    return FileStorage('./test_filestorage', 't')

def test_link_file_valid_inputs(filestorage):
    from_relative_path = 'test.txt'
    to_relative_path = 'test_copy.txt'
    
    filestorage.link_hard(from_relative_path, to_relative_path)
    assert os.path.exists('./test_filestorage/test_copy.txt')

def test_link_file_invalid_inputs(filestorage):
    from_relative_path = 'invalid_file.txt'
    to_relative_path = 'test_copy.txt'
    
    with pytest.raises(FileNotFoundError):
        filestorage.link_hard(from_relative_path, to_relative_path)

def test_link_file_same_inputs(filestorage):
    from_relative_path = 'test.txt'
    to_relative_path = 'test.txt'
    
    with pytest.raises(FileExistsError):
        filestorage.link_hard(from_relative_path, to_relative_path)


@pytest.fixture
def file_storage():
    path = tempfile.mkdtemp()
    yield FileStorage(path, makedirs=True)
    shutil.rmtree(path)

def test_init(file_storage):
    assert os.path.exists(file_storage.storage_path)

def test_atomic_rename_exists(file_storage):
    test_from = os.path.join(file_storage.storage_path, "from.txt")
    test_to = os.path.join(file_storage.storage_path, "to.txt")
    with open(test_from, "w") as fp:
        fp.write("test")
    file_storage.atomic_rename("from.txt", "to.txt")
    assert os.path.exists(test_to) and not os.path.exists(test_from)

def test_atomic_rename_not_exist(file_storage):
    with pytest.raises(FileNotFoundError):
        file_storage.atomic_rename("from.txt", "to.txt")


@pytest.fixture
def file_storage():
    return FileStorage('./test_files')

# Test that the path provided is absolute
def test_in_storage_with_absolute_path(file_storage):
    path = '/tmp/test.txt'
    assert not file_storage.in_storage(path)

# Test that the path provided is relative
def test_in_storage_with_relative_path(file_storage):
    path = './test.txt'
    assert file_storage.in_storage(path)

# Test that the provided path is not in the storage path
def test_in_storage_with_not_in_storage_path(file_storage):
    path = '../test.txt'
    assert not file_storage.in_storage(path)

# Test that the provided path is in the storage path
def test_in_storage_with_in_storage_path(file_storage):
    path = './test_files/test.txt'
    assert file_storage.in_storage(path)

# Test that the provided path is None
def test_in_storage_with_None(file_storage):
    path = None
    with pytest.raises(AssertionError):
        file_storage.in_storage(path)


@pytest.fixture
def storage():
    storage_path = os.path.realpath("storage")
    return FileStorage(storage_path, makedirs=True)

@pytest.mark.parametrize("path, expected_path",
                         [("", ""),
                          ("/test.txt", "test.txt"),
                          ("test.txt", "test.txt"),
                          ("../test.txt", "test.txt"),
                          ("/../test.txt", "test.txt")])
def test_to_relative_path(storage, path, expected_path):
    assert storage.to_relative_path(path) == expected_path
    
@pytest.mark.parametrize("path",
                         ["/../../test.txt",
                          "/test/../../test.txt"])
def test_to_relative_path_exception(storage, path):
    with pytest.raises(ValueError):
        storage.to_relative_path(path)


@pytest.fixture
def file_storage():
    return FileStorage('path', 't', True)

def test_make_full_path_with_absolute_path(file_storage):
    absolute_path = '/test/abs/path'
    expected_result = os.path.realpath(os.path.join(file_storage.storage_path, absolute_path))
    assert file_storage.make_full_path(absolute_path) == expected_result

def test_make_full_path_with_relative_path(file_storage):
    relative_path = 'test/rel/path'
    expected_result = os.path.realpath(os.path.join(file_storage.storage_path, relative_path))
    assert file_storage.make_full_path(relative_path) == expected_result

def test_make_full_path_with_empty_string(file_storage):
    empty_string = ''
    expected_result = os.path.realpath(file_storage.storage_path)
    assert file_storage.make_full_path(empty_string) == expected_result

def test_make_full_path_with_none(file_storage):
    with pytest.raises(TypeError):
        file_storage.make_full_path(None)


@pytest.fixture
def fs(tmp_path):
    return FileStorage(tmp_path)

@pytest.mark.parametrize('wd_relative_path,expected_path', [
    ('/home/user/foo/bar', 'foo/bar'),
    ('~/foo/bar', 'foo/bar'),
    ('../foo/bar', 'foo/bar'),
    ('../../foo/bar', '../foo/bar'),
    ('../../../foo/bar', '../../foo/bar')
])
def test_from_wd_to_relative_path(fs, wd_relative_path, expected_path):
    assert fs.from_wd_to_relative_path(wd_relative_path) == expected_path


@pytest.fixture
def storage():
    storage_path = os.getcwd()
    return FileStorage(storage_path, file_type='t', makedirs=True)

def test_from_relative_path_to_wd_with_correct_input(storage):
    relative_path = 'test_path'
    expected_path = os.path.join(storage.storage_path, relative_path)
    assert storage.from_relative_path_to_wd(relative_path) == expected_path

def test_from_relative_path_to_wd_with_invalid_input(storage):
    relative_path = None
    with pytest.raises(TypeError):
        storage.from_relative_path_to_wd(relative_path)

# @pytest.mark.parametrize('relative_path, expected_path', [
#     ('test_path_1', os.path.join(storage.storage_path, 'test_path_1')),
#     ('test_path_2', os.path.join(storage.storage_path, 'test_path_2')),
#     ('test_path_3', os.path.join(storage.storage_path, 'test_path_3')),
#     ('test_path_4', os.path.join(storage.storage_path, 'test_path_4')),
# ])
# def test_from_relative_path_to_wd_with_multiple_inputs(storage, relative_path, expected_path):
#     assert storage.from_relative_path_to_wd(relative_path) == expected_path


@pytest.fixture
def fstor():
    return FileStorage('/tmp', 't', True)

def test_init_makedirs(fstor):
    assert os.path.exists('/tmp')

@pytest.mark.parametrize("file_path, expected", [
    ('/tmp/my_file.txt', 'my_file.txt'),
    ('/tmp/subdir/my_file.txt', 'my_file.txt'),
    ('/tmp/subdir/subsubdir/my_file.txt', 'my_file.txt'),
])
def test_get_file_name_from_file_path(fstor, file_path, expected):
    assert fstor.get_file_name_from_file_path(file_path) == expected


FILE_COMPONENT_INVALID_CHARACTERS = re.compile(r'[.%{}]')

@pytest.fixture
def file_storage_object():
    return FileStorage("test_path", "t", True)

def test_init_without_error(file_storage_object):
    assert file_storage_object.storage_path == os.path.realpath("test_path")
    assert file_storage_object.file_type == "t"

def test_init_makedirs(file_storage_object):
    assert os.path.exists("test_path")

def test_validate_file_name_component_no_error():
    FileStorage.validate_file_name_component("name123")

@pytest.mark.parametrize("name", ["\\name", "name/", "name.", "name%", "name{", "name}"])
def test_validate_file_name_component_error(name):
    with pytest.raises(pathvalidate.error.InvalidCharError):
        FileStorage.validate_file_name_component(name)


@pytest.fixture
def storage():
    return FileStorage('storage_path', 't', True)

def test_initialization_storage_path_exists(storage):
    assert os.path.exists(storage.storage_path)

def test_initialization_file_type_is_correct(storage):
    assert storage.file_type == 't'

def test_initialization_makedirs_creates_dirs(storage):
    assert os.path.isdir(storage.storage_path)

def test_rmtree_del_ro_is_os_unlink(storage):
    assert storage.rmtree_del_ro(os.unlink, 'name', 'exc') == None

def test_rmtree_del_ro_is_os_remove(storage):
    assert storage.rmtree_del_ro(os.remove, 'name', 'exc') == None

def test_rmtree_del_ro_is_os_rmdir(storage):
    assert storage.rmtree_del_ro(os.rmdir, 'name', 'exc') == None

# def test_rmtree_del_ro_is_os_chmod_for_dirs(storage):
#     assert storage.rmtree_del_ro(os.rmdir, 'name', 'exc') == os.chmod(name, stat.S_IWRITE)

# def test_rmtree_del_ro_is_os_chmod_for_files(storage):
#     assert storage.rmtree_del_ro(os.remove, 'name', 'exc') == os.chmod(name, stat.S_IWRITE)


@pytest.fixture
def storage_path():
    return os.path.join(os.getcwd(), 'test_files')

@pytest.fixture
def file_storage(storage_path):
    return FileStorage(storage_path, makedirs=True)

@pytest.fixture
def sample_data():
    return {'key1': 'value1', 'key2': 'value2'}

# @pytest.mark.parametrize('relative_path, expected_file', [
#     ('foo/bar.json', os.path.join(storage_path, 'foo/bar.json')),
#     ('baz/quux.yaml', os.path.join(storage_path, 'baz/quux.yaml')),
#     ('spam/eggs.txt', os.path.join(storage_path, 'spam/eggs.txt'))
# ])
# def test_save_creates_file(file_storage, sample_data, relative_path, expected_file):
#     # test the file is created
#     file_storage.save(relative_path, sample_data)
#     assert os.path.exists(expected_file)

# @pytest.mark.parametrize('relative_path, expected_file', [
#     ('foo/bar.json', os.path.join(storage_path, 'foo/bar.json')),
#     ('baz/quux.yaml', os.path.join(storage_path, 'baz/quux.yaml')),
#     ('spam/eggs.txt', os.path.join(storage_path, 'spam/eggs.txt'))
# ])
# def test_save_writes_correct_data(file_storage, sample_data, relative_path, expected_file):
#     # test the data written is correct
#     file_storage.save(relative_path, sample_data)
#     with open(expected_file, 'r') as f:
#         assert sample_data == f.read()


@pytest.fixture
def test_file():
    with tempfile.NamedTemporaryFile() as f:
        f.write(b'Some data')
        f.seek(0)
        yield f

@pytest.fixture
def storage_path():
    with tempfile.TemporaryDirectory() as d:
        yield d

@pytest.fixture
def file_storage(storage_path):
    return FileStorage(storage_path)

def test_init_with_makedirs(file_storage):
    assert os.path.exists(file_storage.storage_path)

def test_init_without_makedirs(storage_path):
    file_storage = FileStorage(storage_path, makedirs=False)
    assert not os.path.exists(file_storage.storage_path)

def test_save_atomic_creates_file(file_storage, test_file):
    dest_path = file_storage.save_atomic(file_storage.storage_path, 'test.txt', test_file.read())
    assert os.path.exists(dest_path)

def test_save_atomic_saves_file_correctly(file_storage, test_file):
    dest_path = file_storage.save_atomic(file_storage.storage_path, 'test.txt', test_file.read())
    with open(dest_path, 'rb') as f:
        assert f.read() == test_file.read()

def test_save_atomic_file_type(file_storage, test_file):
    dest_path = file_storage.save_atomic(file_storage.storage_path, 'test.txt', test_file.read(), file_type='b')
    assert os.path.splitext(dest_path)[-1] == '.bin'


@pytest.fixture
def tmp_dir():
    tmp_dir = tempfile.mkdtemp()
    yield tmp_dir
    shutil.rmtree(tmp_dir)

@pytest.fixture
def file_storage(tmp_dir):
    return FileStorage(tmp_dir, file_type='t', makedirs=True)

def test_init(file_storage):
    assert isinstance(file_storage, FileStorage)
    assert file_storage.storage_path == os.path.realpath(tmp_dir)
    assert file_storage.file_type == 't'

@pytest.mark.parametrize('relative_path, expected_output', [
    ('test_file.txt', 'Hello World!'),
    ('test_file2.txt', 'Foo Bar!'),
])
def test_load(file_storage, tmp_dir, relative_path, expected_output):
    file_path = os.path.join(tmp_dir, relative_path)
    with open(file_path, 'w') as text_file:
        text_file.write(expected_output)
    output = file_storage.load(relative_path)
    assert output == expected_output


@pytest.fixture
def file_storage():
    tmp_path = tempfile.mkdtemp()
    fs = FileStorage(tmp_path, file_type='t', makedirs=True)
    return fs

@pytest.mark.parametrize("relative_path", [
    "test.txt",
    "subdir/test.txt",
    "subdir/subdir2/test.txt"
])
def test_delete_success(file_storage, relative_path):
    full_path = file_storage.make_full_path(relative_path)
    with open(full_path, "w") as f:
        f.write("test")
    file_storage.delete(relative_path)
    assert not os.path.exists(full_path)

@pytest.mark.parametrize("relative_path", [
    "test.txt",
    "subdir/test.txt",
    "subdir/subdir2/test.txt"
])
def test_delete_error(file_storage, relative_path):
    with pytest.raises(FileNotFoundError):
        file_storage.delete(relative_path)


@pytest.fixture
def file_storage(tmpdir):
    storage_path = tmpdir.mkdir("file_storage")
    return FileStorage(storage_path)

def test_delete_folder_not_dir(file_storage):
    with pytest.raises(NotADirectoryError):
        file_storage.delete_folder('not_a_dir')

def test_delete_folder_empty_dir(file_storage):
    os.mkdir(file_storage.make_full_path('empty_dir'))
    file_storage.delete_folder('empty_dir')
    assert not os.path.exists(file_storage.make_full_path('empty_dir'))

def test_delete_folder_non_empty_dir(file_storage):
    os.mkdir(file_storage.make_full_path('non_empty_dir'))
    with open(file_storage.make_full_path('non_empty_dir/file.txt'), 'w') as f:
        f.write('file contents')
    file_storage.delete_folder('non_empty_dir')
    assert not os.path.exists(file_storage.make_full_path('non_empty_dir'))

@mock.patch('shutil.rmtree')
def test_delete_folder_recursively_without_delete_ro(file_storage, mock_rmtree):
    os.mkdir(file_storage.make_full_path('non_empty_dir'))
    with open(file_storage.make_full_path('non_empty_dir/file.txt'), 'w') as f:
        f.write('file contents')
    file_storage.delete_folder('non_empty_dir', recursively=True)
    mock_rmtree.assert_called_with(file_storage.make_full_path('non_empty_dir'))

# @mock.patch('shutil.rmtree')
# def test_delete_folder_recursively_with_delete_ro(file_storage, mock_rmtree):


@pytest.fixture
def file_storage():
    return FileStorage("/tmp/file_storage", file_type="t", makedirs=True)

@pytest.mark.parametrize("relative_path,mode,expected", [
    ("foo.txt", "r", "/tmp/file_storage/foo.txt"),
    ("bar/baz.txt", "w", "/tmp/file_storage/bar/baz.txt"),
    ("qux.txt", "a", "/tmp/file_storage/qux.txt")
])
def test_open_file(file_storage, relative_path, mode, expected):
    assert file_storage.open_file(relative_path, mode).name == expected

@pytest.fixture
def file_storage():
    storage_path = os.path.realpath('/tmp')
    file_type = 't'
    makedirs = False
    return FileStorage(storage_path, file_type, makedirs)

@pytest.mark.parametrize("delete, mode, file_type, expected_result", [
    (False, 'w', None, 'wt'),
    (True, 'wb', 'b', 'wbb'),
    (False, 'a', 't', 'at')
])
def test_open_temp(file_storage, delete, mode, file_type, expected_result):
    temp_file = file_storage.open_temp(delete, mode, file_type)
    assert temp_file.mode == expected_result


@pytest.fixture
def file_storage():
    return FileStorage("/test/path", "t")

@pytest.mark.parametrize("relative_path, expected_result",
                         [("/test_file.txt", True),
                          ("/test_dir/test_file.txt", False)])
def test_has_file(file_storage, relative_path, expected_result):
    result = file_storage.has_file(relative_path)
    assert result == expected_result


@pytest.fixture
def storage():
    return FileStorage("/test/path", "t", True)

@pytest.mark.parametrize("relative_path, expected_result", [
    ("test_folder", True),
    ("non_existing_folder", False)
])
def test_has_folder(storage, relative_path, expected_result):
    assert storage.has_folder(relative_path) == expected_result

# test_list_files

@pytest.fixture
def file_storage():
    return FileStorage('test/test_directory', 't', makedirs=True)

def test_list_files_empty_folder(file_storage):
    file_storage.list_folder_files('test/test_directory')
    assert os.listdir('test/test_directory') == []

def test_list_files_non_empty_folder(file_storage):
    test_file = open('test/test_directory/test.txt', 'w+')
    test_file.write('test_content')
    test_file.close()

    file_names = file_storage.list_folder_files('test/test_directory')
    assert file_names == ['test.txt']

def test_list_files_to_root(file_storage):
    file_names = file_storage.list_folder_files('test/test_directory', to_root=True)
    assert file_names == ['test/test_directory/test.txt']


@pytest.fixture
def file_storage():
    return FileStorage(storage_path="test_storage", file_type="txt", makedirs=True)

def test_list_folder_dirs_empty_folder(file_storage):
    """Test list_folder_dirs on an empty folder"""
    relative_path = ""
    to_root = True
    expected_result = []
    actual_result = file_storage.list_folder_dirs(relative_path, to_root)
    assert actual_result == expected_result

def test_list_folder_dirs_non_empty_folder(file_storage):
    """Test list_folder_dirs on a non-empty folder"""
    relative_path = ""
    to_root = True
    os.makedirs(os.path.join(file_storage.storage_path, "test_dir"))
    expected_result = ["test_dir"]
    actual_result = file_storage.list_folder_dirs(relative_path, to_root)
    assert actual_result == expected_result

def test_list_folder_dirs_non_empty_folder_to_root_false(file_storage):
    """Test list_folder_dirs on a non-empty folder with to_root=False"""
    relative_path = ""
    to_root = False
    os.makedirs(os.path.join(file_storage.storage_path, "test_dir"))
    expected_result = ["test_dir"]
    actual_result = file_storage.list_folder_dirs(relative_path, to_root)
    assert actual_result == expected_result

# def test_list_folder_dirs_non_empty_subfolder(file_storage):
#     """Test list_folder_dirs on a non-empty subfolder"""
#     relative_path = "test_dir"
#     to_root = True
#     os.makedirs(os.path.join(file_storage.storage_path, "test_dir"))
#     os.makedirs(os.path.join(file_storage.storage_path, "test_dir",



@pytest.fixture
def file_storage():
    return FileStorage('/file/storage', 't', True)


def test_create_folder_exists_ok_true(file_storage):
    file_storage.create_folder('/test', True)
    assert os.path.exists(file_storage.make_full_path('/test'))


def test_create_folder_exists_ok_false(file_storage):
    with pytest.raises(OSError):
        file_storage.create_folder('/test', False)


@pytest.mark.parametrize('relative_path', [
    '/test1',
    '/test2',
    '/test3',
])
def test_create_folder_exists_ok_true_multiple(file_storage, relative_path):
    file_storage.create_folder(relative_path, True)
    assert os.path.exists(file_storage.make_full_path(relative_path))


@pytest.fixture
def file_storage():
    return FileStorage('/tmp/file_storage', 't', makedirs=True)

@pytest.fixture
def sample_files():
    with open('/tmp/file_storage/test1.txt', 'w') as f1:
        f1.write('test1')
    with open('/tmp/file_storage/test2.txt', 'w') as f2:
        f2.write('test2')

def test_init_makedirs(file_storage):
    assert os.path.exists('/tmp/file_storage/')

def test_link_hard(file_storage, sample_files):
    file_storage.link_hard('test1.txt', 'test2.txt')
    assert os.path.exists('/tmp/file_storage/test2.txt')
    with open('/tmp/file_storage/test2.txt') as f:
        assert f.read() == 'test1'

def test_link_hard_invalid_file(file_storage):
    with pytest.raises(FileNotFoundError):
        file_storage.link_hard('invalid.txt', 'test2.txt')


@pytest.fixture
def file_storage():
    storage_path = './test'
    fs = FileStorage(storage_path, makedirs=True)
    return fs

def test_init_with_invalid_file_type(file_storage):
    with pytest.raises(ValueError):
        fs = FileStorage(file_storage.storage_path, file_type='invalid')

@pytest.mark.parametrize(
    'from_relative_path, to_relative_path',
    [
        ('a.txt', 'b.txt'),
        ('a.txt', 'c/d/e.txt'),
        ('a/b/c.txt', 'd/e/f.txt')
    ]
)
def test_atomic_rename(file_storage, from_relative_path, to_relative_path):
    from_full_path = file_storage.make_full_path(from_relative_path)
    to_full_path = file_storage.make_full_path(to_relative_path)
    with open(from_full_path, 'w+') as f:
        f.write('test')
    assert os.path.exists(from_full_path)
    file_storage.atomic_rename(from_relative_path, to_relative_path)
    assert os.path.exists(to_full_path)
    assert not os.path.exists(from_full_path)


@pytest.fixture
def file_storage():
    return FileStorage(storage_path='/tmp', file_type='t', makedirs=True)

def test_in_storage_valid_path(file_storage):
    assert file_storage.in_storage('/tmp/test.txt') == True

def test_in_storage_invalid_path(file_storage):
    assert file_storage.in_storage('/home/test.txt') == False

def test_in_storage_invalid_type(file_storage):
    assert file_storage.in_storage('/tmp/test.pdf') == False

def test_in_storage_valid_type(file_storage):
    assert file_storage.in_storage('/tmp/test.t') == True

def test_in_storage_path_none(file_storage):
    with pytest.raises(AssertionError):
        file_storage.in_storage(None)


@pytest.fixture
def file_storage():
    return FileStorage(storage_path="/tmp", file_type="txt", makedirs=True)

def test_in_storage_true(file_storage):
    path = "/tmp/file.txt"
    result = file_storage.in_storage(path)
    assert result == True

def test_in_storage_false(file_storage):
    path = "/etc/file.txt"
    result = file_storage.in_storage(path)
    assert result == False

def test_to_relative_path_valid(file_storage):
    path = "/tmp/file.txt"
    result = file_storage.to_relative_path(path)
    assert result == "file.txt"

def test_to_relative_path_invalid(file_storage):
    path = "/etc/file.txt"
    with pytest.raises(ValueError):
        file_storage.to_relative_path(path)


@pytest.fixture
def test_file_storage():
    test_storage_path = "./test_storage"
    os.makedirs(test_storage_path, exist_ok=True)
    file_storage = FileStorage(test_storage_path, file_type='t', makedirs=True)
    yield file_storage
    os.rmdir(test_storage_path)

@pytest.mark.parametrize("path, storage_path, expected", [
    ("test.txt", "./test_storage", "./test_storage/test.txt"),
    ("/test.txt", "./test_storage", "./test_storage/test.txt"),
    ("../test.txt", "./test_storage", "./test_storage/test.txt"),
    ("/../test.txt", "./test_storage", "./test_storage/test.txt")
])
def test_make_full_path(test_file_storage, path, storage_path, expected):
    file_storage = test_file_storage
    file_storage.storage_path = storage_path
    assert file_storage.make_full_path(path) == expected


@pytest.fixture
def fs():
    return FileStorage(storage_path='/home/user/', file_type='t', makedirs=True)

@pytest.mark.parametrize('wd_relative_path, expected_result',
[
    ('/home/user/dir1/dir2/file.txt', 'dir1/dir2/file.txt'),
    ('/home/user2/dir1/dir2/otherfile.txt', None),
    ('/home/user/dir1/dir2/file.txt/', None)
])
def test_from_wd_to_relative_path(fs, wd_relative_path, expected_result):
    assert fs.from_wd_to_relative_path(wd_relative_path) == expected_result


@pytest.fixture
def test_file_storage():
    return FileStorage(storage_path="my_path", file_type="txt", makedirs=True)

def test_from_relative_path_to_wd_basic_case(test_file_storage):
    # Basic case
    assert test_file_storage.from_relative_path_to_wd("test.txt") == "my_path/test.txt"

def test_from_relative_path_to_wd_relative_path_start_with_dot(test_file_storage):
    # Relative path starts with "."
    assert test_file_storage.from_relative_path_to_wd("./test.txt") == "my_path/test.txt"

def test_from_relative_path_to_wd_subdirectory_case(test_file_storage):
    # Subdirectory case
    assert test_file_storage.from_relative_path_to_wd("subdir/test.txt") == "my_path/subdir/test.txt"

def test_from_relative_path_to_wd_subsubdirectory_case(test_file_storage):
    # Subsubdirectory case
    assert test_file_storage.from_relative_path_to_wd("subdir/subsubdir/test.txt") == "my_path/subdir/subsubdir/test.txt"

def test_from_relative_path_to_wd_file_type_case(test_file_storage):
    # File type case
    assert test_file_storage.from_relative_path_to_wd("test.txt") == "my_path/test.txt"
    assert test_file_storage.from_relative_path_to_wd("test.json") == "my_path/test.json"
    assert test_file_storage.from_relative_path_to_wd("test.pdf") == "my_path/test.pdf"


@pytest.fixture
def file_storage_instance():
    return FileStorage('/tmp/test_storage', 'text', True)

def test_init_storage_path(file_storage_instance):
    assert file_storage_instance.storage_path == os.path.realpath('/tmp/test_storage')

def test_init_file_type(file_storage_instance):
    assert file_storage_instance.file_type == 'text'

@pytest.mark.parametrize('file_path, expected_file_name', [('/tmp/test_storage/test_file.txt', 'test_file.txt'), 
('/tmp/test_storage/test_file2.pdf', 'test_file2.pdf')])
def test_get_file_name_from_file_path(file_path, expected_file_name):
    assert FileStorage.get_file_name_from_file_path(file_path) == expected_file_name


@pytest.fixture
def file_storage():
    file_storage = FileStorage('/tmp/testing', 't', True)
    return file_storage

#Check if correct storage path is passed
def test_storage_path(file_storage):
    assert file_storage.storage_path == os.path.realpath('/tmp/testing')

#Check if correct file type is passed
def test_file_type(file_storage):
    assert file_storage.file_type == 't'

#Check if makedirs is correctly set
def test_makedirs(file_storage):
    assert file_storage.makedirs == True

#Check if validating a valid filename passes
@pytest.mark.parametrize('name', [('hello'), ('world.txt')])
def test_validate_valid_file_name(file_storage, name):
    file_storage.validate_file_name_component(name)

#Check if validating an invalid filename raises an exception
@pytest.mark.parametrize('name', [('hello%'), ('world{}')])
def test_validate_invalid_file_name(file_storage, name):
    with pytest.raises(pathvalidate.error.InvalidCharError):
        file_storage.validate_file_name_component(name)


@pytest.fixture
def file_storage():
    storage_path = 'test/'
    file_type = 't'
    makedirs = True
    storage = FileStorage(storage_path, file_type, makedirs)
    return storage

def test_init(file_storage):
    assert file_storage.storage_path == os.path.realpath('test/')
    assert file_storage.file_type == 't'

def test_rmtree_del_ro_unlink(file_storage):
    action = os.unlink
    name = 'test/test.t'
    exc = None
    file_storage.rmtree_del_ro(action, name, exc)
    assert not os.path.exists(name)

def test_rmtree_del_ro_remove(file_storage):
    action = os.remove
    name = 'test/test.t'
    exc = None
    file_storage.rmtree_del_ro(action, name, exc)
    assert not os.path.exists(name)

def test_rmtree_del_ro_rmdir(file_storage):
    action = os.rmdir
    name = 'test/testdir'
    exc = None
    os.makedirs(name, exist_ok=True)
    file_storage.rmtree_del_ro(action, name, exc)
    assert not os.path.exists(name)

