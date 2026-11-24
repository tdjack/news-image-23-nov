#!/usr/bin/env python3
"""Sum up 23 November 2026's world news in one image.

A newspaper front page, drawn entirely with the Python standard library.
Writes /output/entry.png (1024x1024, deterministic, no network, no clock).
"""
import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (247, 242, 231)
INK = (17, 17, 17)
RED = (176, 32, 32)
TEAL = (20, 85, 90)
SEA = (46, 111, 139)
SKY = (214, 232, 235)
OCHRE = (198, 132, 30)
GREEN = (74, 120, 62)
GREY = (96, 92, 84)
DARK = (28, 38, 54)
FLAME = (224, 94, 20)
WHITE = (255, 255, 255)

# ---------------------------------------------------------------- font
# 5x7 bitmap font, hand defined. Each glyph is 7 rows; bit 4 is the
# leftmost pixel, bit 0 the rightmost. Only capitals, digits and a few
# punctuation marks are needed: the whole page is set in capitals.
F = {
    'A': (0b01110, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    'B': (0b11110, 0b10001, 0b10001, 0b11110, 0b10001, 0b10001, 0b11110),
    'C': (0b01110, 0b10001, 0b10000, 0b10000, 0b10000, 0b10001, 0b01110),
    'D': (0b11110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b11110),
    'E': (0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b11111),
    'F': (0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b10000),
    'G': (0b01110, 0b10001, 0b10000, 0b10111, 0b10001, 0b10001, 0b01111),
    'H': (0b10001, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    'I': (0b01110, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    'J': (0b00111, 0b00010, 0b00010, 0b00010, 0b00010, 0b10010, 0b01100),
    'K': (0b10001, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010, 0b10001),
    'L': (0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b11111),
    'M': (0b10001, 0b11011, 0b10101, 0b10101, 0b10001, 0b10001, 0b10001),
    'N': (0b10001, 0b11001, 0b10101, 0b10011, 0b10001, 0b10001, 0b10001),
    'O': (0b01110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    'P': (0b11110, 0b10001, 0b10001, 0b11110, 0b10000, 0b10000, 0b10000),
    'Q': (0b01110, 0b10001, 0b10001, 0b10001, 0b10101, 0b10010, 0b01101),
    'R': (0b11110, 0b10001, 0b10001, 0b11110, 0b10100, 0b10010, 0b10001),
    'S': (0b01111, 0b10000, 0b10000, 0b01110, 0b00001, 0b00001, 0b11110),
    'T': (0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100),
    'U': (0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    'V': (0b10001, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100, 0b00100),
    'W': (0b10001, 0b10001, 0b10001, 0b10101, 0b10101, 0b11011, 0b10001),
    'X': (0b10001, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001, 0b10001),
    'Y': (0b10001, 0b10001, 0b01010, 0b00100, 0b00100, 0b00100, 0b00100),
    'Z': (0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b11111),
    '0': (0b01110, 0b10001, 0b10011, 0b10101, 0b11001, 0b10001, 0b01110),
    '1': (0b00100, 0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    '2': (0b01110, 0b10001, 0b00001, 0b00110, 0b01000, 0b10000, 0b11111),
    '3': (0b11111, 0b00010, 0b00100, 0b00010, 0b00001, 0b10001, 0b01110),
    '4': (0b00010, 0b00110, 0b01010, 0b10010, 0b11111, 0b00010, 0b00010),
    '5': (0b11111, 0b10000, 0b11110, 0b00001, 0b00001, 0b10001, 0b01110),
    '6': (0b00110, 0b01000, 0b10000, 0b11110, 0b10001, 0b10001, 0b01110),
    '7': (0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b01000, 0b01000),
    '8': (0b01110, 0b10001, 0b10001, 0b01110, 0b10001, 0b10001, 0b01110),
    '9': (0b01110, 0b10001, 0b10001, 0b01111, 0b00001, 0b00010, 0b01100),
    ' ': (0, 0, 0, 0, 0, 0, 0),
    '.': (0, 0, 0, 0, 0, 0, 0b00100),
    ',': (0, 0, 0, 0, 0, 0b00100, 0b01000),
    '-': (0, 0, 0, 0b01110, 0, 0, 0),
    '\u2014': (0, 0, 0, 0b11111, 0, 0, 0),  # em dash
    ':': (0, 0b00100, 0, 0, 0, 0b00100, 0),
    ';': (0, 0b00100, 0, 0, 0, 0b00100, 0b01000),
    "'": (0b00100, 0b00100, 0b01000, 0, 0, 0, 0),
    '(': (0b00010, 0b00100, 0b01000, 0b01000, 0b01000, 0b00100, 0b00010),
    ')': (0b01000, 0b00100, 0b00010, 0b00010, 0b00010, 0b00100, 0b01000),
    '%': (0b11001, 0b11010, 0b00010, 0b00100, 0b01000, 0b01011, 0b10011),
    '+': (0, 0b00100, 0b00100, 0b11111, 0b00100, 0b00100, 0),
    '/': (0b00001, 0b00010, 0b00010, 0b00100, 0b01000, 0b01000, 0b10000),
    '?': (0b01110, 0b10001, 0b00001, 0b00110, 0b00100, 0, 0b00100),
    '!': (0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0, 0b00100),
    '"': (0b01010, 0b01010, 0, 0, 0, 0, 0),
    '=': (0, 0, 0b11111, 0, 0b11111, 0, 0),
    '\u2022': (0, 0, 0b01100, 0b01100, 0, 0, 0),  # bullet
    '&': (0b01100, 0b10010, 0b10100, 0b01000, 0b10101, 0b10010, 0b01101),
}

BLANK = (0, 0, 0, 0, 0, 0, 0)


def text_width(text, scale):
    """Width in pixels of text at the given scale."""
    return len(text) * 6 * scale - scale


def wrap(text, scale, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    lines = []
    for chunk in text.split('\n'):
        words = chunk.split(' ')
        line = ''
        for word in words:
            trial = word if not line else line + ' ' + word
            if text_width(trial, scale) <= max_w or not line:
                line = trial
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def fill_rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = c

    def outline_rect(self, x, y, w, h, c, t=2):
        self.fill_rect(x, y, w, t, c)
        self.fill_rect(x, y + h - t, w, t, c)
        self.fill_rect(x, y, t, h, c)
        self.fill_rect(x + w - t, y, t, h, c)

    def hline(self, x, y, w, c, t=1):
        self.fill_rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.fill_rect(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            half = int((r * r - dy * dy) ** 0.5)
            self.fill_rect(cx - half, cy + dy, half * 2 + 1, 1, c)

    def ring(self, cx, cy, r, c, t=2):
        for k in range(t):
            rr = r - k
            for deg in range(0, 360, 2):
                import math
                x = cx + int(rr * math.cos(math.radians(deg)))
                y = cy + int(rr * math.sin(math.radians(deg)))
                self.set(x, y, c)

    def poly(self, pts, c):
        """Filled polygon via scanlines."""
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            if len(xs) >= 2:
                xs.sort()
                self.fill_rect(int(xs[0]), y, int(xs[-1]) - int(xs[0]) + 1, 1, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for dy in range(-ry, ry + 1):
            half = int(rx * (1 - (dy * dy) / (ry * ry)) ** 0.5) if ry else 0
            self.fill_rect(cx - half, cy + dy, half * 2 + 1, 1, c)

    def text(self, x, y, s, scale, c):
        cx = x
        for ch in s:
            glyph = F.get(ch.upper(), BLANK)
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits >> (4 - col) & 1:
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       scale, scale, c)
            cx += 6 * scale

    def text_center(self, y, s, scale, c, cx=512):
        self.text(cx - text_width(s, scale) // 2, y, s, scale, c)


def png_bytes(cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]

    def chunk(tag, data):
        out = struct.pack('>I', len(data)) + tag + data
        out += struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
        return out

    ihdr = struct.pack('>IIBBBBB', cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr)
            + chunk(b'IDAT', zlib.compress(bytes(raw), 9))
            + chunk(b'IEND', b''))


# ---------------------------------------------------------------- pictures
def draw_sun(cv, cx, cy, r, c=OCHRE):
    for k in range(8):
        import math
        a = math.radians(k * 45)
        x0 = cx + int((r + 4) * math.cos(a))
        y0 = cy + int((r + 4) * math.sin(a))
        x1 = cx + int((r + 14) * math.cos(a))
        y1 = cy + int((r + 14) * math.sin(a))
        cv.line(x0, y0, x1, y1, c)
    cv.disc(cx, cy, r, c)


def draw_globe(cv, cx, cy, r):
    cv.disc(cx, cy, r, SEA)
    cv.ellipse(cx - r // 3, cy - r // 4, r // 3, r // 5, GREEN)
    cv.ellipse(cx + r // 4, cy + r // 6, r // 4, r // 6, GREEN)
    cv.ellipse(cx + r // 10, cy - r // 2, r // 5, r // 8, GREEN)
    cv.ellipse(cx - r // 6, cy + r // 2, r // 4, r // 7, GREEN)
    cv.ring(cx, cy, r, INK, 2)
    cv.ellipse(cx - r // 2, cy - r // 8, r // 3, r // 12, WHITE)
    cv.ellipse(cx + r // 5, cy + r // 3, r // 4, r // 12, WHITE)


def draw_cracked_globe(cv, cx, cy, r):
    """The globe with a red crack across it: the pact that broke."""
    draw_globe(cv, cx, cy, r)
    crack = [(cx - r + 12, cy - r + 18), (cx - r // 3, cy - r // 6),
             (cx - r // 2, cy + r // 4), (cx + r // 4, cy + r // 2),
             (cx + r - 12, cy + r - 14)]
    for i in range(len(crack) - 1):
        x0, y0 = crack[i]
        x1, y1 = crack[i + 1]
        cv.line(x0, y0, x1, y1, RED)
        cv.line(x0 + 1, y0, x1 + 1, y1, RED)
        cv.line(x0, y0 + 1, x1, y1 + 1, RED)


def draw_waves(cv, x, y, w, c=TEAL):
    for k, yy in enumerate((y, y + 10, y + 20)):
        xx = x + (6 if k % 2 else 0)
        while xx < x + w - 12:
            cv.line(xx, yy + 4, xx + 6, yy, c)
            cv.line(xx + 6, yy, xx + 12, yy + 4, c)
            xx += 14


def draw_tanker(cv, x, y, w):
    cv.poly([(x, y - 16), (x + w, y - 16), (x + w - 12, y), (x + 8, y)], DARK)
    for i in range(3):
        cx = x + 20 + i * 62
        cv.disc(cx + 22, y - 10, 14, WHITE)
        cv.ring(cx + 22, y - 10, 14, INK, 2)
    cv.fill_rect(x + w - 26, y - 52, 9, 14, RED)
    cv.disc(x + w - 21, y - 56, 4, GREY)
    cv.disc(x + w - 32, y - 48, 5, GREY)


def draw_ballot(cv, x, y, w, h):
    """A ballot box with rising result bars behind it."""
    bars = [(RED, 26), (TEAL, 40), (OCHRE, 54)]
    bx = x + 18
    for i, (c, bh) in enumerate(bars):
        cv.fill_rect(bx + i * 34, y + h - bh, 22, bh, c)
        cv.outline_rect(bx + i * 34, y + h - bh, 22, bh, INK, 1)
    cv.fill_rect(x + w - 118, y + h - 58, 96, 58, DARK)
    cv.outline_rect(x + w - 118, y + h - 58, 96, 58, INK, 2)
    cv.fill_rect(x + w - 100, y + h - 58, 60, 6, WHITE)
    # ballot half-slipped into the slot, inside the picture strip
    cv.fill_rect(x + w - 96, y + 4, 52, 20, WHITE)
    cv.outline_rect(x + w - 96, y + 4, 52, 20, INK, 1)
    cv.line(x + w - 88, y + 14, x + w - 78, y + 19, RED)
    cv.line(x + w - 78, y + 19, x + w - 60, y + 7, RED)


def draw_rubble(cv, x, y, w):
    """A collapsed building: a mound of dark blocks and a small flame."""
    cv.poly([(x, y), (x + w // 3, y - 26), (x + 2 * w // 3, y - 14),
             (x + w, y)], DARK)
    cv.fill_rect(x + 24, y - 26, 46, 26, GREY)
    cv.outline_rect(x + 24, y - 26, 46, 26, INK, 1)
    cv.fill_rect(x + 96, y - 18, 40, 18, GREY)
    cv.outline_rect(x + 96, y - 18, 40, 18, INK, 1)
    cv.poly([(x + w // 2, y - 26), (x + w // 2 + 10, y - 44),
             (x + w // 2 + 20, y - 26)], FLAME)
    cv.disc(x + w // 4, y - 32, 4, GREY)
    cv.disc(x + w // 4 - 10, y - 38, 3, GREY)


def draw_scales(cv, cx, y, h):
    """Scales of justice."""
    cv.vline(cx, y, h, INK, 3)
    cv.hline(cx - 34, y + 4, 68, INK, 3)
    cv.fill_rect(cx - 10, y + h - 4, 20, 4, INK)
    for sx in (cx - 34, cx + 34):
        cv.line(sx, y + 6, sx - 12, y + 22, INK)
        cv.line(sx, y + 6, sx + 12, y + 22, INK)
        cv.poly([(sx - 14, y + 22), (sx + 14, y + 22), (sx, y + 30)], TEAL)
    cv.disc(cx, y - 2, 4, OCHRE)


# ---------------------------------------------------------------- layout
def panel(cv, x, y, w, h):
    cv.outline_rect(x, y, w, h, INK, 2)


def deck(cv, x, y, text, scale, max_w, color=INK, lh=None):
    lines = wrap(text, scale, max_w)
    lh = lh or (scale * 7 + 4)
    for i, line in enumerate(lines):
        cv.text(x, y + i * lh, line, scale, color)
    return y + len(lines) * lh


def draw_page():
    cv = Canvas(W, H, PAPER)
    cv.outline_rect(16, 16, W - 32, H - 32, INK, 3)

    # Masthead
    cv.text_center(34, 'THE WORLD IN ONE DAY', 7, INK)
    cv.fill_rect(28, 92, 968, 4, RED)
    cv.fill_rect(28, 104, 968, 34, RED)
    cv.text_center(111, 'MONDAY 23 NOVEMBER 2026', 3, WHITE)

    # ---- Lead: COP31 collapse
    panel(cv, 28, 154, 968, 308)
    cv.text(48, 172, 'COP31 \u2022 ANTALYA, TURKEY', 2, RED)
    cv.text(48, 198, 'CLIMATE TALKS', 5, INK)
    cv.text(48, 246, 'COLLAPSE', 5, INK)
    deck(cv, 48, 300,
         'AFTER TWO WEEKS OF TALKS AND TWO DAYS OF OVERTIME, THE ANTALYA '
         'PACT WAS REJECTED ON SUNDAY. NO OVERARCHING DEAL. THE FINAL TEXT '
         'NEVER MENTIONED COAL, OIL OR GAS. THE EU AND 100+ COUNTRIES HAD '
         'PUSHED FOR FOSSIL-FUEL WORDING. THE LONGEST COP EVER.',
         2, 540)
    # picture: sun, cracked globe, waves
    cv.fill_rect(620, 170, 356, 276, SKY)
    cv.outline_rect(620, 170, 356, 276, INK, 2)
    draw_sun(cv, 700, 236, 30)
    draw_cracked_globe(cv, 852, 330, 66)
    draw_waves(cv, 636, 408, 324)
    cv.text(636, 178, 'ANTALYA', 2, TEAL)

    # ---- Row 2: Gulf and US House
    # Gulf
    panel(cv, 28, 478, 468, 236)
    cv.fill_rect(44, 486, 436, 70, SKY)
    cv.outline_rect(44, 486, 436, 70, INK, 2)
    draw_waves(cv, 48, 534, 428)
    draw_tanker(cv, 90, 550, 330)
    cv.text(44, 566, 'THE GULF', 2, RED)
    cv.text(44, 590, 'GULF ON EDGE', 3, INK)
    deck(cv, 44, 620,
         'TRUMP MAY RESUME STRIKES AFTER THE NEW YEAR IF NO DEAL IS REACHED. '
         'IRAN STRUCK US PATRIOT RADARS IN BAHRAIN. A CIVILIAN PLANT BURNED, '
         '2 INJURED. TANKERS HIT NEAR HORMUZ.',
         2, 436)
    # US House
    panel(cv, 528, 478, 468, 236)
    cv.fill_rect(544, 486, 436, 70, SKY)
    cv.outline_rect(544, 486, 436, 70, INK, 2)
    draw_ballot(cv, 560, 486, 404, 70)
    cv.text(544, 566, 'WASHINGTON', 2, RED)
    cv.text(544, 590, 'DEMOCRATS WIN BIG', 3, INK)
    deck(cv, 544, 620,
         'DEMOCRATS CLINCHED AT LEAST 258 SEATS, THE LARGEST HOUSE MAJORITY '
         'THIS CENTURY. IN NORTH CAROLINA, HUBBARD BEAT FOXX BY UNDER 300 '
         'VOTES.',
         2, 436)

    # ---- Row 3: Dymer, ICJ, also in brief
    # Dymer
    panel(cv, 28, 730, 304, 216)
    cv.fill_rect(44, 738, 272, 30, (226, 224, 216))
    cv.outline_rect(44, 738, 272, 30, INK, 2)
    draw_rubble(cv, 60, 766, 240)
    cv.text(44, 782, 'BOY, 7, RESCUED', 3, INK)
    deck(cv, 44, 820,
         'A RUSSIAN STRIKE IN DYMER KILLED 11. DAVYD, 7, WAS PULLED ALIVE '
         'AFTER HOURS UNDER RUBBLE. A WOMAN, 79, WAS ALSO RESCUED.',
         2, 272)
    # ICJ
    panel(cv, 360, 730, 304, 216)
    cv.fill_rect(376, 738, 272, 30, SKY)
    cv.outline_rect(376, 738, 272, 30, INK, 2)
    draw_scales(cv, 512, 738, 30)
    cv.text(376, 782, 'MYANMAR GUILTY', 3, INK)
    deck(cv, 376, 820,
         'THE WORLD COURT RULED 9-6 MYANMAR COMMITTED GENOCIDE AGAINST THE '
         'ROHINGYA. A FIRST IN 80 YEARS. REPARATIONS AND RETURN ORDERED.',
         2, 272)
    # Also in brief
    panel(cv, 692, 730, 304, 216)
    cv.fill_rect(708, 738, 272, 30, SKY)
    cv.outline_rect(708, 738, 272, 30, INK, 2)
    draw_globe(cv, 844, 753, 13)
    cv.text(708, 780, 'ALSO IN BRIEF', 3, INK)
    y = 812
    for item in ('BANTEN: FIRE, 24 DEAD, 30 MISSING',
                 'SEATTLE: ICE JET BRIDGE ARRESTS',
                 'PIG KIDNEY: 1 YEAR, A RECORD'):
        y = deck(cv, 708, y, '\u2022 ' + item, 2, 272)
        y += 6

    # Footer
    cv.hline(28, 962, 968, INK, 2)
    cv.text_center(972, '23 NOVEMBER 2026 \u2014 THE DAY IN BRIEF', 2, INK)
    return cv


def main():
    out_dir = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(draw_page())
    with open(os.path.join(out_dir, 'entry.png'), 'wb') as f:
        f.write(data)


if __name__ == '__main__':
    main()
