#!/usr/bin/env python
##===-- sandbox.py -------------------------------------------*- Python -*-===##
##
##                     The LLVM Compiler Infrastructure
##
## This file is distributed under the University of Illinois Open Source
## License. See LICENSE.TXT for details.
##
##===----------------------------------------------------------------------===##



import curses

import os
import signal
import sys

import Queue

import cui

event_queue = None

class SandboxUI(cui.CursesUI):
  def __init__(self, screen, event_queue):
    super(SandboxUI, self).__init__(screen, event_queue)

    height, width = self.screen.getmaxyx()
    w2 = width / 2
    h2 = height / 2

    self.wins = []
    #self.wins.append(cui.TitledWin(w2, h2, w2, h2, "Test Window 4"))
    list_win = cui.ListWin(w2, h2, w2, h2)
    for i in range(0, 40):
      list_win.addItem('Item {0!s}'.format(i))
    self.wins.append(list_win)
    self.wins.append(cui.TitledWin( 0,  0, w2, h2, "Test Window 1"))
    self.wins.append(cui.TitledWin(w2,  0, w2, h2, "Test Window 2"))
    self.wins.append(cui.TitledWin( 0, h2, w2, h2, "Test Window 3"))

    #def callback(s, content):
    #  self.wins[0].win.scroll(1)
    #  self.wins[0].win.addstr(10, 0, '%s: %s' % (s, content))
    #  self.wins[0].win.scroll(1)
    #  self.el.showPrompt(10, 0)

    #self.wins[0].win.scrollok(1)
    #self.el = cui.CursesEditLine(self.wins[0].win, None,
    #  lambda c: callback('got', c), lambda c: callback('tab', c))
    #self.el.prompt = '>>> '
    #self.el.showPrompt(10, 0)

  def handleEvent(self, event):
    if isinstance(event, int):
      if event == ord('q'):
        sys.exit(0)
      #self.el.handleEvent(event)
    super(SandboxUI, self).handleEvent(event)

def main(screen):
  global event_queue
  event_queue = Queue.Queue()

  sandbox = SandboxUI(screen, event_queue)
  sandbox.eventLoop()

if __name__ == "__main__":
  try:
    curses.wrapper(main)
  except KeyboardInterrupt:
    exit()
