from tkinter import *
from tkinter.ttk import *
from urllib.parse import urlparse
from http.client import HTTPConnection

from . import oishare, utils


class App(object):
    def __init__(self):
        self.root = Tk()

        self.style = Style()
        self.style.theme_use('default')
        self.style.configure('TreeView', font=('monospace', 11))
        self.style.configure('Entry', font=('monospace', 11))

        self.root.title('Olympus Photosync')

        self.cb_validate_port = self.root.register(self.validate_port)

        self.setup_vars()
        self.setup_widgets(self.root)

    def setup_vars(self):
        self.url = StringVar()
        self.destdir = StringVar()
        #self.url.set('http://192.168.0.10:80/DCIM/100OLYMP')
        self.url.set('http://localhost:8080/DCIM/100OLYMP')

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
        bt_get = Button(content, text='Download', compound='left', command=self.download_action)

        lb_dst.grid(row=1, column=0)
        en_dst.grid(row=1, column=1, sticky='ew')
        bt_get.grid(row=1, column=2)

        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        content.columnconfigure(1, weight=1)
        content.rowconfigure(2, weight=1)

        tree = Treeview(content)
        tree['columns'] = ('size', 'timestamp')
        tree.heading('#0', text='Name', anchor='w')
        tree.column('#0', anchor='w')
        tree.heading('size', text='Size')
        tree.column('size', anchor='e', minwidth=100, width=100, stretch=False)

        tree.heading('timestamp', text='Timestamp')
        tree.column('timestamp', anchor='c', minwidth=175, width=175, stretch=False)
        tree.grid(row=2, column=0, columnspan=3, sticky='nswe')

        scroll = Scrollbar(content, orient='vertical', command=tree.yview)
        scroll.grid(row=2, column=2, sticky='nse')

        tree.configure(yscrollcommand=scroll.set)

        self.tree = tree

    def set_destdir(self, event):
        d = filedialog.askdirectory()
        self.destdir.set(d)

    def validate_port(self, P):
        return str.isdigit(P) or P == ''

    def download_action(self):
        if not self.destdir.get():
            pass

    def list_action(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        url = urlparse(self.url.get())
        self.conn = HTTPConnection(url.hostname, url.port)
        self.entries = oishare.find_entries(self.conn, '/DCIM/100OLYMP')

        for entry in self.entries:
            val = (utils.sizefmt(entry.size), entry.timestamp)
            self.tree.insert('', 'end', text=entry.name, values=val)


def main():
    app = App()
    app.root.mainloop()
