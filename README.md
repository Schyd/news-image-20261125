# Wednesday 25 November 2026 in one picture

[![news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/Schyd/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/Schyd/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125)

35 stories from Wednesday 25 November 2026, all dated, each marked how sure
we are (CONFIRMED means 2+ outlets). 4 leads, 8 pictured, 23 brief.
9 regions, a UTC timeline, a numbered world map, a two-way DATE CHECK box,
and a big-number strip.

## How it works

`main.py` (Python 3.13, standard library only) draws the whole newspaper
with its own PNG encoder and its own 5x7 bitmap font — no network, no
external assets. Run it and it writes `entry.png` (1024x1024) to
`$MAKEFUN_OUTPUT_DIR` (default `/output`):

```
python3 main.py
```

Two runs produce byte-identical output.

## Verification

- Two runs of `main.py` produce byte-identical `entry.png`
  (sha256 `11d863d5b1c820229a3cbbbef9ee9bf08aa6d1d0159c9faa9d7e25b8e3a2aa80`,
  31,185 bytes, 1024x1024, under the 1 MiB cap).
- Readability at 300 px wide: the date "WEDNESDAY 25 NOVEMBER 2026" is
  the largest element and stays legible; the lead headlines and the overall
  composition (4 leads, pictured grid, map, briefs) still read.
- Every story is dated 25 November 2026, carries its source, and carries a
  CONFIRMED / OFFICIAL / CLAIM / FORECAST tag. CONFIRMED means 2+ outlets.
  Full ranking and sources: see NOTES.md.
- No network, no external assets, no forbidden files.

## The day in brief

1. 720,000 Russian war dead (leaked records, RFE/RL)
2. Ukraine hits Russian ships in the Gulf of Finland and off Libya
3. Trump: Iran war effort "funded" through January
4. Huawei convicted in a Brooklyn jury trial (10 of 12 counts)

Plus 31 more stories from all 9 regions — Riyadh tower hit again, US
inflation and GDP due, Baghdad seizes Kurdish oil, the oldest quasar ever
seen, Real Madrid 5-1 PSV, and more. Every story carries its date, its
source, and a CONFIRMED / OFFICIAL / CLAIM / FORECAST tag.
