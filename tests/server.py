#!/usr/bin/env python3

from bottle import response, route, run
from data.entries import entries

with open("data/index_dcim.html") as fh:
    index_dcim = fh.read()

with open("data/index_dcim_100olymp.html") as fh:
    index_olymp = fh.read()

name_to_entry = {entry.name: entry for entry in entries}


@route("/DCIM")
def index_dcim():
    return index_dcim


@route("/DCIM/100OLYMP")
def index_olymp():
    return index_olymp


@route("/DCIM/100OLYMP/<name>")
def media(name):
    entry = name_to_entry[name]
    response.content_type = "image/jpeg"
    response.content_length = entry.size
    return b"1" * entry.size


run(host="localhost")
