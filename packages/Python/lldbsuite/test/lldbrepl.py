# lldbrepl.py
#
# This source file is part of the Swift.org open source project
#
# Copyright (c) 2014 - 2015 Apple Inc. and the Swift project authors
# Licensed under Apache License v2.0 with Runtime Library Exception
#
# See http://swift.org/LICENSE.txt for license information
# See http://swift.org/CONTRIBUTORS.txt for the list of Swift project authors
#
# ------------------------------------------------------------------------------
import lldb
from lldbpexpect import *
import lldbsuite.test.lldbutil as lldbutil
import os
import unittest2
import sys
import pexpect
import swift
import re
from lldbtest import no_debug_info_test

class REPLTest(PExpectTest):
    
    mydir = TestBase.compute_mydir(__file__)
    
    @swiftTest
    @no_debug_info_test
    def testREPL(self):
        # setup the regexp for the prompt
        self.prompt = re.compile('\\d+>')
        # launch the REPL..
        try:
            self.launch(timeout = 30)
            # and double check that it's there
            self.expect('Welcome to.*Swift')
            self.expect('Type :help for assistance')
            # responsive
            self.promptSync()
            # then do user things
            self.doTest()
        finally:
            try:
                # and quit
                self.quit(gracefully=False)
            except:
                pass

    def setUp(self):
        # Call super's setUp().
        PExpectTest.setUp(self)

    def launchArgs(self):
        return '-x "--repl=-enable-objc-interop -sdk {0!s} -color-diagnostics"'.format((swift.getSwiftSDKRoot()))

    # run a REPL command and wait for the prompt
    def command(self, command, patterns=None, timeout=None, exact=None, prompt_sync=True):
        self.sendline(command)
        if patterns is not None:
            if type(patterns) is list:
                self.expectall(patterns, timeout, exact=exact)
            else:
                self.expect(patterns, timeout, exact=exact)
        if prompt_sync:
            self.promptSync(timeout=timeout)

    # sync with the prompt
    def promptSync(self, timeout=None):
        self.expect(patterns=[self.prompt], timeout=timeout)

def load_tests(x, y, z):
    tests = []
    for test in y:
        testcase = test._tests[0]
        if type(testcase) is REPLTest: continue
        tests.append(test)
    return tests
