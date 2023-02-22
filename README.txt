Setup
    - Python 3.11, (for the type annotations)
    - run ./simulator.py for the cmdline demo
        - "help" to see all options
        - "editmode <file>" opens a second edit simulator to play with cursors
    - run python unittests on /tests/

Structure
    - filesystem.py is the core API impl
    - objects.py defines directories, files, file handlers
    - path_utils.py is a utils file for string parsing
    - simulator.py is a rough cmdline simulator
    - /tests/
        - /test_file_directory is the main test file
        - /test_file_read_write is for R W operations
        - /test_find is for the recursive find operation

Notes
    - Implemented base problem
        - + rough cmdline simulator
        - + file edit mode simulator (accessible within cmdline simulator)
    - Implemented move & copy files with name collision options
    - Implemented absolute/relative paths for all operations
        - including "../" to nav up to parent
        - "-p" option to create missing directories for create/mv operations
    - Implemented invoking arbitrary function recursing down subtree
        - Implemented recursive regex find
    - Implemented read and write cursors
        - Supports random access and moving cursors via relative/absolute positions
        - Read: Can read whole file, read from cursor->end, read line by line, read arbitrary chunk
        - Write: Can overrwrite whole file, append to file, or insert at cursor
    - See tests for corner cases

    - Focused on handling core API corner cases
        - e.g. no file name during create file
        - e.g. invalid path in all operations
        - e.g. name conflicts
        - e.g. complex dir structures
        - e.g. out of bounds for read/write cursor
    - Some error-checking on cmdline simulator parsing, but not totally bulletproof, as it's meant to be a quick demo
    - In general I decided to treat directories & files as separate entities
        - For example, when finding with "name", I return two output lists
        of both the matching files & matching directories respectively
        - I allow files & directories to coexist with the same name in the same dir
        Thus, create/remove/move operations are separate for file vs dir

