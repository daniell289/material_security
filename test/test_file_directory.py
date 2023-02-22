import unittest
from filesystem import *


# Main create, move, remove operations
# Also tests path operations such as change dir
class TestFileDirectory(unittest.TestCase):

    def setUp(self):
        self.fs = Filesystem()

    def test_mkdir_simple(self):
        self.fs.mkdir("dir1")
        self.fs.mkdir("dir2")
        assert self.fs.list_folders() == ["dir1", "dir2"]

    def test_mkfile_simple(self):
        self.fs.mkfile("f1")
        self.fs.mkfile("f2")
        assert self.fs.list_files() == ["f1", "f2"]

    def test_cd_simple(self):
        # Root -> dir1, topfile
        # dir1 -> bottomfile
        self.fs.mkdir("dir1")
        self.fs.mkfile("topfile")
        self.fs.changedir("dir1")
        self.fs.mkfile("bottomfile")
        # Check bottom file exists in the lower dir
        assert self.fs.get_current_path() == "/dir1"
        assert self.fs.list_files() == ["bottomfile"]
        self.fs.changedir("../")
        # Go back up to root, see only top file exists
        assert self.fs.get_current_path() == "/"
        assert self.fs.list_files() == ["topfile"]

    # Test creating all missing parent directories with flag -p
    def test_mkdir_recursive(self):
        # absolute path
        self.fs.mkdir("/dir1/dir2/dir3", option="-p")
        # go to deepest dir
        self.fs.changedir("/dir1/dir2/dir3")
        assert self.fs.get_current_path() == "/dir1/dir2/dir3"

        # walk back up and make sure every dir exists
        self.fs.changedir("../")
        assert self.fs.get_current_path() == "/dir1/dir2"
        self.fs.changedir("../")
        assert self.fs.get_current_path() == "/dir1"

    # Test making recursive directories with relative flag
    # and multi-direction path
    def test_mkdir_recursive_multi_direction(self):
        self.fs.mkdir("dir1")
        self.fs.changedir("dir1")
        # Path is down, up, down, down
        # Also this time with relative path
        self.fs.mkdir("dir2/../dir2/dir3", option="-p")
        # Make sure we didn't create 2 dir2s
        assert self.fs.list_folders() == ["dir2"]
        # Note we are already at "/d1"
        # Use a relative path to traverse
        # Try multiple direction
        self.fs.changedir("dir2/../../dir1/dir2/dir3")
        assert self.fs.get_current_path() == "/dir1/dir2/dir3"

    # Invalid path
    def test_mkdir_fail(self):
        # no flag set
        dir = self.fs.mkdir("dir1/dir2/dir3")
        assert dir is None
        assert self.fs.list_folders() == []

    # No name specified
    def test_mkdir_fail2(self):
        dir = self.fs.mkdir("/parent/", "-p")
        assert dir is None
        # Make sure we don't make missing parents
        # if input is invalid
        assert self.fs.list_folders() == []

    # similar as mkdir but with mkfile
    # Test making recursive directories with relative flag
    # and multi-direction path
    def test_mkfile_recursive_multi_direction(self):
        self.fs.mkdir("dir1")
        self.fs.changedir("dir1")
        # Path is down, up, down, down
        # Also this time with relative path
        self.fs.mkfile("dir2/../dir2/dir3/file", option="-p")
        # Make sure we didn't create 2 dir2s
        assert self.fs.list_folders() == ["dir2"]
        # Note we are already at "/d1"
        self.fs.changedir("dir2/dir3")
        assert self.fs.list_files() == ["file"]

    # Invalid path
    def test_mkfile_fail(self):
        # no flag set
        f = self.fs.mkfile("dir1/file")
        assert f is None

    # No name specified
    def test_mkdir_fail2(self):
        f = self.fs.mkfile("/parent/", "-p")
        assert f is None

    # Bad pathes
    def test_cd_fail(self):
        self.fs.mkdir("dir1")
        self.fs.changedir("dir1")
        # doesn't exist, should end as no-op
        self.fs.changedir("../../../../")
        assert self.fs.get_current_path() == "/dir1"
        # doesn't exist
        self.fs.changedir("dir2")
        # verify root is fine
        assert self.fs.get_current_path() == "/dir1"
        self.fs.changedir("/")
        assert self.fs.get_current_path() == "/"

    def test_remove_file_simple(self):
        self.fs.mkfile("f1")
        self.fs.mkfile("f2")
        self.fs.mkfile("f3")
        assert self.fs.list_files() == ["f1", "f2", "f3"]
        self.fs.remove_file("f2")
        assert self.fs.list_files() == ["f1", "f3"]

    def test_remove_dir_simple(self):
        self.fs.mkdir("d1")
        self.fs.mkdir("d2")
        self.fs.mkdir("d3")
        assert self.fs.list_folders() == ["d1", "d2", "d3"]
        self.fs.remove_dir("d2")
        assert self.fs.list_folders() == ["d1", "d3"]
        # cannot changedir into deleted dir
        assert self.fs.changedir("d2") == False

    def test_remove_dir_absolute(self):
        self.fs.mkdir("d1/d2/d3/d4", "-p")
        self.fs.remove_dir("/d1/d2/d3")
        self.fs.changedir("d1/d2")
        assert self.fs.list_folders() == []

    def test_mvfile_simple(self):
        self.fs.mkfile("/d1/d2/file", "-p")
        self.fs.move_file("/d1/d2/file", "/")
        # file should be at root
        assert self.fs.list_files() == ["file"]
        # check file doesn't exist at /d1/d2
        self.fs.changedir("/d1/d2")
        assert self.fs.list_files() == []

    # Test mvfile override name conflicts
    def test_mvfile_override(self):
        self.fs.mkfile("file")
        self.fs.write_file("file", "old_contents")
        self.fs.mkfile("/d1/file", "-p")
        self.fs.changedir("d1")
        self.fs.write_file("file", "new_contents")
        self.fs.move_file("/d1/file", "/")
        # file should be gone here
        assert self.fs.list_files() == []
        # 1 exact file should exist at root (due to override)
        self.fs.changedir("/")
        assert self.fs.list_files() == ["file"]
        # check its the new contents
        assert self.fs.read_file("file") == "new_contents"

    # Test mvfile -b
    def test_mvfile_backup(self):
        self.fs.mkfile("file")
        self.fs.write_file("file", "old_contents")
        self.fs.mkfile("/d1/file", "-p")
        self.fs.changedir("d1")
        self.fs.write_file("file", "new_contents")
        self.fs.move_file("/d1/file", "/", "-b")
        # file should be gone here
        assert self.fs.list_files() == []
        # 2 files should exist at root
        self.fs.changedir("/")
        assert sorted(self.fs.list_files()) == ["file", "~file"]
        # check the old content is preserved
        assert self.fs.read_file("~file") == "old_contents"

    # Test mvfile -n
    def test_mvfile_no_override(self):
        self.fs.mkfile("file")
        self.fs.mkfile("/d1/file", "-p")
        self.fs.changedir("d1")
        self.fs.move_file("/d1/file", "/", "-n")
        # file should remain
        assert self.fs.list_files() == ["file"]
        # old file should exist at root
        self.fs.changedir("/")
        assert self.fs.list_files() == ["file"]

    # Test mvfile -p
    def test_mvfile_create_parent(self):
        self.fs.mkfile("file")
        self.fs.move_file("file", "/d1/d2/", "-p")
        # file is gone from root
        assert self.fs.list_files() == []
        self.fs.changedir("d1/d2")
        # file is moved to newly created dir
        assert self.fs.list_files() == ["file"]

    # Test destination path contains a diff file name
    def test_mvfile_with_rename(self):
        self.fs.mkfile("/d1/d2/file", "-p")
        self.fs.move_file("/d1/d2/file", "/file2")
        # file should be at root
        assert self.fs.list_files() == ["file2"]
        # check file doesn't exist at /d1/d2
        self.fs.changedir("/d1/d2")
        assert self.fs.list_files() == []

    # test absolute, relative paths
    def test_mvfile_paths(self):
        self.fs.mkfile("/d1/d2/d3/file", "-p")
        self.fs.changedir("/d1")
        # Current at d1
        # Specify source with absolute path
        # Specify dest with relative path
        # This actually moves it to root
        # dest = d1->d2->d1->root
        self.fs.move_file("/d1/d2/d3/file", "d2/../../")
        # check successful move
        self.fs.changedir("/")
        assert self.fs.list_files() == ["file"]
        self.fs.changedir("d1/d2/d3")
        assert self.fs.list_files() == []

    def test_cpfile_simple(self):
        self.fs.mkfile("/d1/d2/file", "-p")
        self.fs.copy_file("/d1/d2/file", "/")
        # file should be at root
        assert self.fs.list_files() == ["file"]
        # check file still exists at /d1/d2
        self.fs.changedir("/d1/d2")
        assert self.fs.list_files() == ["file"]

    # Test cpfile override name conflicts
    def test_cpfile_override(self):
        self.fs.mkfile("file")
        self.fs.write_file("file", "old_contents")
        self.fs.mkfile("/d1/file", "-p")
        self.fs.changedir("d1")
        self.fs.write_file("file", "new_contents")
        # copy to root
        self.fs.copy_file("/d1/file", "/")
        # file is still here
        assert self.fs.list_files() == ["file"]
        # 1 exact file should exist at root (due to override)
        self.fs.changedir("/")
        assert self.fs.list_files() == ["file"]
        # check the copied file overrode with the new contents
        assert self.fs.read_file("file") == "new_contents"

    # Test cpfile -b
    def test_cpfile_backup(self):
        self.fs.mkfile("file")
        self.fs.write_file("file", "old_contents")
        self.fs.mkfile("/d1/file", "-p")
        self.fs.changedir("d1")
        self.fs.write_file("file", "new_contents")
        self.fs.copy_file("/d1/file", "/", "-b")
        # file still here here
        assert self.fs.list_files() == ["file"]
        # 2 files should exist at root
        self.fs.changedir("/")
        assert sorted(self.fs.list_files()) == ["file", "~file"]
        # check the old content is preserved
        assert self.fs.read_file("~file") == "old_contents"
        # check new file has new content
        assert self.fs.read_file("file") == "new_contents"

    # Test cpfile -n
    def test_cpfile_no_override(self):
        self.fs.mkfile("file")
        self.fs.write_file("file", "old_contents")
        self.fs.mkfile("/d1/file", "-p")
        self.fs.changedir("d1")
        self.fs.write_file("file", "new_contents")
        self.fs.copy_file("/d1/file", "/", "-n")
        # file should remain
        assert self.fs.list_files() == ["file"]
        # old file should exist at root
        self.fs.changedir("/")
        assert self.fs.list_files() == ["file"]
        # check old content remains
        assert self.fs.read_file("file") == "old_contents"

    # Test cpfile -p
    def test_cpfile_create_parents(self):
        self.fs.mkfile("file")
        self.fs.copy_file("file", "/d1/d2/", "-p")
        # file is still here
        assert self.fs.list_files() == ["file"]
        self.fs.changedir("d1/d2/")
        # file exists in newly created dir
        assert self.fs.list_files() == ["file"]

    def test_cpfile_rename(self):
        self.fs.mkfile("/d1/d2/file", "-p")
        self.fs.changedir("/d1/d2")
        # copy with absolute and relative path
        # note both refer to d2
        self.fs.copy_file("/d1/d2/file", "file2")
        assert self.fs.list_files() == ["file", "file2"]

if __name__ == '__main__':
    unittest.main()
