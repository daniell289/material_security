from __future__ import annotations


class Directory:
    def __init__(self, name: str, parent: Directory, is_root=False):
        self.is_root = is_root
        self.name = name
        self.parent = parent
        # Prevent double //
        if (is_root):
            self.path = "/"
        elif (parent.is_root):
            self.path = parent.path + name
        else:
            self.path = parent.path + "/" + name
        self.subfolders = {}
        self.files = {}

    # Create a sub directory under this directory
    def new_subfolder(self, new_name: str) -> Directory:
        d = Directory(new_name, self)
        self.subfolders[new_name] = d
        return d

    # Create new file under this directory
    def new_file(self, file_name: str) -> File:
        f = File(file_name, self)
        self.files[file_name] = f
        return f

    # Given an existing file, link it to this directory
    def add_existing_file(self, file: File):
        if (file is None):
            return
        self.files[file.name] = file
        file.parent = self

    def get_file(self, file_name: str) -> File:
        if file_name in self.files.keys():
            return self.files[file_name]
        else:
            return None

    def get_subfolder(self, subfolder_name: str) -> Directory:
        if subfolder_name in self.subfolders.keys():
            return self.subfolders[subfolder_name]
        else:
            return None

    # Removes subfolder, NOOp if doesn't exist.
    def remove_subfolder(self, subfolder_name):
        return self.subfolders.pop(subfolder_name, None)

    # Removes file, NOOp if doesn't exist.
    def remove_file(self, file_name: str) -> File:
        return self.files.pop(file_name, None)

    # Starting from this dir, invoke an arbitrary func on every folder & file
    # + recursively on every subfolder
    # Return the output of each type (file|folder) as two dicts where
    # dict{key=file/folder-path, val=func output}
    # Output = tuple(dict,dict) correspondg to file-output, folder-output

    # e.g. Imagine a tree of  / -> file1, dir1; 
    #                         /dir1 -> file2
    # e.g. Output: ({/file1->val1, /dir1/file2->val2} , {/dir1->val3})
    # where the first dict is the output of all file invocations
    # and the second dict is the output of all directory invocations
    def recurse_with_func(self, func: function, args: list) -> tuple[dict, dict]:
        output_files = {}
        output_folders = {}
        for file in self.files.values():
            output_files[file.get_path()] = func(file, *args)
        for dir in self.subfolders.values():
            output_folders[dir.path] = func(dir, *args)
            recurse_output_files, recurse_output_folders = dir.recurse_with_func(
                func, args)
            # merge dicts; no worries about key conflict due to unique pathes as keys
            output_files = {**output_files, **recurse_output_files}
            output_folders = {**output_folders, **recurse_output_folders}
        return (output_files, output_folders)


class File:
    def __init__(self, name: str, parent: Directory):
        self.name = name
        self.contents = ""
        self.parent = parent
        # TODO implement read/write lock logic
        # Supports multiple open reads
        self.read_handlers = set()
        # Supports only 1 open write
        self.write_handler = None

    def get_path(self) -> str:
        if self.parent.is_root:
            return "/"+self.name
        else:
            return self.parent.path + "/" + self.name

    def copy(self) -> File:
        f = File(self.name, self.parent)
        f.contents = self.contents
        return f

    # Deep copy this file in the same dir with new_name
    # returns the new file
    def copy_in_place(self, new_name: str) -> File:
        if (new_name == self.name):
            raise Exception("Can't copy file with same name")
        else:
            f = File(new_name, self.parent)
            self.parent.add_existing_file(f)
            f.contents = self.contents
            return f

# Allows reading and writing of file in chunks
class FileHandler:
    def __init__(self, file: File):
        self.file = file
        self.cursor = 0  # Used to maintain current position
        self.is_open = False

    # Moves the cursor to absolute index
    # Returns T/F for success/fail
    def move_cursor_abs(self, i: int) -> bool:
        if (i < 0 or i > len(self.file.contents)):
            print("Cursor value out of bounds")
            return False
        self.cursor = i
        return True

    # Moves the cursor relative to current index
    # Negative int will move it backward
    # Returns T/F for success/fail
    def move_cursor_rel(self, i: int) -> bool:
        new_pos = self.cursor + i
        if (new_pos < 0 or new_pos >= len(self.file.contents)):
            print("Cursor value out of bounds")
            return False
        self.cursor = new_pos
        return True

    # If i is out of bounds, round i to 0 or EoF
    def _round_index(self, i: int) -> int:
        if i > len(self.file.contents):
            i = len(self.file.contents)
        if i < 0:
            i = 0
        return i


class ReadHandler(FileHandler):
    # Read next i chars
    def read_next(self, i: int) -> str:
        if not self.is_open:
            raise Exception("Cannot read from unopened handler")
        new_index = self._round_index(self.cursor+i)
        output = self.file.contents[self.cursor:new_index]
        self.cursor = new_index
        return output

    # Read from cursor to end
    def read_to_end(self) -> str:
        if not self.is_open:
            raise Exception("Cannot read from unopened handler")
        output = self.file.contents[self.cursor:]
        self.cursor = len(self.file.contents)
        return output

    # Stream output until the next newline starting from cursor
    def read_line(self) -> str:
        if not self.is_open:
            raise Exception("Cannot read from unopened handler")
        output = ""
        for i in range(self.cursor, len(self.file.contents)):
            c = self.file.contents[self.cursor]
            output += c
            self.cursor = self._round_index(self.cursor + 1)
            if (c == "\n"):
                break
        return output

    # Outputs all file contents, doesn't move cursor
    def read(self) -> str:
        if not self.is_open:
            raise Exception("Cannot read from unopened handler")
        return self.file.contents

    # Opening a read handler is always successful
    def open(self) -> bool:
        self.file.read_handlers.add(self)
        self.is_open = True
        self.cursor = 0
        return True

    # Close the handler
    def close(self) -> None:
        self.file.read_handlers.remove(self)
        self.is_open = False


class WriteHandler(FileHandler):
    # Overwrites file contents
    def write(self, contents: str) -> None:
        if not self.is_open:
            raise Exception("Cannot write with unopened handler")
        self.file.contents = contents
        self.cursor = len(self.file.contents)

    # Appends file contents to end
    def concat(self, contents: str) -> None:
        if not self.is_open:
            raise Exception("Cannot write with unopened handler")
        self.file.contents += contents
        self.cursor = len(self.file.contents)

    # Inserts contents at current cursor
    # Cursor now points to cursor + len(contents)
    def insert(self, contents: str) -> None:
        if not self.is_open:
            raise Exception("Cannot write with unopened handler")
        c = self.file.contents
        self.file.contents = c[0:self.cursor] + contents + c[self.cursor:]
        self.cursor = self.cursor + len(contents)

    # Open the write handler
    # Returns false if an open one already exists

    def open(self) -> bool:
        if (self.file.write_handler is None):
            self.file.write_handler = self
            self.is_open = True
            self.cursor = 0
            return True
        else:
            return False

    # Close the handler
    def close(self) -> None:
        self.file.write_handler = None
        self.is_open = False
