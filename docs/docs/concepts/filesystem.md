# Filesystem

A filesystem is an abstraction over local filesystems, remote machines connected by SSH, or any other source of files. A filesystem is a resource rooted at some absolute filepath.

Rename files with params.apply_filesystem_edit(RenameFile(filepath=filepath, new_filepath=new_filepath)). See filesystem_edit.py for all the FileSystemEdit subclasses you can use here. I'll probably just add special methods for each of them later so you can write params.rename_file(...)  or something

## Actions

### Read file

### Add file

### Delete file

### Add folder

### Delete folder
