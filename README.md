# Olympus Photosync

[![Latest version released on PyPi](https://img.shields.io/pypi/v/olympus-photosync.svg?style=flat-square&label=latest%20stable%20version)](https://pypi.python.org/pypi/olympus-photosync)
[![BSD 3-Clause](https://img.shields.io/pypi/l/olympus-photosync.svg?style=flat-square&label=license)](https://pypi.python.org/pypi/olympus-photosync)

List, download and sync photos and videos from WiFi enabled Olympus cameras.

[![Asciinema terminal recording](https://asciinema.org/a/i1og9KbzvspJsKpO3aOzFhZfA.png)](https://asciinema.org/a/i1og9KbzvspJsKpO3aOzFhZfA?theme=monokai&size=medium&autoplay=1&speed=1.2)

All functionality has been verified to work with the following digital cameras:

- Olympus E-M10

However, cameras that use the same media sharing mechanism should work just
as well. With that mentioned, the list of cameras that *probably* work is:

- Olympus E-M1
- Olympus E-M5
- Olympus TG-860
- Olympus TG-5

## Installation

The latest stable version of olympus-photosync can be installed from pypi:

```bash
$ pip install olympus-photosync
```

## Usage

```
Usage: olympus-photosync [options] <get|list|sync> ...

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
  -n, --dryrun            show files that will be synced and exit
  destdir                 directory which to download media files

Filter options:
  --older timefmt|name    select files older than timestamp or filename
  --newer timefmt|name    select files newer than timestamp or filename
  --on timefmt            select media from a specific day

Examples:
  olympus-photosync list --newer 2017-09-17T16:21:00 --older 2017-09-20
  olympus-photosync list --newer 10d --older 12h
  olympus-photosync list --newer PA290930.JPG --older PB070950.JPG
  olympus-photosync list --on today
  olympus-photosync get -d ~/photos P8060697.JPG P7250454.MOV
  olympus-photosync get -d ~/photos "*.jpg"
  olympus-photosync sync ~/photos
```

A cross-platform GUI is provided by the `olympus-photosync-gui` program. At
the moment it can be used to list and download files from supported devices.

![GUI screenshot](docs/images/gui-screenshot.png)

## Todo

- Test on more cameras.
- Test on Windows.
- The GUI needs more work (e.g. add thumbnails, improve usability).
- Provide a standalone binary for Windows using PyInstaller.

## Alternatives

- [olympus-photosync](https://github.com/mauriciojost/olympus-photosync): A well-tested command-line application written in Scala.

## License

Released under the terms of the [Revised BSD License](https://raw.github.com/gvalkov/olympus-photosync/master/LICENSE).
