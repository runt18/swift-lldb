"""
                     The LLVM Compiler Infrastructure

This file is distributed under the University of Illinois Open Source
License. See LICENSE.TXT for details.

Prepares language bindings for LLDB build process.  Run with --help
to see a description of the supported command line arguments.
"""

# Python modules:
import os
import platform
import sys


def _find_file_in_paths(paths, exe_basename):
    """Returns the full exe path for the first path match.

    @params paths the list of directories to search for the exe_basename
    executable
    @params exe_basename the name of the file for which to search.
    e.g. "swig" or "swig.exe".

    @return the full path to the executable if found in one of the
    given paths; otherwise, returns None.
    """
    for path in paths:
        trial_exe_path = os.path.join(path, exe_basename)
        if os.path.exists(trial_exe_path):
            return os.path.normcase(trial_exe_path)
    return None

def find_executable(executable):
    """Finds the specified executable in the PATH or known good locations."""

    # Figure out what we're looking for.
    if platform.system() == "Windows":
        executable = executable + ".exe"
        extra_dirs = []
    else:
        extra_dirs = ["/usr/local/bin"]

    # Figure out what paths to check.
    path_env = os.environ.get("PATH", None)
    if path_env is not None:
        paths_to_check = path_env.split(os.path.pathsep)
    else:
        paths_to_check = []

    # Add in the extra dirs
    paths_to_check.extend(extra_dirs)
    if len(paths_to_check) < 1:
        raise os.OSError(
            "executable was not specified, PATH has no "
            "contents, and there are no extra directories to search")

    result = _find_file_in_paths(paths_to_check, executable)

    if not result or len(result) < 1:
        raise os.OSError(
            "failed to find exe='{0!s}' in paths='{1!s}'".format(executable, paths_to_check))
    return result

