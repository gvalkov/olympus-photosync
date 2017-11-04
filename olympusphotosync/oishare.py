import os
import re

from collections import namedtuple
from datetime import datetime

from . import utils


Entry = namedtuple('Entry', 'root name size timestamp')


def download(conn, entry, chunksize=8192):
    srcpath = os.path.join(entry.root, entry.name)
    resp = utils.httpget(conn, srcpath, stream=True)

    while not resp.isclosed():
        yield resp.read(chunksize)


def find_entries(conn, baseurl):
    html = utils.httpget(conn, baseurl)
    return parse_index(html)


def filter_by_date(entries, newer_than=None, older_than=None):
    for entry in entries:
        if newer_than and entry.timestamp <= newer_than:
            continue

        if older_than and entry.timestamp >= older_than:
            continue

        yield entry


def parse_index(html):
    for entry in re.findall(rb'wlan.*?\[\d+?\]="(.*?)";', html):
        root, name, size, _, date, time = entry.lstrip(b'/').split(b',')
        root, name = root.decode('utf8'), name.decode('utf8')
        timestamp = parse_date_time(int(date), int(time))

        yield Entry(root, name, int(size), timestamp)


def parse_date_time(date, time):
    da = (0b0000000000011111 & date) >> 0
    mo = (0b0000000111100000 & date) >> 5
    yr = (0b1111111000000000 & date) >> 9

    dd = (0b1111100000000000 & time) >> 11
    mm = (0b0000011111100000 & time) >> 5
    ss = (0b0000000000011111 & time)

    return datetime(yr + 1980, mo, da, dd, mm, ss)
