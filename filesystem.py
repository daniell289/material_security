from objects import *
from path_utils import *
import re


class Filesystem:
    def __init__(self):
        self.root = Directory("", None, is_root=True)
        self.current_dir = self.root

    # Change current directory to given absolute/relative path
    # Return T/F on success/failure (fail if invalid path)
    def changedir(self, path:str) -> bool:
        dir_list, is_absolute = parse_path(path)
        final_dir = self._walk_dir_path_absolute_or_relative(
            dir_list, is_absolute)
        if (final_dir is not None):
            self.current_dir = final_dir
            return True
        else:
            print("Invalid path")
            return False

    # Create and return the specified directory. Fail if dir already exists
    # Default: Returns None if path is invalid
    # Option "-p": Creates missing parent directories
    #   e.g. /a/b/c -> also creates a->b before creating c if a->b doesn't exist
    # Returns None if no ending name
    #   e.g. /a/b/c/ -> None, due to no name specified (see trailing slash)
    def mkdir(self, path: str, option="") -> Directory:
        dir_list, new_dir_name, is_absolute = parse_path_with_ending_name(
            path)
        if (new_dir_name == ""):
            print("No specified directory name")
            return None
        final_dir = self._walk_dir_path_absolute_or_relative(
            dir_list, is_absolute, option)
        if (final_dir is None):
            print("Invalid path; try -p to create missing parent directories")
            return None
        if (final_dir.get_subfolder(new_dir_name)):
            print("Directory already exists")
            return None
        return final_dir.new_subfolder(new_dir_name)

    # Create and return a new empty file
    # **Similar to mkdir**
    # Default Option: Return None if path is invalid
    # Option "-p": Creates missing parent directories
    def mkfile(self, path: str, option="") -> File:
        dir_list, new_file_name, is_absolute = parse_path_with_ending_name(
            path)
        if (new_file_name == ""):
            print("No specified file name")
            return None
        final_dir = self._walk_dir_path_absolute_or_relative(
            dir_list, is_absolute, option)
        if (final_dir is None):
            print("Invalid path; try -p to create missing parent directories")
            return None
        if (final_dir.get_file(new_file_name)):
            print("File already exists; please remove or rename")
            return None
        return final_dir.new_file(new_file_name)

    # List all subdirectory names in the current dir
    def list_folders(self) -> list[str]:
        return list(self.current_dir.subfolders.keys())

    # List all file names in the current dir
    def list_files(self) -> list[str]:
        return list(self.current_dir.files.keys())

    # Get current path
    def get_current_path(self) -> str:
        return self.current_dir.path

    # Removes a directory; Accepts absolute/relative path
    # Return T/F success/fail
    def remove_dir(self, path: str) -> bool:
        dir_list, rm_name, is_absolute = parse_path_with_ending_name(
            path)
        final_dir = self._walk_dir_path_absolute_or_relative(
            dir_list, is_absolute)
        if (final_dir is None):
            print("Invalid path")
            return False
        removed_dir = final_dir.remove_subfolder(rm_name)
        if (removed_dir is None):
            print("Directory doesn't exist")
            return False
        return True

    # Removes a file; Accepts absolute/relative path
    # Return T/F success/fail
    def remove_file(self, path: str):
        dir_list, rm_name, is_absolute = parse_path_with_ending_name(
            path)
        final_dir = self._walk_dir_path_absolute_or_relative(
            dir_list, is_absolute)
        if (final_dir is None):
            print("Invalid path")
            return False
        removed_file = final_dir.remove_file(rm_name)
        if (removed_file is None):
            print("File doesn't exist")
            return False
        return True

    # Gets the R/W file handler for more fine grained edit operations
    # returns None if invalid path or file doesn't exist
    def getFileHandlerFromPath(self, file_path: str, is_write: bool) -> FileHandler:
        dir_list, file_name, is_absolute = parse_path_with_ending_name(
            file_path)
        final_dir = self._walk_dir_path_absolute_or_relative(
            dir_list, is_absolute)
        if (final_dir is None):
            print("Invalid path")
            return None
        file = final_dir.get_file(file_name)
        if (file is None):
            print("File doesn't exist at path")
            return None
        if (is_write):
            return WriteHandler(file)
        else:
            return ReadHandler(file)

    # Read the contents of the file
    def read_file(self, file_path: str) -> str:
        fh = self.getFileHandlerFromPath(file_path, is_write=False)
        if fh is None or not fh.open():
            print("Failed to open read file handler")
            return ""
        contents = fh.read()
        fh.close()
        return contents

    # Write to file
    # By default overwrites the file
    # Option "-a" appends to file with new line
    # Option "-c" concats to file without new line
    # Returns T/F on success/fail (fail if invalid file path)
    def write_file(self, file_path: str, contents: str, option="") -> bool:
        fh = self.getFileHandlerFromPath(file_path, is_write=True)
        if fh is None or not fh.open():
            print("Failed to open write file handler")
            return False
        if (option == "-a"):
            fh.concat("\n"+contents)
        elif (option == "-c"):
            fh.concat(contents)
        else:
            fh.write(contents)
        fh.close()
        return True

    # Given a path and a regex, find every
    # matching folder or file under that path
    # return tup[file_list, folder_list] of the matching pathes
    # option "-r": Recurse under subdirectories and return all matches

    # Note: path = "." is shorthand for current directory
    def find_with_regex(self, regex: str, path: str, option="") -> tuple[list, list]:
        dir_list, is_absolute = parse_path(path)
        starting_dir = self._walk_dir_path_absolute_or_relative(
            dir_list, is_absolute)
        if (starting_dir is None):
            print("Invalid path")
            return

        # Inner function (for recursion)
        def _does_match(obj: File | Directory, regex: str) -> bool:
            return re.match(regex, obj.name) is not None

        # Recurse
        if (option == "-r"):
            file_output, folder_output = starting_dir.recurse_with_func(
                _does_match, args=[regex])
            # Filter matches
            file_output = [k for (k, v) in file_output.items() if v]
            folder_output = [k for (k, v) in folder_output.items() if v]
        else:  # Only check current dir
            file_output = [f.get_path()
                           for f in starting_dir.files.values() if _does_match(f, regex)]
            folder_output = [
                f.path for f in starting_dir.subfolders.values() if _does_match(f, regex)]
        return (file_output, folder_output)

    # Moves or Copies source file to dest
    # Can also use this to rename files
    # By default overrides name conflict files in dest
    # By default, No-Ops (returns False) if dest path is an invalid directory tree
    # Option [-b] On file name conflict, a backup of the conflicting file is created with ~<filename>
    # Option [-n] On file name conflict, operation fails
    # Option [-p] Creates missing parent directories along the Dest path
    # Returns true/false on success/failure

    def move_file(self, source_file_path: str, dest_path: str, option="") -> bool:
        return self._move_or_copy_file(source_file_path, dest_path, False, option)

    def copy_file(self, source_file_path: str, dest_path: str, option="") -> bool:
        return self._move_or_copy_file(source_file_path, dest_path, True, option)

    def _move_or_copy_file(self, source_file_path: str, dest_path: str, should_copy: bool, option="") -> bool:
        # Extract Source File
        dir_list, source_file_name, is_absolute = parse_path_with_ending_name(
            source_file_path)
        source_file_dir = self._walk_dir_path_absolute_or_relative(
            dir_list, is_absolute)
        f = source_file_dir.get_file(source_file_name)
        if (f is None):
            print("Source file doesn't exist")
            return False
        # Extract Destination Directory
        dir_list, dest_file_name, is_absolute = parse_path_with_ending_name(
            dest_path)
        # If new file name is unspecified, keep the same name
        if (dest_file_name == ""):
            dest_file_name = source_file_name
        dest_dir = self._walk_dir_path_absolute_or_relative(
            dir_list, is_absolute, option)
        if (dest_dir is None):
            print("Dest Directory doesn't exist")
            return False
        # Move or Copy
        # Option "-b": backup conflicts as "~name"
        if (option == "-b"):
            existing_file = dest_dir.get_file(dest_file_name)
            if (existing_file is not None):
                print(dest_file_name + " exists, creating backup")
                existing_file.copy_in_place("~" + existing_file.name)
            self._move_file_with_override(
                f, dest_dir, dest_file_name, should_copy)
            return True
        # Option "-n": do not override conflicts
        elif (option == "-n"):
            existing_file = dest_dir.get_file(dest_file_name)
            if (existing_file is None):
                self._move_file_with_override(
                    f, dest_dir, dest_file_name, should_copy)
                return True
            else:
                print(dest_file_name + " exists in dest, move aborted")
                return False
        # normal move with override
        else:
            self._move_file_with_override(
                f, dest_dir, dest_file_name, should_copy)
            return True

    # Precondition: source_file & dest_dir are not None
    # Moves or copies source file to dest_dir as dest_file_name,
    # overriding name conflicts
    def _move_file_with_override(self, source_file: File, dest_dir: Directory,  dest_file_name: str, should_copy: bool) -> None:
        if (should_copy):
            source_file = source_file.copy()
        else:
            # unlink source from it's parent
            old_parent_dir = source_file.parent
            old_parent_dir.remove_file(source_file.name)
        source_file.name = dest_file_name
        dest_dir.add_existing_file(source_file)

    # Precondition: source_dir & dest_dir are not None
    # Moves or copies source dir to dest_dir as new_name,
    # overriding name conflicts
    def _move_dir_with_override(self, source_dir: Directory, dest_dir: Directory, new_name: str, should_copy: bool) -> None:
        source_subfolders = source_dir.subfolders
        source_files = source_dir.files
        if (not should_copy):
            # unlink source from it's parent
            old_parent_dir = source_dir.parent
            old_parent_dir.remove_subfolder(source_dir.name)
        # Creating a new Directory obj fixes the path on the moved directory
        d = dest_dir.new_subfolder(new_name)
        d.subfolders = source_subfolders
        d.files = source_files

    # Given an absolute or relative ordered directory list
    # Walk and return the final directory
    # Default: Return None if invalid tree
    # Option "-p": Creates missing parent directories instead
    def _walk_dir_path_absolute_or_relative(self, dirs: list[str], is_absolute: bool, option="") -> Directory:
        create_missing_dir = False
        if (option == "-p"):
            create_missing_dir = True
        # Only difference between absolute or relative path is the starting Directory
        if (is_absolute):
            return self._walk_dir_path(self.root, dirs, create_missing_dir)
        else:
            return self._walk_dir_path(self.current_dir, dirs, create_missing_dir)

    # Given a starting directory, walk and return the final directory
    # If flag is set: create missing parent directories
    # Else Return None if flag is not set and walk is invalid
    # IMPORTANT: Only creates missing child directories, not "../"
    def _walk_dir_path(self, starting_dir: Directory, dirs: list[str], should_create_missing_dir: bool) -> Directory:
        current_dir = starting_dir
        for dir_name in dirs:
            # special case, ".." refers to parent directory
            if (dir_name == ".."):
                current_dir = current_dir.parent
                if (current_dir is None):
                    return None
            # special case, "." refers to current directory, so no-op
            elif (dir_name == "."):
                continue
            else:
                next_dir = current_dir.get_subfolder(dir_name)
                if (next_dir is None):
                    if (should_create_missing_dir):
                        next_dir = current_dir.new_subfolder(dir_name)
                    else:
                        # stop the walk
                        return None
                current_dir = next_dir
        return current_dir
