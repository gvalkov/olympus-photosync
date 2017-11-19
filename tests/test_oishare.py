from datetime import datetime as dt
from olympusphotosync.utils import parse_filename
from olympusphotosync.oishare import Entry, filter_entries


e1 = [
    Entry(root='', name=41, size=7969793, timestamp=dt(2017, 10, 25, 12, 50, 19)),
    Entry(root='', name=42, size=7981048, timestamp=dt(2017, 10, 25, 12, 50, 19)),
    Entry(root='', name=43, size=8236786, timestamp=dt(2017, 10, 25, 12, 50, 20)),
    Entry(root='', name=44, size=8050200, timestamp=dt(2017, 10, 25, 12, 52, 2)),
    Entry(root='', name=45, size=7971506, timestamp=dt(2017, 10, 25, 12, 52, 2)),
    Entry(root='', name=46, size=8044623, timestamp=dt(2017, 10, 26, 12, 52, 3)),
    Entry(root='', name=47, size=8231171, timestamp=dt(2017, 10, 26, 12, 52, 4)),
    Entry(root='', name=48, size=7903742, timestamp=dt(2017, 10, 27, 12, 52, 6)),
    Entry(root='', name=49, size=7982131, timestamp=dt(2017, 10, 27, 12, 52, 7)),
    Entry(root='', name=50, size=7863172, timestamp=dt(2017, 10, 27, 12, 52, 8)),
    Entry(root='', name=51, size=7813090, timestamp=dt(2017, 10, 27, 12, 52, 9)),
    Entry(root='', name=52, size=7806783, timestamp=dt(2017, 10, 29, 12, 52, 10)),
    Entry(root='', name=53, size=7760271, timestamp=dt(2017, 10, 29, 12, 52, 11)),
    Entry(root='', name=54, size=7651375, timestamp=dt(2017, 10, 29, 12, 52, 12)),
]

e2 = [
    Entry(root='', name='PA290941.JPG', size=7903742, timestamp=dt(2017, 10, 27, 12, 52, 6)),
    Entry(root='', name='PA290942.JPG', size=7982131, timestamp=dt(2017, 10, 27, 12, 52, 7)),
    Entry(root='', name='PA290943.JPG', size=7863172, timestamp=dt(2017, 10, 27, 12, 52, 8)),
    Entry(root='', name='PA290944.JPG', size=7813090, timestamp=dt(2017, 10, 27, 12, 52, 9)),
    Entry(root='', name='PA290945.JPG', size=7806783, timestamp=dt(2017, 10, 29, 12, 52, 10)),
    Entry(root='', name='PA290946.JPG', size=7760271, timestamp=dt(2017, 10, 29, 12, 52, 11)),
    Entry(root='', name='PA290947.JPG', size=7651375, timestamp=dt(2017, 10, 29, 12, 52, 12)),
]


def only_names(it):
    return {i.name for i in it}


def test_filter_timestamp():
    d = dt(2017, 10, 27, 12, 52, 6), 'timestamp'
    assert {49, 50, 51, 52, 53, 54}     == only_names(filter_entries(e1, newer_than=d))
    assert {41, 42, 43, 44, 45, 46, 47} == only_names(filter_entries(e1, older_than=d))

    nd = dt(2017, 10, 25, 12, 52, 2), 'timestamp'
    od = dt(2017, 10, 29, 12, 52, 10), 'timestamp'
    assert {51, 50, 49, 48, 47, 46} == only_names(filter_entries(e1, newer_than=nd, older_than=od))


def test_filter_name():
    d = parse_filename('PA290944'), 'name'
    assert {'PA290941.JPG', 'PA290942.JPG', 'PA290943.JPG'} == only_names(filter_entries(e2, older_than=d))
    assert {'PA290945.JPG', 'PA290946.JPG', 'PA290947.JPG'} == only_names(filter_entries(e2, newer_than=d))

    nd = parse_filename('PA290943'), 'name'
    od = parse_filename('PA290946'), 'name'
    assert {'PA290945.JPG', 'PA290944.JPG', 'PA290945.JPG'} == only_names(filter_entries(e2, newer_than=nd, older_than=od))


def test_filter_mixed():
    nd = parse_filename('PA290943'), 'name'
    od = dt(2017, 10, 29, 12, 52, 11), 'timestamp'
    assert {'PA290945.JPG', 'PA290944.JPG', 'PA290945.JPG'} == only_names(filter_entries(e2, newer_than=nd, older_than=od))
