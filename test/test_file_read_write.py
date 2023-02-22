import unittest
from filesystem import *


# Tests File Read and Write cases
class TestFileReadWrite(unittest.TestCase):

    def setUp(self):
        self.fs = Filesystem()

    # *** Simple Tests without Cursor ****

    def test_write_read_invalid(self):
        self.fs.mkfile("f1")
        assert (self.fs.write_file("f2", "contents") == False)
        assert (self.fs.read_file("f2") == "")

    def test_write_read_simple(self):
        self.fs.mkfile("f1")
        self.fs.write_file("f1", "contents")
        assert (self.fs.read_file("f1") == "contents")

    def test_write_overwrite(self):
        self.fs.mkfile("f")
        self.fs.write_file("f", "aaaa")
        self.fs.write_file("f", "bbbb")
        assert (self.fs.read_file("f") == "bbbb")

    def test_write_append(self):
        self.fs.mkfile("f")
        self.fs.write_file("f", "aaaa")
        self.fs.write_file("f", "bbbb", "-a")
        assert (self.fs.read_file("f") == "aaaa\nbbbb")

    def test_write_concat(self):
        self.fs.mkfile("f")
        self.fs.write_file("f", "aaaa")
        self.fs.write_file("f", "bbbb", "-c")
        assert (self.fs.read_file("f") == "aaaabbbb")

    # *** Cursor Related Tests ****
    def test_read_line(self):
        self.fs.mkfile("f")
        self.fs.write_file("f", "line1\nline2\nline3")
        rh = self.fs.getFileHandlerFromPath("f", is_write=False)
        rh.open()
        assert (rh.read_line() == "line1\n")
        assert (rh.read_line() == "line2\n")
        assert (rh.read_line() == "line3")
        assert (rh.read_line() == "")
        rh.close()
    
    def test_read_next(self):
        self.fs.mkfile("f")
        self.fs.write_file("f", "line1\nline2\nline3")
        rh = self.fs.getFileHandlerFromPath("f", is_write=False)
        rh.open()
        assert (rh.read_next(3) == "lin")
        assert (rh.read_next(3) == "e1\n")
        assert (rh.read_next(6) == "line2\n")
        assert (rh.read_next(6) == "line3")
        assert (rh.read_next(5) == "")
        rh.close()

    def test_move_cursor_abs(self):
        self.fs.mkfile("f")
        self.fs.write_file("f", "line1\nline2\nline3")
        rh = self.fs.getFileHandlerFromPath("f", is_write=False)
        rh.open()
        #move to middle
        rh.move_cursor_abs(10)
        assert (rh.read_to_end() == "2\nline3")
        #move to start
        rh.move_cursor_abs(0)
        assert (rh.read_to_end() == "line1\nline2\nline3")
        #move to out of bounds
        assert (rh.move_cursor_abs(500000) == False)
        #move to end
        assert (rh.move_cursor_abs(17) == True)
        assert (rh.read_to_end() == "")
        rh.close()

    def test_move_cursor_rel(self):
        self.fs.mkfile("f")
        self.fs.write_file("f", "line1\nline2\nline3")
        rh = self.fs.getFileHandlerFromPath("f", is_write=False)
        rh.open()
        # move +5
        # read from 5:10
        rh.move_cursor_rel(5)
        assert (rh.read_next(5) == "\nline")
        #move backwards -10
        # read 0:5
        rh.move_cursor_rel(-10)
        assert (rh.read_next(5) == "line1")
        # move +3
        # read 8:rest
        rh.move_cursor_rel(3)
        assert (rh.read_to_end() == "ne2\nline3")
        #move to out of bounds
        assert (rh.move_cursor_rel(-50) == False)
        rh.close()

    # insert at a cursor
    def test_write_insert(self):
        self.fs.mkfile("f")
        wh = self.fs.getFileHandlerFromPath("f", is_write=True)
        wh.open()
        wh.write("abcdefg")
        #move to 2
        wh.move_cursor_abs(2)
        wh.insert("HI")
        assert (self.fs.read_file("f") == "abHIcdefg")
        #keep writing, write cursor is maintained
        wh.insert("BYE")
        assert (self.fs.read_file("f") == "abHIBYEcdefg")
        #move rel +2
        wh.move_cursor_rel(2)
        wh.insert("GO")
        assert (self.fs.read_file("f") == "abHIBYEcdGOefg")
        wh.close()

    # Use two read and write cursors
    # Tests that the two cursors are independently tracked
    def test_write_read_complex(self):
        self.fs.mkfile("f")
        wh = self.fs.getFileHandlerFromPath("f", is_write=True)
        wh.open()
        rh = self.fs.getFileHandlerFromPath("f", is_write=False)
        rh.open()
        # double insert should move write cursor appropriately
        wh.insert("abc\n")
        wh.insert("def")
        #abc\ndef
        assert(rh.read_line() == "abc\n")
        assert(rh.read_line() == "def")
        wh.move_cursor_abs(2)
        wh.insert("HI")
        # abHIc\ndef
        rh.move_cursor_abs(2)
        assert(rh.read_to_end() == "HIc\ndef")
        wh.move_cursor_rel(3)
        wh.insert("BYE")
        # abHIc\ndBYEef
        # Do not move read cursor which was previous EoF
        # Contents is 3 char longer so it should
        # now print the last 3
        assert(rh.read_to_end() == "Eef")
        rh.move_cursor_abs(0)
        assert(rh.read_to_end() == "abHIc\ndBYEef")





if __name__ == '__main__':
    unittest.main()
