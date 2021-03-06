#!/usr/bin/env python

"""This spawns a sub-shell (bash) and gives the user interactive control. The
entire shell session is logged to a file called script.log. This behaves much
like the classic BSD command 'script'.

./script.py [-a] [-c command] {logfilename}

    logfilename : This is the name of the log file. Default is script.log.
    -a : Append to log file. Default is to overwrite log file.
    -c : spawn command. Default is to spawn the sh shell.

Example:

    This will start a bash shell and append to the log named my_session.log:

        ./script.py -a -c bash my_session.log

"""

import os, sys, time, getopt
import signal, fcntl, termios, struct
import traceback
import pexpect

global_pexpect_instance = None # Used by signal handler

def exit_with_usage():

    print globals()['__doc__']
    os._exit(1)

def main():

    ######################################################################
    # Parse the options, arguments, get ready, etc.
    ######################################################################
    try:
        optlist, args = getopt.getopt(sys.argv[1:], 'h?ac:', ['help','h','?'])
    except Exception, e:
        print str(e)
        exit_with_usage()
    options = dict(optlist)
    if len(args) > 1:
        exit_with_usage()
        
    if [elem for elem in options if elem in ['-h','--h','-?','--?','--help']]:
        print "Help:"
        exit_with_usage()

    if len(args) == 1:
        script_filename = args[0]
    else:
        script_filename = "script.log"
    if '-a' in options:
        fout = file (script_filename, "ab")
    else:
        fout = file (script_filename, "wb")
    if '-c' in options:
        command = options['-c']
    else:
        command = "sh"

    # Begin log with date/time in the form CCCCyymm.hhmmss
    fout.write ('# {0:4d}{1:02d}{2:02d}.{3:02d}{4:02d}{5:02d} \n'.format(*time.localtime()[:-3]))
    
    ######################################################################
    # Start the interactive session
    ######################################################################
    p = pexpect.spawn(command)
    p.logfile = fout
    global global_pexpect_instance
    global_pexpect_instance = p
    signal.signal(signal.SIGWINCH, sigwinch_passthrough)

    print "Script recording started. Type ^] (ASCII 29) to escape from the script shell."
    p.interact(chr(29))
    fout.close()
    return 0

def sigwinch_passthrough (sig, data):

    # Check for buggy platforms (see pexpect.setwinsize()).
    if 'TIOCGWINSZ' in dir(termios):
        TIOCGWINSZ = termios.TIOCGWINSZ
    else:
        TIOCGWINSZ = 1074295912 # assume
    s = struct.pack ("HHHH", 0, 0, 0, 0)
    a = struct.unpack ('HHHH', fcntl.ioctl(sys.stdout.fileno(), TIOCGWINSZ , s))
    global global_pexpect_instance
    global_pexpect_instance.setwinsize(a[0],a[1])

if __name__ == "__main__":
    try:
        main()
    except SystemExit, e:
        raise e
    except Exception, e:
        print "ERROR"
        print str(e)
        traceback.print_exc()
        os._exit(1)

