#!/usr/bin/env python3

from bottle import route, run, response
from data.entries import entries


index_dcim = open('data/index_dcim.html').read()
index_olymp = open('data/index_dcim_100olymp.html').read()

name_to_entry = {entry.name: entry for entry in entries}

@route('/DCIM')
def index():
    return index_dcim

@route('/DCIM/100OLYMP')
def index():
    return index_olymp

@route('/DCIM/100OLYMP/<name>')
def media(name):
    entry = name_to_entry[name]
    response.content_type = 'image/jpeg'
    response.content_length = entry.size
    return b'1' * entry.size

run(host='localhost')
