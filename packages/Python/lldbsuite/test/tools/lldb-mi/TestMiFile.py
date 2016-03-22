"""
Test lldb-mi -file-xxx commands.
"""

from __future__ import print_function



import lldbmi_testcase
from lldbsuite.test.lldbtest import *

class MiFileTestCase(lldbmi_testcase.MiTestCaseBase):

    mydir = TestBase.compute_mydir(__file__)

    @skipIfWindows #llvm.org/pr24452: Get lldb-mi tests working on Windows
    @skipIfFreeBSD # llvm.org/pr22411: Failure presumably due to known thread races
    def test_lldbmi_file_exec_and_symbols_file(self):
        """Test that 'lldb-mi --interpreter' works for -file-exec-and-symbols exe."""

        self.spawnLldbMi(args = None)

        # Test that -file-exec-and-symbols works for filename
        self.runCmd("-file-exec-and-symbols {0!s}".format(self.myexe))
        self.expect("\^done")

        # Run
        self.runCmd("-exec-run")
        self.expect("\^running")
        self.expect("\*stopped,reason=\"exited-normally\"")

    @skipIfWindows #llvm.org/pr24452: Get lldb-mi tests working on Windows
    @skipIfFreeBSD # llvm.org/pr22411: Failure presumably due to known thread races
    def test_lldbmi_file_exec_and_symbols_absolute_path(self):
        """Test that 'lldb-mi --interpreter' works for -file-exec-and-symbols fullpath/exe."""

        self.spawnLldbMi(args = None)

        # Test that -file-exec-and-symbols works for absolute path
        import os
        path = os.path.join(os.getcwd(), self.myexe)
        self.runCmd("-file-exec-and-symbols \"{0!s}\"".format(path))
        self.expect("\^done")

        # Run
        self.runCmd("-exec-run")
        self.expect("\^running")
        self.expect("\*stopped,reason=\"exited-normally\"")

    @skipIfWindows #llvm.org/pr24452: Get lldb-mi tests working on Windows
    @skipIfFreeBSD # llvm.org/pr22411: Failure presumably due to known thread races
    def test_lldbmi_file_exec_and_symbols_relative_path(self):
        """Test that 'lldb-mi --interpreter' works for -file-exec-and-symbols relpath/exe."""

        self.spawnLldbMi(args = None)

        # Test that -file-exec-and-symbols works for relative path
        path = "./{0!s}".format(self.myexe)
        self.runCmd("-file-exec-and-symbols {0!s}".format(path))
        self.expect("\^done")

        # Run
        self.runCmd("-exec-run")
        self.expect("\^running")
        self.expect("\*stopped,reason=\"exited-normally\"")

    @skipIfWindows #llvm.org/pr24452: Get lldb-mi tests working on Windows
    @skipIfFreeBSD # llvm.org/pr22411: Failure presumably due to known thread races
    def test_lldbmi_file_exec_and_symbols_unknown_path(self):
        """Test that 'lldb-mi --interpreter' works for -file-exec-and-symbols badpath/exe."""

        self.spawnLldbMi(args = None)

        # Test that -file-exec-and-symbols fails on unknown path
        path = "unknown_dir/{0!s}".format(self.myexe)
        self.runCmd("-file-exec-and-symbols {0!s}".format(path))
        self.expect("\^error")
