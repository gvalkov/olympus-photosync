from pytest import mark, raises

from datetime import datetime as dt, timedelta as td
from olympusphotosync import utils


now = dt.now().replace(microsecond=0)

@mark.parametrize('spec,expect', [
    ('2017/11/20',          dt(2017, 11, 20, 0, 0)),
    ('2017-11-20',          dt(2017, 11, 20, 0, 0)),
    ('2017-10-29T12:52:09', dt(2017, 10, 29, 12, 52, 9)),
    ('2017-10-29 12:52',    dt(2017, 10, 29, 12, 52, 0)),
    ('12:52:09',            now.replace(hour=12, minute=52, second=9)),
    ('12:52',               now.replace(hour=12, minute=52, second=0)),
    ('today',               now.replace(hour=0, minute=0, second=0)),
    ('1h',                  now - td(hours=1)),
    ('10d',                 now - td(days=10)),
])
def test_parse_timespec(spec, expect):
    assert utils.parse_timespec(spec) == expect


def test_parse_timespec_failure():
    assert utils.parse_timespec('not a date') is None


@mark.parametrize('size,expect', [
    (2048,       '2.00KiB'),
    (123235,     '120.35KiB'),
    (121234624,  '115.62MiB'),
    (2**34,      '16.00GiB'),
])
def test_sizefmt(size, expect):
    assert utils.sizefmt(size) == expect


@mark.parametrize('fname,expect', [
    ('PA001123.jpg', 10001123),
    ('AA001123.jpg', None),
    ('P0000001.jpg', 1),
    ('PF000000.jpg', 15000000),
])
def test_parse_fname(fname, expect):
    assert utils.parse_filename(fname) == expect
