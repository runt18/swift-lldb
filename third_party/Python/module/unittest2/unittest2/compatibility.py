import os
import sys

try:
    from functools import wraps
except ImportError:
    # only needed for Python 2.4
    def wraps(_):
        def _wraps(func):
            return func
        return _wraps

__unittest = True

def _relpath_nt(path, start=os.path.curdir):
    """Return a relative version of a path"""

    if not path:
        raise ValueError("no path specified")
    start_list = os.path.abspath(start).split(os.path.sep)
    path_list = os.path.abspath(path).split(os.path.sep)
    if start_list[0].lower() != path_list[0].lower():
        unc_path, rest = os.path.splitunc(path)
        unc_start, rest = os.path.splitunc(start)
        if bool(unc_path) ^ bool(unc_start):
            raise ValueError("Cannot mix UNC and non-UNC paths ({0!s} and {1!s})".format(path, start))
        else:
            raise ValueError("path is on drive {0!s}, start on drive {1!s}".format(path_list[0], start_list[0]))
    # Work out how much of the filepath is shared by start and path.
    for i in range(min(len(start_list), len(path_list))):
        if start_list[i].lower() != path_list[i].lower():
            break
    else:
        i += 1

    rel_list = [os.path.pardir] * (len(start_list)-i) + path_list[i:]
    if not rel_list:
        return os.path.curdir
    return os.path.join(*rel_list)

# default to posixpath definition
def _relpath_posix(path, start=os.path.curdir):
    """Return a relative version of a path"""

    if not path:
        raise ValueError("no path specified")
    
    start_list = os.path.abspath(start).split(os.path.sep)
    path_list = os.path.abspath(path).split(os.path.sep)

    # Work out how much of the filepath is shared by start and path.
    i = len(os.path.commonprefix([start_list, path_list]))

    rel_list = [os.path.pardir] * (len(start_list)-i) + path_list[i:]
    if not rel_list:
        return os.path.curdir
    return os.path.join(*rel_list)

if os.path is sys.modules.get('ntpath'):
    relpath = _relpath_nt
else:
    relpath = _relpath_posix