****** API *******
**Commands**
    exit                exit the test simmulator
    mkdir [op]  <dir>   make a new directory (absolute or relative path)
          [-p]            Creates missing parent directories
    mkfile [op] <file>  make a new file (absolute or relative path)
          [-p]            Creates missing parent directories
    mvfile/cpfile [op] <source> <dest> 
                        Moves/Copies source file as dest, overriding name conflict files in dest
                        If a different filename is specified in dest than source, file is renamed
            [-b]          On file name conflict, a backup of the conflicting file is created with ~<filename>
            [-n]          On file name conflict, operation fails 
            [-p]          Creates missing parent directories along the Dest path
    pwd                 get current working directory path
    ls                  list current directory's subdirectories & files
    cd <path>           switch directory (absolute or relative path)
                            "../" is special and refers to parent directory
    rmdir <path>        delete that directory (recursively)
    rmfile <path>       delete that file
    find [op] <regex> <path> 
                        Finds all files/folders with matching regex name under path
                        Use find <regex> . to refer to the current directory
         [-r]           Recursively returns all matches under the subdirectories
    read <file>         read whole file
    write <file_path> contents
                        overwrite file with contents
    write [op] <file_path> contents
            [-c]           concats contents to file (no new line)
            [-a]           appends contents to file with new line

    ***Extra Modes***
    editmode <file>      open read/write mode with cursors
    """

*******Edit Mode ***********
    Commands:
    read_line       -> reads next line
    read_to_end     -> reads from cursor to end
    read_next <int> -> reads next <int> chars
    insert <text>    -> inserts text at current write cursor
    move_abs [r/w] <int>  -> moves read/write cursor to absolute position <int>
    move_rel [r/w] <int>  -> move read/write cursor with relative position
    print_cursor    -> (debug) print cursor number
    exit            -> exit EditMode

Note when moving cursors, you have to specify r or w


***********************

**Change Directory**
    cd <path>
    
    - Changes current working directory to specified path
    - cd /d1/d2 refers to absolute path
    - cd d1/d2 refers to relative path
    - ../ refers to parent
        e.g cd ../../ goes up 2 levels
        e.g cd d2/../ will return you to the same starting place
    - Returns T/F on success. False is for invalid path

**Get Current Directory**
    pwd
    - Gets current working directory path
    - e.g. pwd -> /a/b/c
    - e.g. pwd -> / if at root

**Make Directory**
    mkdir [op] <dest_path>
        -p recursively creates missing parent directories
    
    - Creates new directory specified at path. Fails if invalid path
    unless using -p, in which case it creates those missing directories
    - e.g. mkdir /d1/d2/d3 creates d3 under /d1/d2
    - e.g. mkdir -p /d1/d2/d3 ^also creates /d1/d2 if it doesn't exist
    - e.g. mkdir /d1/d2/d3/ -> FAIL, no directory name specified (due to trailing slash)
    - e.g. mkdir d1 relative path ok, makes d1 in current directory

**List Current Directory Contents**
    ls
    - Lists files & subdirectories separately
    - Note this implies files and directories can coexist
    with the same name at the same layer

**Remove a Directory**
    rmdir <path>
    - Deletes that directory
    - Meta-note (in a real filesystem you would implement -r to recursively delete it's contents)
        But because this is in memory; Unhooking the reference is enough to let the 
        garbage collector handle it

**Create a file**
    mkfile [op] <dest_path>
        -p recursively creates missing parent directories
    - Similar to mkdir but for files. See mkdir API for details. 
    - Same failure cases apply, since as missing filename at the end of path

**Remove a file**
    rmfile <path>
    - Deletes that file
    - Meta-note (in a real filesystem you would mark all the Inodes as deleted)
        But because this is in memory; Unhooking the reference is enough to let the 
        garbage collector handle it

**Move File**
    mvfile [op] <source_path> <dest_path>

    - Moves source file to dest
    - Can also use this to rename files
    - By default overrides name conflict files in dest
    - By default, fails w no-op if dest path is an invalid directory tree
    - Option [-b] On file name conflict, a backup of the conflicting file is created with ~<filename>
    - Option [-n] On file name conflict, operation fails
    - Option [-p] Creates missing parent directories along the Dest path

    Examples:
    mvfile file1 file2 => renames file1 to file2 in the same directory
    mvfile /d1/d2/file1 /d1/file2 => moves file1 from /d1/d2/ to /d1/, renamed as file2
    mvfile file1 /d1/ => moves file1 to d1; Not specifying dest file name keeps the same name
    mvfile /d1/d2/ /d1 => FAIL no source file specified (trailing slash)
    mvfile -b file1 file1 => [file1, ~file1] with the later as backup

**Copy File**
    cpfile [op] <source_path> <dest_path> 
    - Option [-b] On file name conflict, a backup of the conflicting file is created with ~<filename>
    - Option [-n] On file name conflict, operation fails
    - Option [-p] Creates missing parent directories along the Dest path

    - Same exact logic as move file except a copy of the source file is kept in place 

**Find File**
    find [-r] <regex> <path>  
    - Option [-r] makes it recursive

    - Finds all files/folders with matching regex name under path
    - Outputs tuple(list_files, list_folders)
    - e.g. find -r name[0-9]+ /dir1/dir2
        Recursively finds files/folders like name123 under /dir1/dir2        
        output = [/dir1/dir2/name1, /dir/dir2/name2, /dir1/dir2/dir3/dir4/name4], [] #empty if no matching directories
    - e.g. find -r ff* /
        [file1, file2], [fffDirectory, gDirectory/ffSubDirectory] # here both files and directories match

**Write File**
    write [op] <file_path> contents* 
    - By default overwrites the file with contents
    - Option [-a] appends contents to file with new line
    - Option [-c] concats contents to file without new line
    - Fails with no-op if file_path is invalid
    
    - E.g write file aaa; read file -> aaa
    - E.g write -a file bbb; read file -> aaa \n bbb
    - E.g write -c file ccc; read file -> aaa \n bbbccc
    - Note cmdline accepts multiple words for content
    - E.g. write /file Hi Material Security -> Valid

**Edit Mode**
    editmode <file_path>
    Special edit mode simulator detailed below

