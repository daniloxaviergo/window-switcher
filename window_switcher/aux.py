from subprocess import check_output

import sys
import os
import re
import json

sys.path.append("/home/danilo/scripts/")

from wmctrl_window import WmctrlWindow
from chromix_too_tab import ChromixTooTab
from sublime_tab import SublimeTab

def get_windows(options):
    all_windows = []
    current_window = {}

    if not options['only_tabs']:
        wmctrl_out = check_output(['wmctrl', '-dliGux'])#.decode('utf-8')
        wmctrl_out = wmctrl_out.split('\n')
        wmctrl_out.pop()

        outt = os.popen('/home/danilo/scripts/get_current_window.sh').read()
        current_window_id = outt.replace(',', '').split('x')[1]
        current_window_id = re.sub(r'(\r\n\t|\n|\r\t|\n)', '', current_window_id)

        current_window = None
        for window in wmctrl_out[::-1]:
            ctrlWindow = WmctrlWindow(unicode(window, 'utf-8'))

            if window.find(current_window_id) >= 0:
                current_window = WmctrlWindow(window)

            id = ctrlWindow.id
            name = 'k' + str(ctrlWindow.workspace +1) + 'm' + str(ctrlWindow.monitor) + ' ' + ctrlWindow.kname
            if ctrlWindow.workspace +1 > 0:
                all_windows.append({
                    'id': ctrlWindow.id,
                    'type': ctrlWindow.type,
                    'set_focus': ctrlWindow.set_focus,
                    'name': name.lower()
                })

    all_tabs = []
    if not options['only_windows']:
        try:
            chromix_out = check_output(['chromix-too', 'ls']).decode('utf-8')
        except BaseException:
            chromix_out = ''

        chromix_out = chromix_out.split('\n')

        if len(chromix_out) < 2:
            return [all_windows, current_window]

        for tab in chromix_out:
            if len(tab) > 5:
                all_tabs.append(ChromixTooTab(tab))

        all_tabs.sort(key=lambda x: x.id, reverse=True)
        for tab in all_tabs:
            prefix = 't '
            if options['only_tabs']:
                prefix = ''

            all_windows.append({
                'id': tab.id,
                'type': tab.type,
                'set_focus': tab.set_focus,
                'name': prefix + tab.domain + ' ' + tab.title.lower()
            })

    all_sublime = []
    if not options['only_sublime']:
        str_json = open("/home/danilo/scripts/sublime_tabs.json", "r").read()
        sublime_tabs = json.loads(str_json)

        for window_id in sublime_tabs.keys():
            for idx, path_file in enumerate(sublime_tabs[window_id], start=0):
                sublime_tab = SublimeTab(window_id, path_file, idx)
                all_windows.append({
                    'id': sublime_tab.id,
                    'type': sublime_tab.type,
                    'set_focus': sublime_tab.set_focus,
                    'name': 's ' + sublime_tab.title
                })

    return [all_windows, current_window]
