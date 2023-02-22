import unittest
from filesystem import *


# Tests the find operation
class TestFind(unittest.TestCase):
    def setUp(self):
        self.fs = Filesystem()

    def test_find_file_simple(self):
        self.fs.mkfile("f1")
        self.fs.mkfile("f2")
        files, folders = self.fs.find_with_regex("f1", "/")
        assert files == ["/f1"]
        assert folders == []

    # -r recurse
    def test_find_file_and_dir_recurse_simple(self):
        self.fs.mkfile("name")
        self.fs.mkdir("name")
        self.fs.mkdir("bbbb")
        # sub files
        self.fs.mkfile("/name/name")
        self.fs.mkfile("/bbbb/name")
        self.fs.mkfile("/bbbb/cccc")

        files, folders = self.fs.find_with_regex("name", "/", "-r")
        assert sorted(files) == ["/bbbb/name", "/name", "/name/name"]
        assert folders == ["/name"]

    # use an actual regex this time
    # name[0-9]+ matches name12, name345, but not name_no_numbers
    def test_find_file_and_dir_with_regex(self):
        self.fs.mkfile("name12")
        self.fs.mkfile("name_no_numbers")
        self.fs.mkdir("cccc")
        self.fs.mkdir("bbbb")
        # sub files
        self.fs.mkfile("/cccc/name345")
        self.fs.mkfile("/bbbb/name_no_number")
        self.fs.mkfile("/bbbb/cccc")

        files, folders = self.fs.find_with_regex("name[0-9]+", "/", "-r")
        assert sorted(files) == ["/cccc/name345", "/name12"]
        assert folders == []

    # test finds where starting point not at root
    def test_find_within_sub_directory(self):
        self.fs.mkfile("name")
        self.fs.mkdir("a/b/c/d", "-p")
        self.fs.mkfile("a/name")
        self.fs.mkfile("a/b/name")
        self.fs.mkfile("a/b/c/name")
        self.fs.mkfile("a/b/c/d/name")
        self.fs.mkfile("a/b/c/d/not_name")
        # Look under /a/b/c
        files, folders = self.fs.find_with_regex("name", "/a/b", "-r")
        assert sorted(files) == ["/a/b/c/d/name", "/a/b/c/name", "/a/b/name"]
        assert folders == []

    # Complex directory structure, path, regex
    # Find all things that start with a, end with z
    # Recurse and no recurse
    def test_find_complex(self):
        self.fs.mkfile("applez")
        self.fs.mkdir("a/az/aa/d", "-p")
        self.fs.mkdir("a/af/az", "-p")
        self.fs.mkfile("a/az/aloe")
        self.fs.mkfile("a/az/cat")
        self.fs.mkfile("a/af/az/aws")
        self.fs.mkfile("a/af/az/afilez")

        # Use relative path going up to root /../../..
        # Recurse down
        self.fs.changedir("a/af/az")
        files, folders = self.fs.find_with_regex("a[a-z]*z", "../../../", "-r")
        assert sorted(files) == ["/a/af/az/afilez", "/applez"]
        assert sorted(folders) == ["/a/af/az", "/a/az"]

        # No recurse
        files, folders = self.fs.find_with_regex("a[a-z]*z", "../../../")
        assert sorted(files) == ["/applez"]
        assert sorted(folders) == []

if __name__ == '__main__':
    unittest.main()
