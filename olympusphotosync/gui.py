import os
import sys
import argparse
import threading

from tkinter import *
from tkinter import filedialog, messagebox
from tkinter.ttk import *
from urllib.parse import urlparse
from http.client import HTTPConnection

from . import oishare, utils


class Application(object):
    def __init__(self, url, destdir):
        self.root = Tk()

        self.style = Style()
        self.style.theme_use('default')
        self.style.configure('TreeView', font=('monospace', 11))
        self.style.configure('Entry', font=('monospace', 11))

        lpbar_style = ('LabeledProgressbar.trough', {
            'children': [
                ('LabeledProgressbar.pbar', {'side': 'left', 'sticky': 'ns'}),
                ('LabeledProgressbar.label', {'sticky': ''})
            ],
            'sticky': 'nswe'
        })
        self.style.layout('LabeledProgressbar', [lpbar_style])
        self.root.title('Olympus Photosync')

        self.setup_vars(url, destdir)
        self.setup_widgets(self.root)

    def setup_vars(self, url, destdir):
        self.url = StringVar()
        self.destdir = StringVar()
        self.destdir.set(destdir)
        self.url.set(url)

    def setup_widgets(self, root):
        content = Frame(root)
        content.grid(column=0, row=0, sticky='nswe')

        lb_url = Label(content, text='Camera URL:', justify='left')
        en_url = Entry(content, textvariable=self.url, justify='right')
        bt_lst = Button(content, text='List', compound='left', command=self.list_action)

        lb_url.grid(row=0, column=0, padx=5)
        en_url.grid(row=0, column=1, sticky='ew')
        bt_lst.grid(row=0, column=2, padx=5)

        lb_dst = Label(content, text='Destination:', justify='left')
        en_dst = Entry(content, textvariable=self.destdir, justify='right')
        en_dst.bind('<Button-1>', self.set_destdir)

        bt_get = Button(content, text='Download', compound='left', state='disabled', command=self.download_action)

        lb_dst.grid(row=1, column=0)
        en_dst.grid(row=1, column=1, sticky='ew')
        bt_get.grid(row=1, column=2)
        self.bt_get = bt_get

        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        content.columnconfigure(1, weight=1)
        content.rowconfigure(2, weight=1)

        tree = Treeview(content)
        tree['columns'] = ('size', 'timestamp')
        tree.heading('#0', text='Name', anchor='w')
        tree.column('#0', anchor='w', minwidth=100)
        tree.heading('size', text='Size')
        tree.column('size', anchor='e', minwidth=100, width=100, stretch=False)
        tree.bind('<Control-a>', self.tree_select_all)
        tree.bind('<<TreeviewSelect>>', self.tree_select_event)

        tree.heading('timestamp', text='Timestamp')
        tree.column('timestamp', anchor='c', minwidth=200, width=200, stretch=False)
        tree.grid(row=2, column=0, columnspan=3, sticky='nswe')

        treescroll = Scrollbar(content, orient='vertical', command=tree.yview)
        treescroll.grid(row=2, column=2, sticky='nse')

        tree.configure(yscrollcommand=treescroll.set)
        self.tree = tree

        pbar = Progressbar(content, orient='horizontal', mode='determinate', style='LabeledProgressbar')
        pbar.grid(row=3, column=0, columnspan=3, sticky='ew')
        self.pbar = pbar

    def set_destdir(self, event):
        d = filedialog.askdirectory()
        self.destdir.set(d)

    def tree_select_all(self, event):
        self.tree.selection_set(self.tree.get_children())

    def tree_select_event(self, event):
        if self.tree.selection():
            self.bt_get['state'] = 'enabled'
        else:
            self.bt_get['state'] = 'disabled'

    def download_action(self):
        if not self.destdir.get():
            messagebox.showerror('Error', 'Destination directory not set')
            return

        names = [self.tree.item(i)['text'] for i in self.tree.selection()]
        entries = [self.name_to_entry[name] for name in names]

        t1 = DownloadThread(self, entries, self.destdir.get())
        t1.daemon = True
        t1.start()

    def list_action(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        url = urlparse(self.url.get())
        self.conn = HTTPConnection(url.hostname, url.port)
        entries = oishare.find_entries(self.conn, '/DCIM/100OLYMP')
        self.name_to_entry = {i.name: i for i in entries}

        for entry in self.name_to_entry.values():
            val = (utils.sizefmt(entry.size), entry.timestamp.strftime('%c'))
            self.tree.insert('', 'end', text=entry.name, values=val)

    def progressbar_reset(self):
        self.pbar['maximum'] = 0
        self.pbar.step(0)

    def progressbar_desc(self, size, name):
        self.pbar['maximum'] = size
        self.style.configure('LabeledProgressbar', text=name)


class DownloadThread(threading.Thread):
    def __init__(self, app, entries, destdir):
        self.app = app
        self.entries = entries
        self.destdir = destdir
        self.stop_event = threading.Event()
        super().__init__()

    def download(self, fh, entry):
        for data in oishare.download(self.app.conn, entry):
            # Very inefficient but the alternatives require more work.
            if self.stop_event.is_set():
                return
            fh.write(data)
            self.app.pbar.step(len(data))

    def run(self):
        entry_iter = iter(self.entries)
        entry = next(entry_iter, None)
        while entry and not self.stop_event.is_set():
            dest = os.path.join(self.destdir, entry.name)
            with open(dest, 'wb') as fh:
                self.app.progressbar_reset()
                self.app.progressbar_desc(entry.size, entry.name)
                self.download(fh, entry)
            entry = next(entry_iter, None)
        self.app.style.configure('LabeledProgressbar', text='')


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-u', '--url', default='http://192.168.0.10:80/DCIM/100OLYMP', help='oishare base url')
    parser.add_argument('-d', '--destdir', default=os.path.abspath(os.curdir), help='destination directory')
    args = parser.parse_args()
    app = Application(args.url, args.destdir)
    app.root.mainloop()
