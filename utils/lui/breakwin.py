##===-- breakwin.py ------------------------------------------*- Python -*-===##
##
##                     The LLVM Compiler Infrastructure
##
## This file is distributed under the University of Illinois Open Source
## License. See LICENSE.TXT for details.
##
##===----------------------------------------------------------------------===##

import cui
import curses
import lldb, lldbutil
import re

class BreakWin(cui.ListWin):
  def __init__(self, driver, x, y, w, h):
    super(BreakWin, self).__init__(x, y, w, h)
    self.driver = driver
    self.update()
    self.showDetails = {}

  def handleEvent(self, event):
    if isinstance(event, lldb.SBEvent):
      if lldb.SBBreakpoint.EventIsBreakpointEvent(event):
        self.update()
    if isinstance(event, int):
      if event == ord('d'):
        self.deleteSelected()
      if event == curses.ascii.NL or event == curses.ascii.SP:
        self.toggleSelected()
      elif event == curses.ascii.TAB:
        if self.getSelected() != -1:
          target = self.driver.getTarget()
          if not target.IsValid():
            return
          i = target.GetBreakpointAtIndex(self.getSelected()).id
          self.showDetails[i] = not self.showDetails[i]
          self.update()
    super(BreakWin, self).handleEvent(event)

  def toggleSelected(self):
    if self.getSelected() == -1:
      return
    target = self.driver.getTarget()
    if not target.IsValid():
      return
    bp = target.GetBreakpointAtIndex(self.getSelected())
    bp.SetEnabled(not bp.IsEnabled())

  def deleteSelected(self):
    if self.getSelected() == -1:
      return
    target = self.driver.getTarget()
    if not target.IsValid():
      return
    bp = target.GetBreakpointAtIndex(self.getSelected())
    target.BreakpointDelete(bp.id)

  def update(self):
    target = self.driver.getTarget()
    if not target.IsValid():
      self.win.erase()
      self.win.noutrefresh()
      return
    selected = self.getSelected()
    self.clearItems()
    for i in range(0, target.GetNumBreakpoints()):
      bp = target.GetBreakpointAtIndex(i)
      if bp.IsInternal():
        continue
      text = lldbutil.get_description(bp)
      # FIXME: Use an API for this, not parsing the description.
      match = re.search('SBBreakpoint: id = ([^,]+), (.*)', text)
      try:
        id = match.group(1)
        desc = match.group(2).strip()
        if bp.IsEnabled():
          text = '{0!s}: {1!s}'.format(id, desc)
        else:
          text = '{0!s}: (disabled) {1!s}'.format(id, desc)
      except ValueError as e:
        # bp unparsable
        pass

      if self.showDetails.setdefault(bp.id, False):
        for location in bp:
          desc = lldbutil.get_description(location, lldb.eDescriptionLevelFull)
          text += '\n  ' + desc
      self.addItem(text)
    self.setSelected(selected)
