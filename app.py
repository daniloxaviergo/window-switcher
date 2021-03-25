import subprocess
from tkinter import Tk
from window_switcher.window import Window
import gi
import timeit
import sys

# start = timeit.default_timer()

reload(sys)
sys.setdefaultencoding('utf-8')

gi.require_version('Gdk', '3.0') 
from gi.repository import Gdk

screen = Gdk.Screen.get_default()
monitor = screen.get_monitor_at_window(screen.get_active_window())
monitor = screen.get_monitor_geometry(monitor)

ws = monitor.width
hs = monitor.height - 200
w = int(ws / 2)
h = 40

options = {
  'inicial_find': False,
  'only_windows': False,
  'only_tabs': False
}

if len(sys.argv) > 1:
  options['inicial_find'] = sys.argv[1] == 'inicial'

  if len(sys.argv) > 2:
    options['only_windows'] = sys.argv[2] == 'only_windows'
    options['only_tabs'] = sys.argv[2] == 'only_tabs'

root = Tk()
window = Window(root, w, h, options)
# print('Time to start {0:.3f}'.format(timeit.default_timer() - start))

root.mainloop()
