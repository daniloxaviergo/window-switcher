from tkinter import Entry, Listbox, StringVar
import sys, tkinter, subprocess
from window_switcher.aux import get_windows

import re
import unicodedata

class Window:
    FONT = ('Monospace', 13)
    ITEM_HEIGHT = 22
    MAX_FOUND = 50
    BG_COLOR = '#202b3a'
    FG_COLOR = '#ced0db'

    def resize(self, items):
        if self.resized:
            return

        self.root.geometry('{0}x{1}+4853+1129'.format(self.width, self.height))
        self.resized = True

    def __init__(self, root, width, height, options):
        self.root = root
        self.width = 2000
        self.height = 700
        self.options = options
        self.inicial_find = self.options['inicial_find']
        self.all_windows = []
        self.resized = False

        # master.geometry(500)
        root.title("window switcher")
        root.resizable(width=True, height=True)
        root.configure(background=Window.BG_COLOR)

        # ugly tkinter code below
        sv = StringVar()
        sv.trace("w", lambda name, index, mode, sv=sv: self.on_entry(sv))

        self.main_entry = Entry(
            root,
            font=Window.FONT,
            width=1000,
            textvariable=sv,
            bg=Window.BG_COLOR,
            fg=Window.FG_COLOR,
            insertbackground=Window.FG_COLOR,
            bd=0
        )
        self.main_entry.grid(row=0, column=0, padx=10)
        self.main_entry.focus_set()

        self.listbox = Listbox(
            root,
            height=Window.ITEM_HEIGHT,
            font=Window.FONT,
            highlightthickness=0,
            borderwidth=0,
            bg=Window.BG_COLOR,
            fg=Window.FG_COLOR,
            selectbackground='#2c3c51',
            selectforeground='#cedaed'
        )
        self.listbox.grid(row=1, column=0, sticky='we', padx=10, pady=10)

        # key bindings
        self.main_entry.bind('<Control-a>', self.select_all)
        self.main_entry.bind('<Up>', self.select_prev)
        self.main_entry.bind('<Down>', self.select_next)
        self.main_entry.bind('<Return>', self.select_window)
        self.main_entry.bind('<Control-BackSpace>', self.entry_ctrl_bs)
        self.main_entry.bind('<Alt-BackSpace>', self.entry_ctrl_bs)
        self.listbox.bind('<Double-Button>', self.select_window)
        self.root.bind('<Escape>', lambda e: sys.exit())
        self.root.bind("<FocusOut>", lambda e: sys.exit())

        # sv.set('k1m1')
        # self.resize(Window.MAX_FOUND)
        self.initial_get(None)

    def initial_get(self, event):
        [self.all_windows, current_window] = get_windows(self.options)
        
        self.find_windows('')
        if self.inicial_find and current_window:
            search_text = 'k' + str(current_window.workspace+1) + 'm' + str(current_window.monitor)
            self.find_windows(search_text)

    def select_all(self, event):
        # select text
        self.main_entry.select_clear()
        self.main_entry.select_range(0, 'end')
        # move cursor to the end
        self.main_entry.icursor('end')

        return 'break'

    def find_windows(self, text):
        text = text.lower().encode("utf-8")
        words = re.split(r'\s+', text)

        mat = []
        for word in words:
            wword = unicode(word, 'utf-8')
            wword = unicodedata.normalize('NFD', wword).encode('ascii', 'ignore')
            if len(wword) > 0:
                mat.append(wword)

        # found = [window for window in self.all_windows if window['name'].find(text) != -1]
        # found = [window for window in self.all_windows if any(re.findall(r'|'.join(list_words), window['name']))]
        # found = [window for window in self.all_windows if any(re.findall(match_string, window['name']))]

        windows = self.all_windows
        if len(mat) > 0:
            window_types = {
                't': 'chromix-too',
                'w': 'wmctrl',
                's': 'sublime'

            }
            if window_types.get(mat[0]):
                windows = [window for window in windows if window['type'] == window_types.get(mat[0])]
                mat.remove(mat[0])

        # (?<!\S)(?:t\shub.*)(?!\S)
        match_string = r'({})'.format("|".join(mat))

        found = []
        for window in windows:
            if len(mat) == 0:
                found.append(window)
                continue;

            window_name = unicodedata.normalize('NFD', window['name']).encode('ascii', 'ignore')
            result = re.findall(match_string, window_name)
            if any(result) and len(set(result)) == len(mat):
                found.append(window)
        # print(found)

        self.found = found

        self.listbox.delete(0, 'end')

        for i, item in enumerate(found):
            if i >= Window.MAX_FOUND:
                break
            self.listbox.insert('end', str(item['name']))

        self.resize(min(len(found), Window.MAX_FOUND))

        # select first element
        self.listbox.selection_set(0)

    def select_next(self, event):
        if len(self.found) == 0:
            return

        idx = self.listbox.curselection()[0]
        max = self.listbox.size()
        idx += 1
        if idx >= max:
            idx = 0

        self.listbox.selection_clear(0, 'end')
        self.listbox.selection_set(idx)

    def select_prev(self, event):
        if len(self.found) == 0:
            return

        idx = self.listbox.curselection()[0]
        max = self.listbox.size()
        idx -= 1
        if idx < 0:
            idx = max - 1

        self.listbox.selection_clear(0, 'end')
        self.listbox.selection_set(idx)

    def select_window(self, event):
        idx = self.listbox.curselection()[0]

        self.found[idx]['set_focus']()
        sys.exit(0)

    def entry_ctrl_bs(self, event):
        ent = event.widget
        end_idx = ent.index('insert')
        start_idx = ent.get().rfind(" ", None, end_idx)
        ent.selection_range(start_idx, end_idx)

    def on_entry(self, newtext):
        search_test = newtext.get()
        self.find_windows(search_test)
        return True
