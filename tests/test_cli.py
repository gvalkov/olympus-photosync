from datetime import datetime
from pathlib import Path

from olympusphotosync import cli
from olympusphotosync.oishare import Entry


def test_parseopts_on_today():
    opts, cmd, args = cli.parseopts(["--on", "today", "list"])
    assert cmd == "list"
    assert args == ["list"]
    assert (opts.newer[0].hour, opts.newer[0].minute, opts.newer[0].second) == (0, 0, 0)
    assert (opts.older[0].hour, opts.older[0].minute, opts.older[0].second) == (23, 59, 59)
    assert opts.older[0].microsecond == 999999
    assert opts.newer[1] == opts.older[1] == "timestamp"


def test_download_replaces_partial_file(tmp_path):
    entries = [Entry(root="", name="P1.JPG", size=4, timestamp=datetime(2020, 1, 1))]

    def download_func(conn, fh, entry, total, num, dest):
        assert Path(fh.name).name == "P1.JPG.part"
        assert not Path(dest).exists()
        fh.write(b"data")

    cli.download_helper(None, entries, tmp_path, download_func)

    assert (tmp_path / "P1.JPG").read_bytes() == b"data"
    assert list(tmp_path.glob("*.part")) == []
