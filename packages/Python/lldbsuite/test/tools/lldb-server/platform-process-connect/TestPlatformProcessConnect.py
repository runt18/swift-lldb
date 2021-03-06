from __future__ import print_function

import gdbremote_testcase
from lldbsuite.test.lldbtest import *
import lldbsuite.test.lldbutil as lldbutil

class TestPlatformProcessConnect(gdbremote_testcase.GdbRemoteTestCaseBase):
    mydir = TestBase.compute_mydir(__file__)

    @llgs_test
    @no_debug_info_test
    @skipIf(remote=False)
    @expectedFailureAll(hostoslist=["windows"], triple='.*-android')
    def test_platform_process_connect(self):
        self.build()
        self.init_llgs_test(False)

        working_dir = lldb.remote_platform.GetWorkingDirectory()
        err = lldb.remote_platform.Put(lldb.SBFileSpec(os.path.join(os.getcwd(), "a.out")),
                                       lldb.SBFileSpec(os.path.join(working_dir, "a.out")))
        if err.Fail():
            raise RuntimeError("Unable copy '{0!s}' to '{1!s}'.\n>>> {2!s}".format(f, wd, err.GetCString()))

        port_file = "{0!s}/port".format(working_dir)
        commandline_args = ["platform", "--listen", "*:0", "--socket-file", port_file, "--", "{0!s}/a.out".format(working_dir), "foo"]
        self.spawnSubprocess(self.debug_monitor_exe, commandline_args, install_remote=False)
        self.addTearDownHook(self.cleanupSubprocesses)
        new_port = self.run_shell_cmd("while [ ! -f {0!s} ]; do sleep 0.25; done && cat {1!s}".format(port_file, port_file))

        new_debugger = lldb.SBDebugger.Create()
        new_debugger.SetAsync(False)
        def del_debugger(new_debugger=new_debugger):
            del new_debugger
        self.addTearDownHook(del_debugger)

        new_platform = lldb.SBPlatform(lldb.remote_platform.GetName())
        new_debugger.SetSelectedPlatform(new_platform)
        new_interpreter = new_debugger.GetCommandInterpreter()

        m = re.search("(.*):[0-9]+", configuration.lldb_platform_url)
        command = "platform connect {0!s}:{1!s}".format(m.group(1), new_port)
        result = lldb.SBCommandReturnObject()
        new_interpreter.HandleCommand(command, result)
        self.assertTrue(result.Succeeded(), "platform process connect failed: {0!s}".format(result.GetOutput()))

        target = new_debugger.GetSelectedTarget()
        process = target.GetProcess()
        thread = process.GetThreadAtIndex(0)

        breakpoint = target.BreakpointCreateByName("main")
        process.Continue()

        frame = thread.GetFrameAtIndex(0)
        self.assertEqual(frame.GetFunction().GetName(), "main")
        self.assertEqual(frame.FindVariable("argc").GetValueAsSigned(), 2)
        process.Continue()
