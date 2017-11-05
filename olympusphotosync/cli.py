import sys
import fnmatch
import textwrap
import optparse
from pathlib import Path
from http.client import HTTPConnection

from tqdm import tqdm

from . import __version__
from . import oishare
from . import utils


#-----------------------------------------------------------------------------
# Option parsing
#-----------------------------------------------------------------------------

def parseopts(argv=None):
    usage = '''
    Usage: {prog} [options] <get|list|sync> ...

    List, download and sync photos and videos from WiFi enabled Olympus cameras.

    Commands:
      get                     download files from camera
      list                    list media on camera
      sync                    pull missing files from camera

    General options:
      -h, --help              show this help message and exit
      -v, --version           show version number and exit
      -r, --parsable          no progress bars and no human readable dates and sizes

    Camera server options:
      -a, --addr ip|hostname  address of camera server (default: 192.168.0.10)
      -p, --port port         camera server port number (default: 80)
      -b, --baseurl path      url under which media is located (default: /DCIM/100OLYMP)
      -t, --timeout seconds   connection timeout (default: 60)

    Download options:
      -d, --destdir           destination directory (default: ./)
      name [name ...]         media files to download (example: PA290940.JPG)

    Synchronization options:
      destdir                 directory which to download media files

    Filter options:
      --older timefmt         select files older than $timefmt
      --newer timefmt         select files newer than $timefmt
      --on timefmt            select media from a specific day

    Examples:
      {prog} list --newer 2017-09-17T16:21:00 --older 2017-09-20
      {prog} list --newer 10d --older 12h
      {prog} list --on today
      {prog} get -d ~/photos P8060697.JPG P7250454.MOV
      {prog} get -d ~/photos "*.jpg"
      {prog} sync ~/photos
    '''

    parser = optparse.OptionParser(add_help_option=False, option_class=Option, version=__version__)
    opt = parser.add_option

    opt('-h', '--help', action='store_true')
    opt('-v', action='version')

    opt('-a', '--addr', default='192.168.0.10')
    opt('-p', '--port', default=80, type='int')
    opt('-b', '--baseurl', default='/DCIM/100OLYMP')
    opt('-t', '--timeout', default=60, type='int')

    opt('-r', '--parsable', action='store_true')
    opt('-d', '--destdir', default='./')

    opt('-o', '--older', type='timespec')
    opt('-n', '--newer', type='timespec')
    opt('--on', type='timespec')

    opts, args = parser.parse_args(argv)

    if not args or opts.help:
        usage = textwrap.dedent(usage).strip().format(prog=parser.get_prog_name())
        print(usage, file=sys.stderr)
        sys.exit(0)

    if opts.on:
        # TODO: Works only for days.
        opts.newer = opts.on.replace(hour=0, minute=0, second=0, microsecond=0)
        opts.older = opts.on.replace(hour=23, minute=59, second=59, microsecond=59999)

    if args[0] == 'sync':
        if not args[1:]:
            print('error: sync command requires destination directory', file=sys.stderr)
            sys.exit(2)
        opts.destdir = args[1]

    if args[0] not in ('get', 'list', 'sync'):
        print('error: unknown command: %s' % args[0], file=sys.stderr)
        sys.exit(2)

    if args[0] == 'get' and not args[1:]:
        print('error: no files specified', file=sys.stderr)
        sys.exit(2)

    opts.destdir = Path(opts.destdir)

    return opts, args[0], args


def check_timespec_option(option, opt, value):
    try:
        return utils.parse_timespec(value)
    except ValueError:
        msg = 'option %s: unable to parse timespec %r' % (opt, value)
        raise optparse.OptionValueError(msg)

# Add a 'timespec' option type.
class Option(optparse.Option):
    TYPES = optparse.Option.TYPES + ('timespec',)
    TYPE_CHECKER = optparse.Option.TYPE_CHECKER.copy()
    TYPE_CHECKER['timespec'] = check_timespec_option


#-----------------------------------------------------------------------------
# Commands
#-----------------------------------------------------------------------------

def cmd_list(entries, parsable):
    '''List all media files on camera.'''
    fmt = '{} {} {} ' if parsable else '{}   {:<9}  {}'
    for entry in entries:
        size = entry.size if parsable else utils.sizefmt(entry.size)
        time = int(entry.timestamp.timestamp()) if parsable else entry.timestamp.isoformat()
        print(fmt.format(entry.name, size, time))


def cmd_get(conn, entries, names, destdir, parsable):
    '''Download one or more file from camera.'''
    entries_to_download = names_to_entries(names, entries)
    download_helper(conn, entries_to_download, destdir, parsable)


def cmd_sync(conn, entries, destdir, parsable):
    '''Pull missing files from camera.'''
    entries_to_download = []
    for entry in entries:
        dest = destdir / entry.name
        if not dest.exists() or dest.stat().st_size != entry.size:
            entries_to_download.append(entry)

    download_helper(conn, entries_to_download, destdir, parsable)


#-----------------------------------------------------------------------------
# Utility functions
#-----------------------------------------------------------------------------

def names_to_entries(names, entries):
    '''Find all entries that match a given name or pattern.'''
    name_to_entry = {entry.name: entry for entry in entries}
    matched_names = []

    for name in names:
        matched = fnmatch.filter(name_to_entry, name)
        if matched:
            matched_names += matched
        else:
            raise SystemExit('error: pattern or name "%s" does not match any files' % name)

    matched_names = utils.remove_duplicates(matched_names)
    return [name_to_entry[name] for name in matched_names]


def download_helper(conn, entries, destdir, parsable):
    '''Download entries.'''
    def with_progress(fh, entry, num_entries, num_entry):
        with tqdm(desc=fh.name, total=entry.size, unit='B', unit_scale=True, unit_divisor=1024) as pbar:
            pbar.set_postfix(remaining=num_entries - num_entry)
            for data in oishare.download(conn, entry):
                pbar.update(len(data))
                fh.write(data)

    def without_progress(fh, entry, num_entries, num_entry):
        for data in oishare.download(conn, entry):
            fh.write(data)
        print(fh.name)

    destdir.mkdir(parents=True, exist_ok=True)
    download_func = without_progress if parsable else with_progress

    num_entries = len(entries)
    for n, entry in enumerate(entries, 1):
        dest = destdir / entry.name
        with dest.open('wb') as fh:
            download_func(fh, entry, num_entries, n)


#-----------------------------------------------------------------------------

def main(argv=sys.argv[1:]):
    opts, cmd, args = parseopts(argv)
    conn = HTTPConnection(opts.addr, opts.port, opts.timeout)

    entries = oishare.find_entries(conn, opts.baseurl)
    if opts.newer or opts.older:
        entries = oishare.filter_by_date(entries, opts.newer, opts.older)

    try:
        if cmd == 'list':
            cmd_list(entries, opts.parsable)
        elif cmd == 'get':
            cmd_get(conn, entries, args[1:], opts.destdir, opts.parsable)
        elif cmd == 'sync':
            cmd_sync(conn, entries, opts.destdir, opts.parsable)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
