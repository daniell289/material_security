from objects import *
from filesystem import *


# Cmdline Simulator
class Simulator:
    def __init__(self):
        self.filesystem = Filesystem()

    def print_help(self):
        help_text = """
        **Commands**
        exit                exit the test simmulator
        mkdir  [op] <dir>   make a new directory (absolute or relative path)
               [-p]             Creates missing parent directories
        mkfile [op] <file>  make a new file (absolute or relative path)
               [-p]            Creates missing parent directories
        mvfile/cpfile [op] <source> <dest> 
                            Moves/Copies source file as dest, overriding name conflict files in dest
                            If a different filename is specified in dest than source, file is renamed
                  [-b]         On file name conflict, a backup of the conflicting file is created with ~<filename>
                  [-n]         On file name conflict, operation fails 
                  [-p]         Creates missing parent directories along the Dest path
        pwd                 get current working directory path
        ls                  list current directory's subdirectories & files
        cd <path>           switch directory (absolute or relative path)
                              "../" is special and refers to parent directory
        rmdir <path>        delete that directory (recursively)
        rmfile <path>       delete that file
        find [op] <regex> <path> 
                            Finds all files/folders with matching regex name under path
                            Use find <regex> . to refer to the current directory
              [-r]          Recursively returns all matches
        read <file>         read whole file
        write <file_path> contents
                            overwrite file with contents
        write [op] <file_path> contents
              [-c]           concats contents to file (no new line)
              [-a]           appends contents to file with new line
        
        ***Extra Modes***
        editmode <file>      open read/write mode
        """
        print(help_text)

    def parse_output(self, text):
        text = text.split(" ")
        if (text[0] == "help"):
            self.print_help()
        elif (text[0] == "mkdir"):
            if (len(text) == 3):
                self.filesystem.mkdir(text[2], text[1])
            elif (len(text) == 2):
                self.filesystem.mkdir(text[1])
            else:
                print("Wrong number of arguments")
        elif (text[0] == "mkfile"):
            if (len(text) == 3):
                self.filesystem.mkfile(text[2], text[1])
            elif (len(text) == 2):
                self.filesystem.mkfile(text[1])
            else:
                print("Wrong number of arguments")
        elif (text[0] == "ls"):
            if (len(text) > 1):
                print("Wrong number of arguments")
                return
            print("***Folders***")
            print(self.filesystem.list_folders())
            print("\n")
            print("***Files***")
            print(self.filesystem.list_files())
        elif (text[0] == "cd"):
            if (len(text) == 2):
                self.filesystem.changedir(text[1])
            else:
                print("Wrong number of arguments")
        elif (text[0] == "pwd"):
            print(self.filesystem.get_current_path())
        elif (text[0] == "rmdir"):
            if (len(text) == 2):
                self.filesystem.remove_dir(text[1])
            else:
                print("Wrong number of arguments")
        elif (text[0] == "rmfile"):
            if (len(text) == 2):
                self.filesystem.remove_file(text[1])
            else:
                print("Wrong number of arguments")
        elif (text[0] == "find"):
            if len(text) == 3:
                files, folders = self.filesystem.find_with_regex(
                    text[1], text[2])
            elif len(text) == 4 and (text[1] == "-r"):
                files, folders = self.filesystem.find_with_regex(
                    text[2], text[3], "-r")
            else:
                print("Invalid find command")
                return
            print("**Matching File")
            print(files)
            print("**Matching Folders")
            print(folders)
        elif (text[0] == "read"):
            if (len(text) == 2):
                print(self.filesystem.read_file(text[1]))
            else:
                print("Wrong number of arguments")
        elif (text[0] == "editmode"):
            if (len(text) == 2):
                self.enter_edit_mode(text[1])
            else:
                print("Wrong number of arguments")
        elif (text[0] == "mvfile"):
            if (len(text) == 4):
                self.filesystem.move_file(text[2], text[3], text[1])
            elif (len(text) == 3):
                self.filesystem.move_file(text[1], text[2])
            else:
                print("Wrong number of arguments")
        elif (text[0] == "cpfile"):
            if (len(text) == 4):
                self.filesystem.copy_file(text[2], text[3], text[1])
            elif (len(text) == 3):
                self.filesystem.copy_file(text[1], text[2])
            else:
                print("Wrong number of arguments")
        elif (text[0] == "write"):
            if (text[1] == "-a" or text[1] == "-c"):
                self.filesystem.write_file(
                    text[2], ' '.join(text[3:]), text[1])
            else:
                self.filesystem.write_file(text[1], ' '.join(text[2:]))
        else:
            print("Invalid Command")

    def parse_edit_mode_output(self, text, rh: ReadHandler, wh: WriteHandler):
        text = text.split(" ")
        if (text[0] == "read_line"):
            out = rh.read_line()
            # Only strip \n in the simmulator
            # because print already adds a newline
            if (len(out) > 1 and out[-1] == "\n"):
                out = out[:-1]
            if (len(out) > 1):
                print(out)
        elif (text[0] == "read_to_end"):
            print(rh.read_to_end())
        elif (text[0] == "read_next"):
            if (len(text) == 0):
                print("Missing arguments")
            else:
                print(rh.read_next(int(text[1])))
        elif (text[0] == "move_abs"):
            if (len(text) < 3):
                print("Missing arguments")
            elif (text[1] == "r"):
                rh.move_cursor_abs(int(text[2]))
            elif (text[1] == "w"):
                wh.move_cursor_abs(int(text[2]))
            else:
                print("Please specifiy r or w cursor")
        elif (text[0] == "move_rel"):
            if (len(text) < 3):
                print("Missing arguments")
            elif (text[1] == "r"):
                rh.move_cursor_rel(int(text[2]))
            elif (text[1] == "w"):
                wh.move_cursor_rel(int(text[2]))
            else:
                print("Please specifiy r or w cursor")
        elif (text[0] == "insert"):
            if (len(text) < 2):
                print("Missing Arguments")
            else:
                wh.insert(text[1])
        elif (text[0] == "print_cursor"):
            print("read cursor: " + str(rh.cursor))
            print("write cursor: " + str(wh.cursor))
        else:
            print("invalid command")

    def enter_edit_mode(self, path: str):
        welcome_text = '''
        **Welcome to EditMode**
            Commands:
            read_line       -> reads next line
            read_to_end     -> reads from cursor to end
            read_next <int> -> reads next <int> chars
            insert <text>    -> inserts text at current write cursor
            move_abs [r/w] <int>  -> moves read/write cursor to absolute position <int>
            move_rel [r/w] <int>  -> move read/write cursor with relative position
            print_cursor    -> (debug) print cursor number
            exit            -> exit EditMode
        '''
        print(welcome_text)
        rh = self.filesystem.getFileHandlerFromPath(path, is_write=False)
        rh.open()
        wh = self.filesystem.getFileHandlerFromPath(path, is_write=True)
        wh.open()

        inp = input("> ")
        while (inp != "exit"):
            try:
                self.parse_edit_mode_output(inp, rh, wh)
            except Exception as e:
                print(e)
            inp = input("> ")
        print("Exiting EditMode; Going back to cmdline\n\n")
        rh.close()
        wh.close()

    def start(self):
        print("**Command line Test**")
        print("**type 'help' for options**")

        text = input("> ")
        while (text != "exit"):
            try:
                self.parse_output(text)
            except Exception as e:
                print(e)
            text = input("> ")


s = Simulator()
s.start()
