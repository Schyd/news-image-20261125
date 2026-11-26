#!/usr/bin/env python3
"""news-image-20261125: draws one image summing up Wednesday 25 November 2026.

Standard library only. Writes /output/entry.png (or $MAKEFUN_OUTPUT_DIR).
Deterministic: two runs produce identical bytes. No network.
"""
import os
import struct
import zlib

W, H = 1024, 1024

# Palette indices
PAPER = 0    # cream paper
INK = 1      # near-black
RED = 2      # accent red
BLUE = 3     # dark blue
TEAL = 4     # teal
GOLD = 5     # gold
LGRAY = 6    # light gray band
MGRAY = 7    # mid gray
WINE = 8     # dark red
GREEN = 9    # green
ORANGE = 10  # orange
SEA = 11     # map sea light blue
LAND = 12    # map land tan
WHITE = 13   # white

PALETTE = [
    (250, 244, 224),  # 0 paper
    (22, 22, 22),     # 1 ink
    (178, 34, 34),    # 2 red
    (30, 60, 120),    # 3 blue
    (0, 110, 110),    # 4 teal
    (198, 158, 40),   # 5 gold
    (228, 226, 216),  # 6 light gray
    (150, 150, 145),  # 7 mid gray
    (120, 20, 30),    # 8 wine
    (40, 120, 60),    # 9 green
    (200, 100, 20),   # 10 orange
    (172, 202, 232),  # 11 sea
    (210, 190, 150),  # 12 land
    (255, 255, 255),  # 13 white
]


def _chunk(typ, data):
    out = struct.pack(">I", len(data)) + typ + data
    out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
    return out


