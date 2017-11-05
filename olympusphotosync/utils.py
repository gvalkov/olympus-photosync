import re
from datetime import datetime, timedelta


def sizefmt(num):
    for unit in '', 'Ki', 'Mi':
        if abs(num) < 1024.0:
            return '{:3.2f}{}B'.format(num, unit)
        num /= 1024.0
    return '{:3.2f}GiB'.format(num)


def remove_duplicates(seq):
    seen = set()
    return [x for x in seq if not (x in seen or seen.add(x))]


def httpget(conn, url, check=True, stream=False):
    conn.request('GET', '/' + url.lstrip('/'))
    resp = conn.getresponse()
    if check:
        assert resp.status == 200
    return resp if stream else resp.read()


def parse_short_timespec(dt_str):
    m = re.match('^(\d+)([smhdw])$', dt_str)
    if not m:
        return

    now = datetime.now().replace(microsecond=0)
    value, magnitude = m.groups()

    timedelta_kw = {'s': 'seconds', 'm': 'minutes', 'h': 'hours', 'd': 'days', 'w': 'weeks'}
    kw = {timedelta_kw[magnitude]: int(value)}
    return now - timedelta(**kw)


def parse_timespec(dt_str):
    formats = (
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%Y-%m-%d',
        '%Y-%m',
        '%Y',
        '%H:%M:%S',
        '%H:%M',
    )

    dt_str = dt_str.replace('/', '-')
    now = datetime.now()

    def try_parse(f):
        if dt_str == 'today':
            return now.replace(hour=0, minute=0, second=0, microsecond=0)

        short_spec = parse_short_timespec(dt_str)
        if short_spec:
            return short_spec

        try:
            dt = datetime.strptime(dt_str, f)
            if dt.year == 1900:
                dt = dt.replace(year=now.year, month=now.month, day=now.day)
            return dt
        except ValueError:
            pass

    for dt in map(try_parse, formats):
        if dt:
            return dt
    else:
        raise ValueError('time specifier "%s" could not be parsed' % dt_str)
