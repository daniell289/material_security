# Utils class to manipulate path

# Return (list of preceding directories, last file/dir name, is_absolute)
#
# /a/b/c/file_name -> ([a,b,c], file_name, true) absolute paths have leading slash
# a/b/c/file_name -> ([a,b,c], file_name, false) relative paths miss the leading slash
# a/c/ -> ([a,c], "", false) empty file name is due to trailing slash
def parse_path_with_ending_name(path: str) -> tuple[list[str], str, bool]:
    pathes = path.strip().split("/")
    is_absolute = False
    if (pathes[0] == ""):
        is_absolute = True
        # strip off the empty root
        pathes = pathes[1:]
    return pathes[0:-1], pathes[-1], is_absolute

# Return (list of in order directories, is_absolute)
#
# /a/b/c/ -> ([a,b,c], true)
# a/b/c/ -> ([a,b,c], false)
# Used when the entire path is meant to be directories
# such as for change directory
def parse_path(path: str) -> tuple[list[str], str, bool]:
    pathes = path.strip().split("/")
    is_absolute = False
    if (pathes[0] == ""):
        is_absolute = True
    # Doesn't matter if user puts a trailing slash or not
    pathes = list(filter(None, pathes))
    return pathes, is_absolute