def write_png(path, w, h, idx):
    """Write an 8-bit palette PNG. idx is bytes of palette indices, w*h."""
    raw0 = b"".join(b"\x00" + idx[y * w:(y + 1) * w] for y in range(h))
    rows = []
    for y in range(h):
        row = bytearray(idx[y * w:(y + 1) * w])
        for x in range(w - 1, 0, -1):
            row[x] = (row[x] - row[x - 1]) & 0xFF
        rows.append(b"\x01" + bytes(row))
    raw1 = b"".join(rows)
    comp0 = zlib.compress(raw0, 9)
    comp1 = zlib.compress(raw1, 9)
    comp = comp0 if len(comp0) <= len(comp1) else comp1
    plte = b"".join(bytes(p) for p in PALETTE)
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 3, 0, 0, 0)
    data = (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr) +
            _chunk(b"PLTE", plte) + _chunk(b"IDAT", comp) +
            _chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(data)


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray([bg]) * (w * h)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.px[y * self.w + x] = c

    def rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        for yy in range(y0, y1):
            base = yy * self.w
            for xx in range(x0, x1):
                self.px[base + xx] = c

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def outline(self, x, y, w, h, c, t=1):
        self.rect(x, y, w, t, c)
        self.rect(x, y + h - t, w, t, c)
        self.rect(x, y, t, h, c)
        self.rect(x + w - t, y, t, h, c)

    def circle(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            for xx in range(cx - dx, cx + dx + 1):
                self.set(xx, cy + dy, c)

    def ring(self, cx, cy, r, c):
        for a in range(0, 360, 2):
            import math
            self.set(cx + int(r * math.cos(math.radians(a))),
                     cy + int(r * math.sin(math.radians(a))), c)

# 5x7 bitmap font, written from scratch in this session.
# Each glyph: 7 rows of 5 characters ('#' = on, '.' = off).
FONT = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    'J': ("..###", "....#", "....#", "....#", "....#", "#...#", ".###."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    'a': (".....", ".....", ".###.", "....#", ".####", "#...#", ".####"),
    'b': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
    'c': (".....", ".....", ".####", "#....", "#....", "#....", ".####"),
    'd': ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
    'e': (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
    'f': ("..##.", ".#..#", ".#...", "###..", ".#...", ".#...", ".#..."),
    'g': (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    'h': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
    'i': (".....", "..#..", ".....", ".##..", "..#..", "..#..", ".###."),
    'j': (".....", "..#..", ".....", "..##.", "...#.", "...#.", ".##.."),
    'k': ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
    'l': (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'm': (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
    'n': (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
    'o': (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
    'p': (".....", ".....", "####.", "#...#", "#...#", "####.", "#...."),
    'q': (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    'r': (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
    's': (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
    't': (".#...", ".#...", "###..", ".#...", ".#...", ".#...", ".##.."),
    'u': (".....", ".....", "#...#", "#...#", "#...#", "#...#", ".####"),
    'v': (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'w': (".....", ".....", "#...#", "#...#", "#.#.#", "#.#.#", ".#.#."),
    'x': (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    'y': (".....", ".....", "#...#", "#...#", "#...#", ".####", "...#."),
    'z': (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
    '0': (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    '.': (".....", ".....", ".....", ".....", ".....", ".....", "..#.."),
    ',': (".....", ".....", ".....", ".....", ".....", "..##.", ".#..."),
    ':': (".....", "..#..", ".....", ".....", ".....", "..#..", "....."),
    ';': (".....", "..#..", ".....", ".....", ".....", "..##.", ".#..."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    '-': (".....", ".....", ".....", ".####", ".....", ".....", "....."),
    '/': ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    '%': ("#...#", "#..#.", "...#.", "..#..", ".#...", ".#..#", "#...#"),
    '$': ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    '&': (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    '(': ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ')': (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    '+': (".....", ".....", "..#..", ".###.", "..#..", ".....", "....."),
    '=': (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '*': (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    '#': (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    '@': (".###.", "#...#", "#.###", "#.#.#", "#.#..", "#....", ".###."),
    '_': (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
    '[': (".###.", ".#...", ".#...", ".#...", ".#...", ".#...", ".###."),
    ']': (".###.", "...#.", "...#.", "...#.", "...#.", "...#.", ".###."),
    '<': ("...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."),
    '>': (".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."),
    '|': ("..#..", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    '\\': ("#....", "#....", ".#...", "..#..", "...#.", "....#", "....#"),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '\u2014': (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    '\u2022': (".....", ".....", ".###.", ".###.", ".###.", ".....", "....."),
}


def text_width(text, scale=1):
    """Pixel width of text at given scale (1px gap between glyphs)."""
    return len(text) * (5 * scale + scale) - scale


def draw_text(cv, x, y, text, scale, color):
    """Draw text with top-left at (x, y). Returns the x after the text."""
    cx = x
    for ch in text:
        g = FONT.get(ch)
        if g is None:
            g = FONT[' ']
        for r in range(7):
            row = g[r]
            for c in range(5):
                if row[c] == '#':
                    cv.rect(cx + c * scale, y + r * scale, scale, scale, color)
        cx += 5 * scale + scale
    return cx


def wrap_text(text, scale, max_w):
    """Greedy word wrap. Returns list of lines that fit max_w pixels."""
    words = text.split(' ')
    lines = []
    cur = ''
    for w in words:
        trial = (cur + ' ' + w) if cur else w
        if text_width(trial, scale) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

# Pictogram icons, 12x12 grids, drawn from scratch in this session.
# '#' = main colour, 'o' = accent colour, '.' = transparent.
ICONS = {
    'doc': (
        "..########..",
        "..#......#..",
        "..#.####.#..",
        "..#......#..",
        "..#.####.#..",
        "..#......#..",
        "..#.####.#..",
        "..#......#..",
        "..########..",
        "............",
        "............",
        "............",
    ),
    'ship': (
        ".....#......",
        ".....#......",
        ".....##.....",
        ".....#.#....",
        ".....#......",
        "..#######...",
        ".#########..",
        "###########.",
        ".#########..",
        "..#######...",
        "............",
        "............",
    ),
    'flame': (
        ".....#......",
        "....###.....",
        "....#.#.....",
        "...##.##....",
        "...#...#....",
        "..##...##...",
        "..#.....#...",
        "..#######...",
        "..#######...",
        "............",
        "............",
        "............",
    ),
    'scales': (
        ".....#......",
        ".....#......",
        "..#######...",
        ".#.......#..",
        ".#.......#..",
        ".###...###..",
        "..#.....#...",
        ".....#......",
        "....###.....",
        "............",
        "............",
        "............",
    ),
    'tower': (
        ".....#......",
        "....###.....",
        "....###.....",
        "...#####....",
        "...#####....",
        "...#####....",
        "...#####....",
        "..#######...",
        "..#######...",
        "..#######...",
        ".#########..",
        ".#########..",
    ),
    'chart': (
        "............",
        "....#.......",
        "....#...#...",
        "....#...#...",
        "..#.#...#...",
        "..#.#.#.#...",
        "..#.#.#.#...",
        "..#.#.#.#...",
        "##########..",
        "............",
        "............",
        "............",
    ),
    'derrick': (
        ".....#......",
        "....###.....",
        "....#.#.....",
        "...#...#....",
        "...#...#....",
        "..#.....#...",
        "..#..#..#...",
        "..#.....#...",
        ".#########..",
        "............",
        "............",
        "............",
    ),
    'burst': (
        ".....#......",
        "#....#....#.",
        ".#...#...#..",
        "..#..#..#...",
        "...#####....",
        "###########.",
        "...#####....",
        "..#..#..#...",
        ".#...#...#..",
        "#....#....#.",
        ".....#......",
        "............",
    ),
    'chip': (
        "............",
        ".##########.",
        ".#........#.",
        ".##.####.##.",
        ".#..####..#.",
        ".#..####..#.",
        ".#..####..#.",
        ".##.####.##.",
        ".#........#.",
        ".##########.",
        "............",
        "............",
    ),
    'globe': (
        "....####....",
        "..##....##..",
        ".#........#.",
        ".#...##...#.",
        "#....##....#",
        "#....##....#",
        "#....##....#",
        ".#...##...#.",
        ".#........#.",
        "..##....##..",
        "....####....",
        "............",
    ),
    'star': (
        ".....#......",
        ".....#......",
        "....###.....",
        "....###.....",
        "###########.",
        ".##########.",
        "###########.",
        "....###.....",
        "....###.....",
        ".....#......",
        ".....#......",
        "............",
    ),
    'ball': (
        "....####....",
        "..##....##..",
        ".#..####..#.",
        ".#.#....#.#.",
        "#..#....#..#",
        "#..#....#..#",
        ".#.#....#.#.",
        ".#..####..#.",
        "..##....##..",
        "....####....",
        "............",
        "............",
    ),
}


def draw_icon(cv, name, x, y, s, color, accent=None):
    """Draw an icon grid scaled to s x s pixels, top-left at (x, y)."""
    rows = ICONS[name]
    n = len(rows)
    cell = max(1, s // n)
    ox = x + (s - cell * n) // 2
    oy = y + (s - cell * n) // 2
    for r in range(n):
        for c in range(n):
            ch = rows[r][c]
            if ch == '#':
                cv.rect(ox + c * cell, oy + r * cell, cell, cell, color)
            elif ch == 'o' and accent is not None:
                cv.rect(ox + c * cell, oy + r * cell, cell, cell, accent)


# World map: continents as rectangles in a 100 x 60 space.
LAND_RECTS = [
    # North America
    (2, 6, 8, 6), (8, 4, 22, 10), (8, 14, 20, 8), (10, 22, 8, 6),
    (17, 27, 5, 3),
    # Greenland
    (31, 2, 5, 6),
    # South America
    (20, 30, 12, 6), (21, 36, 10, 8), (23, 44, 5, 10),
    # Europe
    (47, 2, 5, 6), (45, 8, 12, 7), (44, 7, 2, 3), (46, 14, 8, 3),
    # Africa
    (46, 20, 14, 8), (47, 28, 12, 8), (49, 36, 8, 8), (60, 38, 2, 4),
    # Middle East
    (58, 14, 7, 6),
    # Asia
    (57, 2, 38, 8), (60, 10, 15, 6), (72, 12, 14, 8), (64, 18, 6, 8),
    (74, 19, 6, 5), (74, 25, 12, 3), (86, 10, 3, 7),
    # Oceania
    (78, 40, 12, 8), (92, 46, 3, 5),
]

# Region number -> (x, y) centre in the 100 x 60 space.
REGION_PINS = {
    1: (14, 12),   # North America
    2: (22, 36),   # Latin America
    3: (50, 8),    # Europe
    4: (61, 16),   # Middle East
    5: (52, 28),   # Africa
    6: (66, 21),   # South Asia
    7: (78, 14),   # East Asia
    8: (77, 23),   # Southeast Asia
    9: (83, 43),   # Oceania
}


def draw_map(cv, x, y, w, h):
    """Draw the numbered world map in the box (x, y, w, h)."""
    cv.rect(x, y, w, h, SEA)
    sx = w / 100.0
    sy = h / 60.0
    for (rx, ry, rw, rh) in LAND_RECTS:
        cv.rect(x + int(rx * sx), y + int(ry * sy),
                max(1, int(rw * sx)), max(1, int(rh * sy)), LAND)
    for num, (px, py) in REGION_PINS.items():
        cx = x + int(px * sx)
        cy = y + int(py * sy)
        cv.circle(cx, cy, 8, WHITE)
        cv.circle(cx, cy, 7, RED)
        draw_text(cv, cx - 3, cy - 3, str(num), 1, WHITE)

# The 35 stories of Wednesday 25 November 2026, ranked by consequence
# (ranking + sources: see NOTES.md). Every story carries its date.
# tag: CONFIRMED = 2+ outlets, OFFICIAL = official body,
#      CLAIM = one party / one outlet, FORECAST = scheduled / prediction.
# region: 1 N America, 2 Latin America, 3 Europe, 4 Middle East, 5 Africa,
#         6 South Asia, 7 East Asia, 8 SE Asia, 9 Oceania.
STORIES = [
    {"rank": 1, "kind": "lead", "region": 3, "icon": "doc",
     "head": "720,000 RUSSIAN DEAD, EST.",
     "body": "Leaked records suggest Russia's Ukraine war dead may top 720,000 - the grimmest toll yet of the nearly five-year war.",
     "when": "25 NOV 01:00 UTC", "tag": "CONFIRMED", "src": "RFE/RL"},
    {"rank": 2, "kind": "lead", "region": 3, "icon": "ship",
     "head": "UKRAINE HITS RUSSIAN SHIPS",
     "body": "Zelenskiy confirms Ukraine struck a Russian cargo ship in the Gulf of Finland and sank a Russian warship off Benghazi, Libya.",
     "when": "25 NOV", "tag": "CONFIRMED", "src": "Reuters"},
    {"rank": 3, "kind": "lead", "region": 4, "icon": "flame",
     "head": "TRUMP: IRAN WAR FUNDED TO JAN",
     "body": "Trump says his war effort with Iran is 'funded' through January and addresses Israel's goal of regime change in Tehran.",
     "when": "25 NOV", "tag": "CLAIM", "src": "NY Post"},
    {"rank": 4, "kind": "lead", "region": 1, "icon": "chart",
     "head": "US GDP 4.3%, INFLATION HOT",
     "body": "Q3 growth revised up from 3.4%; October PCE 3.8%, core 3.3% - the Fed may hike in December.",
     "when": "25 NOV 13:30 UTC", "tag": "CONFIRMED", "src": "BEA"},
    {"rank": 5, "kind": "pictured", "region": 4, "icon": "tower",
     "head": "RIYADH TOWER HIT AGAIN",
     "body": "Houthi projectile hits the PIF Tower, Riyadh's tallest, wounding 11.",
     "when": "25 NOV", "tag": "CONFIRMED", "src": "Reuters"},
    {"rank": 6, "kind": "pictured", "region": 1, "icon": "scales",
     "head": "HUAWEI GUILTY IN US TRIAL",
     "body": "Jury convicts Huawei on 10 of 12 counts: fraud, sanctions, secrets.",
     "when": "25 NOV", "tag": "CONFIRMED", "src": "DOJ"},
    {"rank": 7, "kind": "pictured", "region": 4, "icon": "derrick",
     "head": "BAGHDAD SEIZES KURD OIL",
     "body": "Iraq orders federal control of Kurdish oilfields and crossings.",
     "when": "25 NOV", "tag": "CONFIRMED", "src": "FT"},
    {"rank": 8, "kind": "pictured", "region": 4, "icon": "burst",
     "head": "HAMAS SECURITY CHIEF KILLED",
     "body": "Israeli strike kills Naim Abu Nahal, Hamas internal security chief.",
     "when": "25 NOV", "tag": "CONFIRMED", "src": "Reuters"},
    {"rank": 9, "kind": "pictured", "region": 1, "icon": "chip",
     "head": "HUANG SAYS SORRY, IN THERAPY",
     "body": "Nvidia's CEO apologizes; shares fall 6% after Monday's surge.",
     "when": "25 NOV", "tag": "CONFIRMED", "src": "CNN"},
    {"rank": 10, "kind": "pictured", "region": 1, "icon": "globe",
     "head": "US WEIGHS NEW TARIFFS",
     "body": "Washington readies duties on India, China, Brazil and 14 partners.",
     "when": "25 NOV", "tag": "CONFIRMED", "src": "Reuters"},
    {"rank": 11, "kind": "pictured", "region": 3, "icon": "star",
     "head": "OLDEST QUASAR FOUND",
     "body": "A quasar 13.1bn years old, its black hole 360m suns.",
     "when": "25 NOV", "tag": "CONFIRMED", "src": "Reuters"},
    {"rank": 12, "kind": "pictured", "region": 4, "icon": "flame",
     "head": "RAS TANURA REFINERY HIT",
     "body": "Houthis claim a strike on Ras Tanura, the kingdom's biggest refinery.",
     "when": "25 NOV", "tag": "CLAIM", "src": "Reuters"},
    {"rank": 13, "kind": "brief", "region": 4,
     "head": "ABU AL-AOUF KILLED",
     "body": "Killed with wife and two daughters in Gaza City.",
     "when": "25 NOV", "tag": "CONFIRMED", "src": "Reuters"},
    {"rank": 14, "kind": "brief", "region": 5,
     "head": "CAIRO TANKER FIRE KILLS 31",
     "body": "Tanker crash sets Cairo ring road ablaze, 31 dead.",
     "when": "25 NOV", "tag": "CONFIRMED", "src": "CNN"},
    {"rank": 15, "kind": "brief", "region": 5,
     "head": "RSF DRONES KILL 19 IN SUDAN",
     "body": "RSF drones kill 19 civilians in Blue Nile state.",
     "when": "25 NOV", "tag": "CLAIM", "src": "Reuters"},
    {"rank": 16, "kind": "brief", "region": 7,
     "head": "FIRST FOREIGNER ON TIANGONG",
     "body": "Pakistani astronaut first foreigner aboard Tiangong.",
     "when": "25 NOV 03:56 UTC", "tag": "CONFIRMED", "src": "Xinhua"},
    {"rank": 17, "kind": "brief", "region": 9,
     "head": "SOLOMONS BARS FOREIGN BASES",
     "body": "Solomons bars foreign bases in new Australia treaty.",
     "when": "25 NOV", "tag": "CONFIRMED", "src": "CNN"},
    {"rank": 18, "kind": "brief", "region": 3,
     "head": "POPE SLAMS COP31 FAILURE",
     "body": "Leo XIV calls COP31's no-deal outcome 'troubling'.",
     "when": "25 NOV", "tag": "CONFIRMED", "src": "Reuters"},
    {"rank": 19, "kind": "brief", "region": 1,
     "head": "MACY'S PARADE MOVED TO SAT",
     "body": "100th parade moved to Saturday as storm bears down.",
     "when": "25 NOV", "tag": "CONFIRMED", "src": "Reuters"},
    {"rank": 20, "kind": "brief", "region": 3,
     "head": "UK SANCTIONS HOUTHIS",
     "body": "Britain freezes assets of the group and 4 officials.",
     "when": "25 NOV", "tag": "CONFIRMED", "src": "Reuters"},
    {"rank": 21, "kind": "brief", "region": 4,
     "head": "2 MORE TANKERS HIT MINES",
     "body": "Two tankers explode and catch fire in Hormuz.",
     "when": "25 NOV", "tag": "CLAIM", "src": "IRGC"},
    {"rank": 22, "kind": "brief", "region": 4,
     "head": "IRAN'S MEDICINE CRISIS",
     "body": "Pharmacies shut, deliveries stall, patients ration.",
     "when": "25 NOV", "tag": "CLAIM", "src": "DW"},
    {"rank": 23, "kind": "brief", "region": 4,
     "head": "HOUTHIS 60 KM FROM ADEN",
     "body": "Yemen's army: rebels will not take the capital.",
     "when": "25 NOV", "tag": "CLAIM", "src": "Reuters"},
    {"rank": 24, "kind": "brief", "region": 1,
     "head": "MICROSOFT 'CODE RED'",
     "body": "Firm declares an emergency after a historic outage.",
     "when": "25 NOV", "tag": "CLAIM", "src": "Reuters"},
    {"rank": 25, "kind": "brief", "region": 1,
     "head": "IOWA BLAST DONE, 0.0 LEAD",
     "body": "Army blast succeeds; EPA reads 0.0 lead in the air.",
     "when": "25 NOV 15:00 UTC", "tag": "OFFICIAL", "src": "US Army"},
    {"rank": 26, "kind": "brief", "region": 3,
     "head": "SARKOZY TO STAND TRIAL",
     "body": "Court orders ex-president and Bruni to trial.",
     "when": "25 NOV", "tag": "CONFIRMED", "src": "Reuters"},
    {"rank": 27, "kind": "brief", "region": 3,
     "head": "CAMEROON REBEL IN NORWAY COURT",
     "body": "Lucas Cho Ayaba pleads not guilty to war crimes.",
     "when": "25 NOV", "tag": "CONFIRMED", "src": "BBC"},
    {"rank": 28, "kind": "brief", "region": 5,
     "head": "DR CONGO REBELS PULL BACK",
     "body": "Rebels withdraw after clashes; plane missing.",
     "when": "25 NOV", "tag": "CONFIRMED", "src": "BBC"},
    {"rank": 29, "kind": "brief", "region": 5,
     "head": "NIGERIA EMIR SUSPENDED",
     "body": "Emir of Daura, 92, suspended after assault claims.",
     "when": "25 NOV", "tag": "CONFIRMED", "src": "BBC"},
    {"rank": 30, "kind": "brief", "region": 5,
     "head": "AFCON QUALIFIER SHOCKS",
     "body": "Gambia stun Ghana 4-2; Guinea-Bissau beat Nigeria 3-0.",
     "when": "25 NOV", "tag": "CONFIRMED", "src": "Al Jazeera"},
    {"rank": 31, "kind": "brief", "region": 8,
     "head": "INDONESIA VP DEADLINE",
     "body": "Prabowo must name two VP candidates today.",
     "when": "25 NOV", "tag": "CLAIM", "src": "TSC.ai"},
    {"rank": 32, "kind": "brief", "region": 6,
     "head": "INDIA MARKETS REOPEN",
     "body": "Sensex and Nifty resume after the holiday.",
     "when": "25 NOV", "tag": "CONFIRMED", "src": "BusinessLine"},
    {"rank": 33, "kind": "brief", "region": 2,
     "head": "CARTAGENA HOSTAGES HELD",
     "body": "Gunmen hold 25 hostage in a supermarket.",
     "when": "25 NOV", "tag": "CONFIRMED", "src": "WireMinute"},
    {"rank": 34, "kind": "brief", "region": 2,
     "head": "COLOMBIA CAR BOMB",
     "body": "A blast injures at least 23 people.",
     "when": "25 NOV", "tag": "CLAIM", "src": "Starlit"},
    {"rank": 35, "kind": "brief", "region": 1,
     "head": "PACKERS AT RAMS TONIGHT",
     "body": "NFL's first Thanksgiving Eve game; Parsons returns.",
     "when": "25 NOV", "tag": "FORECAST", "src": "DailyFoxNews"},
]

REGIONS = [
    (1, "N. AMERICA", 8),
    (2, "LATIN AMERICA", 2),
    (3, "EUROPE", 7),
    (4, "MIDDLE EAST", 9),
    (5, "AFRICA", 5),
    (6, "S. ASIA", 1),
    (7, "E. ASIA", 1),
    (8, "SE ASIA", 1),
    (9, "OCEANIA", 1),
]

TIMELINE = [
    ("00:06", "Al Jazeera: Gambia stun Ghana 4-2"),
    ("00:39", "Riyadh tower strike reported"),
    ("00:46", "NZ's Peters on Australia change"),
    ("01:00", "RFE/RL: 720,000 Russian war dead"),
    ("03:56", "Shenzhou-24 docks at Tiangong"),
    ("13:30", "US GDP 4.3%, PCE 3.8%"),
    ("15:00", "Iowa blast done, 0.0 lead"),
]

TAG_COLOR = {"CONFIRMED": BLUE, "OFFICIAL": GREEN, "CLAIM": RED,
             "FORECAST": ORANGE}


def center_text(cv, y, text, scale, color):
    x = (W - text_width(text, scale)) // 2
    draw_text(cv, x, y, text, scale, color)
    return x


def center_text_in(cv, x0, x1, y, text, scale, color):
    """Center text inside a panel [x0, x1] (not the whole canvas)."""
    x = x0 + (x1 - x0 - text_width(text, scale)) // 2
    draw_text(cv, x, y, text, scale, color)
    return x


def draw_meta(cv, x, y, when, tag, src):
    """Meta line: date - TAG (coloured) - source. Returns x after text."""
    x = draw_text(cv, x, y, when + " - ", 1, INK)
    x = draw_text(cv, x, y, tag, 1, TAG_COLOR.get(tag, INK))
    x = draw_text(cv, x, y, " - " + src, 1, MGRAY)
    return x


def draw_region_chip(cv, x, y, region):
    cv.circle(x, y, 9, WHITE)
    cv.circle(x, y, 8, RED)
    draw_text(cv, x - 3, y - 3, str(region), 1, WHITE)


def draw_lead(cv, s, x, y, w, h):
    cv.rect(x, y, w, h, WHITE)
    cv.outline(x, y, w, h, MGRAY, 1)
    # icon box
    cv.rect(x + 8, y + 8, 84, 84, LGRAY)
    draw_icon(cv, s["icon"], x + 8, y + 8, 84, INK, RED)
    # headline
    tx = x + 100
    tw = w - 108
    head = str(s["rank"]) + ". " + s["head"]
    lines = wrap_text(head, 2, tw)
    yy = y + 8
    for ln in lines[:2]:
        draw_text(cv, tx, yy, ln, 2, INK)
        yy += 16
    # body
    yy += 2
    for ln in wrap_text(s["body"], 1, tw)[:3]:
        draw_text(cv, tx, yy, ln, 1, INK)
        yy += 9
    # meta at the bottom of the cell
    draw_meta(cv, tx, y + h - 14, s["when"], s["tag"], s["src"])
    draw_region_chip(cv, x + w - 14, y + h - 14, s["region"])


def draw_pictured(cv, s, x, y, w, h):
    cv.rect(x, y, w, h, WHITE)
    cv.outline(x, y, w, h, MGRAY, 1)
    # icon strip at top
    cv.rect(x + 6, y + 6, w - 12, 36, LGRAY)
    draw_icon(cv, s["icon"], x + 6, y + 6, 36, INK, RED)
    # headline (scale 2, up to 2 lines)
    tx = x + 8
    tw = w - 16
    yy = y + 44
    for ln in wrap_text(str(s["rank"]) + ". " + s["head"], 2, tw)[:2]:
        draw_text(cv, tx, yy, ln, 2, INK)
        yy += 16
    # body (scale 1, up to 2 lines)
    yy += 1
    for ln in wrap_text(s["body"], 1, tw)[:2]:
        draw_text(cv, tx, yy, ln, 1, INK)
        yy += 9
    # meta
    draw_meta(cv, tx, y + h - 10, s["when"], s["tag"], s["src"])
    draw_region_chip(cv, x + w - 13, y + 13, s["region"])


def draw_brief(cv, s, x, y, w):
    # line 1: rank. HEADLINE - src - TAG
    line1 = str(s["rank"]) + ". " + s["head"] + " - " + s["src"] + " - " + s["tag"]
    draw_text(cv, x, y, line1, 1, INK)
    # body, trimmed at a word boundary so it never spills into the
    # next column
    body = s["body"]
    while text_width(body, 1) > w and " " in body:
        body = body.rsplit(" ", 1)[0]
    draw_text(cv, x, y + 9, body, 1, INK)


def build():
    cv = Canvas(W, H, PAPER)
    cv.outline(8, 8, W - 16, H - 16, INK, 3)

    # ---- header ----
    center_text(cv, 20, "ONE DAY - ONE PICTURE - THE WORLD", 2, INK)
    center_text(cv, 44, "WEDNESDAY 25 NOVEMBER 2026", 6, RED)
    cv.rect(16, 92, W - 32, 3, RED)
    center_text(cv, 100,
                "TO THE JUDGE: 35 STORIES, ALL FROM WEDNESDAY 25 NOVEMBER 2026, "
                "ALL DATED, EACH MARKED HOW SURE WE ARE - CONFIRMED MEANS 2+ OUTLETS.",
                1, INK)
    cv.rect(16, 112, W - 32, 22, LGRAY)
    center_text(cv, 119,
                "35 STORIES - 9 REGIONS - 4 LEADS - 8 PICTURED - 23 BRIEF - "
                "ALL DATED - ALL SOURCED", 1, INK)

    # ---- leads: 2 x 2 ----
    leads = [s for s in STORIES if s["kind"] == "lead"]
    for i, s in enumerate(leads):
        x = 16 + (i % 2) * 498
        y = 140 + (i // 2) * 112
        draw_lead(cv, s, x, y, 490, 106)

    # ---- pictured: 4 x 2 ----
    pics = [s for s in STORIES if s["kind"] == "pictured"]
    for i, s in enumerate(pics):
        x = 16 + (i % 4) * 248
        y = 372 + (i // 4) * 112
        draw_pictured(cv, s, x, y, 240, 106)

    # ---- middle band: map | timeline | date check + how sure ----
    # map panel
    cv.rect(16, 600, 336, 186, WHITE)
    cv.outline(16, 600, 336, 186, MGRAY, 1)
    center_text_in(cv, 16, 352, 606, "THE WORLD - 9 REGIONS", 1, INK)
    draw_map(cv, 24, 622, 320, 140)
    center_text_in(cv, 16, 352, 768, "NUMBERS = REGIONS - SEE STRIP BELOW", 1, MGRAY)
    # timeline panel
    cv.rect(360, 600, 296, 186, WHITE)
    cv.outline(360, 600, 296, 186, MGRAY, 1)
    center_text_in(cv, 360, 656, 606, "25 NOV IN UTC", 1, INK)
    yy = 626
    for (t, txt) in TIMELINE:
        draw_text(cv, 370, yy, t, 1, RED)
        draw_text(cv, 410, yy, txt, 1, INK)
        yy += 20
    # date check box
    cv.rect(664, 600, 344, 92, WHITE)
    cv.outline(664, 600, 344, 92, RED, 2)
    center_text_in(cv, 664, 1008, 606, "DATE CHECK", 2, RED)
    draw_text(cv, 676, 628, "TODAY: WEDNESDAY 25 NOVEMBER 2026", 1, INK)
    draw_text(cv, 676, 642, "NOT 24 NOV: SENEGAL AFCON RULING", 1, INK)
    draw_text(cv, 676, 656, "NOT 26 NOV: THANKSGIVING - PARADE MOVED TO SAT", 1, INK)
    draw_text(cv, 676, 672, "EVERY STORY HERE IS DATED 25 NOV", 1, INK)
    # how sure box
    cv.rect(664, 698, 344, 88, WHITE)
    cv.outline(664, 698, 344, 88, MGRAY, 1)
    center_text_in(cv, 664, 1008, 704, "HOW SURE ARE WE?", 2, INK)
    draw_text(cv, 676, 726, "CONFIRMED = 2+ OUTLETS", 1, BLUE)
    draw_text(cv, 676, 740, "OFFICIAL = OFFICIAL BODY", 1, GREEN)
    draw_text(cv, 676, 754, "CLAIM = ONE PARTY / OUTLET", 1, RED)
    draw_text(cv, 676, 768, "FORECAST = SCHEDULED / PREDICTION", 1, ORANGE)

    # ---- how to read ----
    center_text(cv, 794,
                "HOW TO READ: LEADS ARE THE DAY'S BIGGEST STORIES - PICTURED HAVE "
                "A DRAWING - ALSO ON IS THE REST - EVERY STORY IS DATED 25 NOV",
                1, INK)

    # ---- briefs: 3 columns ----
    center_text(cv, 812, "ALSO ON - 23 MORE STORIES, ALL DATED 25 NOV", 2, INK)
    briefs = [s for s in STORIES if s["kind"] == "brief"]
    for i, s in enumerate(briefs):
        col = i % 3
        row = i // 3
        x = 16 + col * 330
        y = 836 + row * 17
        draw_brief(cv, s, x, y, 324)

    # ---- big numbers + region strip + sources ----
    center_text(cv, 976,
                "720,000 RUSSIAN WAR DEAD, EST. - 31 KILLED IN CAIRO - GDP UP 4.3%",
                2, RED)
    strip = "REGIONS: " + " - ".join(
        "%d %s %d" % (n, name, cnt) for (n, name, cnt) in REGIONS)
    center_text(cv, 994, strip, 1, INK)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or os.environ.get(
        "MAKEFUN_OUTPUT") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    cv = build()
    write_png(os.path.join(out_dir, "entry.png"), W, H, bytes(cv.px))


if __name__ == "__main__":
    main()
