from pathlib import Path

from wintap_perf_collection.procfs import parse_smaps_rollup, parse_status, summarize_maps


def test_parse_smaps_rollup() -> None:
    text = """
Rss:                1234 kB
Pss:                 456 kB
Private_Clean:        11 kB
Private_Dirty:        22 kB
RssAnon:             333 kB
RssFile:             444 kB
Swap:                  0 kB
""".strip()
    parsed = parse_smaps_rollup(text)
    assert parsed["Rss"] == 1234
    assert parsed["Pss"] == 456
    assert parsed["RssAnon"] == 333
    assert parsed["RssFile"] == 444


def test_parse_smaps_rollup_ignores_rollup_header_line() -> None:
    text = """
55eeec363000-7ffd5b538000 ---p 00000000 00:00 0                              [rollup]
Rss:                1234 kB
Anonymous:           333 kB
""".strip()
    parsed = parse_smaps_rollup(text)
    assert parsed == {"Rss": 1234, "Anonymous": 333}


def test_parse_status() -> None:
    text = """
Name:\tLintap
State:\tS (sleeping)
Tgid:\t123
Pid:\t123
PPid:\t1
Threads:\t17
FDSize:\t64
VmRSS:\t2048 kB
RssAnon:\t1024 kB
RssFile:\t512 kB
VmSwap:\t0 kB
voluntary_ctxt_switches:\t88
nonvoluntary_ctxt_switches:\t5
""".strip()
    parsed = parse_status(text)
    assert parsed["Name"] == "Lintap"
    assert parsed["Pid"] == 123
    assert parsed["VmRSS"] == 2048
    assert parsed["voluntary_ctxt_switches"] == 88


def test_summarize_maps() -> None:
    text = """
00400000-00452000 r-xp 00000000 08:02 12345 /usr/bin/foo
00652000-00653000 rw-p 00052000 08:02 12345 /usr/bin/foo
7f0000000000-7f0000200000 rw-p 00000000 00:00 0
""".strip()
    parsed = summarize_maps(text)
    assert parsed["mapped_regions"] == 3
    assert parsed["executable_regions"] == 1
    assert parsed["writable_private_regions"] == 2
    assert parsed["mapped_bytes_total"] > 0
