#!/usr/bin/env python3
"""Sum up 23 November 2026's world news in one image.

A newspaper front page, drawn entirely with the Python standard
library. No network, no clock, no randomness: the same input always
produces the same bytes. Writes /output/entry.png, 1024 by 1024.
"""
import math
import os
import struct
import zlib

PAGE_W = 1024
PAGE_H = 1024

CREAM = (248, 243, 232)
INK = (18, 18, 18)
CRIMSON = (178, 30, 30)
NAVY = (24, 42, 68)
TEAL = (18, 88, 92)
OCEAN = (48, 112, 140)
PALE = (216, 233, 236)
GOLD = (200, 134, 28)
LEAF = (76, 122, 64)
ASH = (98, 94, 86)
EMBER = (226, 96, 22)
SNOW = (255, 255, 255)
SMOKE = (228, 226, 218)

# ------------------------------------------------------------------ font
# A hand-made 5x7 bitmap font. Every glyph is seven rows; in each row
# bit 4 is the leftmost pixel. The whole page is set in capitals, so
# only capitals, digits and a small set of punctuation are defined.
GLYPHS = {
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
    'V': (0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100),
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
    '—': (0, 0, 0, 0b11111, 0, 0, 0),
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
    '•': (0, 0, 0b01100, 0b01100, 0, 0, 0),
    '&': (0b01100, 0b10010, 0b10100, 0b01000, 0b10101, 0b10010, 0b01101),
}

EMPTY_GLYPH = (0, 0, 0, 0, 0, 0, 0)


def glyph_width(text, size):
    """Pixel width of a string at the given font size."""
    return len(text) * 6 * size - size


def split_lines(text, size, max_width):
    """Greedy word wrap into lines no wider than max_width."""
    out = []
    for piece in text.split('\n'):
        words = piece.split(' ')
        current = ''
        for word in words:
            candidate = word if not current else current + ' ' + word
            if glyph_width(candidate, size) <= max_width or not current:
                current = candidate
            else:
                out.append(current)
                current = word
        if current:
            out.append(current)
    return out


# ------------------------------------------------------------------ page
class Page:
    """A plain RGB canvas with a tiny drawing vocabulary."""

    def __init__(self, width, height, background):
        self.width = width
        self.height = height
        self.data = bytearray(width * height * 3)
        self.box(0, 0, width, height, background)

    def dot(self, x, y, colour):
        if 0 <= x < self.width and 0 <= y < self.height:
            pos = (y * self.width + x) * 3
            self.data[pos], self.data[pos + 1], self.data[pos + 2] = colour

    def box(self, x, y, w, h, colour):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.width, x + w), min(self.height, y + h)
        for yy in range(y0, y1):
            start = (yy * self.width + x0) * 3
            for xx in range(x0, x1):
                pos = start + (xx - x0) * 3
                self.data[pos], self.data[pos + 1], self.data[pos + 2] = colour

    def frame(self, x, y, w, h, colour, thick=2):
        self.box(x, y, w, thick, colour)
        self.box(x, y + h - thick, w, thick, colour)
        self.box(x, y, thick, h, colour)
        self.box(x + w - thick, y, thick, h, colour)

    def rule(self, x, y, w, colour, thick=2):
        self.box(x, y, w, thick, colour)

    def segment(self, x0, y0, x1, y1, colour):
        """Bresenham line between two points."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        step_x = 1 if x0 < x1 else -1
        step_y = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.dot(x0, y0, colour)
            if x0 == x1 and y0 == y1:
                break
            doubled = 2 * err
            if doubled >= dy:
                err += dy
                x0 += step_x
            if doubled <= dx:
                err += dx
                y0 += step_y

    def disc(self, cx, cy, radius, colour):
        for dy in range(-radius, radius + 1):
            half = int((radius * radius - dy * dy) ** 0.5)
            self.box(cx - half, cy + dy, half * 2 + 1, 1, colour)

    def ring(self, cx, cy, radius, colour, thick=2):
        for k in range(thick):
            rr = radius - k
            for deg in range(0, 360, 3):
                rad = math.radians(deg)
                self.dot(cx + int(rr * math.cos(rad)),
                         cy + int(rr * math.sin(rad)), colour)

    def triangle(self, points, colour):
        """Filled triangle / polygon by horizontal scanlines."""
        ys = [p[1] for p in points]
        for y in range(min(ys), max(ys) + 1):
            hits = []
            count = len(points)
            for i in range(count):
                ax, ay = points[i]
                bx, by = points[(i + 1) % count]
                if (ay <= y < by) or (by <= y < ay):
                    hits.append(ax + (y - ay) * (bx - ax) / (by - ay))
            if len(hits) >= 2:
                hits.sort()
                self.box(int(hits[0]), y, int(hits[-1]) - int(hits[0]) + 1, 1, colour)

    def oval(self, cx, cy, rx, ry, colour):
        for dy in range(-ry, ry + 1):
            half = int(rx * (1 - (dy * dy) / (ry * ry)) ** 0.5) if ry else 0
            self.box(cx - half, cy + dy, half * 2 + 1, 1, colour)

    def write(self, x, y, text, size, colour):
        cursor = x
        for char in text:
            glyph = GLYPHS.get(char.upper(), EMPTY_GLYPH)
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits >> (4 - col) & 1:
                        self.box(cursor + col * size, y + row * size,
                                 size, size, colour)
            cursor += 6 * size

    def write_centred(self, y, text, size, colour, centre=512):
        self.write(centre - glyph_width(text, size) // 2, y, text, size, colour)

    def paragraph(self, x, y, text, size, max_width, colour=INK, gap=4):
        """Draw wrapped text; return the y just below the last line."""
        step = size * 7 + gap
        for i, line in enumerate(split_lines(text, size, max_width)):
            self.write(x, y + i * step, line, size, colour)
        return y + len(split_lines(text, size, max_width)) * step


def encode_png(page):
    """Encode the page as PNG bytes; filter byte 0 on every scanline."""
    raw = bytearray()
    for y in range(page.height):
        raw.append(0)
        raw += page.data[y * page.width * 3:(y + 1) * page.width * 3]

    def chunk(tag, payload):
        block = struct.pack('>I', len(payload)) + tag + payload
        block += struct.pack('>I', zlib.crc32(tag + payload) & 0xffffffff)
        return block

    header = struct.pack('>IIBBBBB', page.width, page.height, 8, 2, 0, 0, 0)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', header)
            + chunk(b'IDAT', zlib.compress(bytes(raw), 9))
            + chunk(b'IEND', b''))


# ------------------------------------------------------------ pictures
def draw_sun(page, cx, cy, radius, colour=GOLD):
    """A sun with eight straight rays."""
    for k in range(8):
        angle = math.radians(k * 45)
        x0 = cx + int((radius + 5) * math.cos(angle))
        y0 = cy + int((radius + 5) * math.sin(angle))
        x1 = cx + int((radius + 16) * math.cos(angle))
        y1 = cy + int((radius + 16) * math.sin(angle))
        page.segment(x0, y0, x1, y1, colour)
    page.disc(cx, cy, radius, colour)


def draw_globe(page, cx, cy, radius):
    """A small stylised world: blue sea, green land, white clouds."""
    page.disc(cx, cy, radius, OCEAN)
    page.oval(cx - radius // 3, cy - radius // 4, radius // 3, radius // 5, LEAF)
    page.oval(cx + radius // 4, cy + radius // 6, radius // 4, radius // 6, LEAF)
    page.oval(cx + radius // 10, cy - radius // 2, radius // 5, radius // 8, LEAF)
    page.oval(cx - radius // 6, cy + radius // 2, radius // 4, radius // 7, LEAF)
    page.ring(cx, cy, radius, INK, 2)
    page.oval(cx - radius // 2, cy - radius // 8, radius // 3, radius // 12, SNOW)
    page.oval(cx + radius // 5, cy + radius // 3, radius // 4, radius // 12, SNOW)


def draw_sea(page, x, y, width, colour=TEAL):
    """Three zig-zag wave rows."""
    for row, yy in enumerate((y, y + 10, y + 20)):
        xx = x + (7 if row % 2 else 0)
        while xx < x + width - 12:
            page.segment(xx, yy + 4, xx + 6, yy, colour)
            page.segment(xx + 6, yy, xx + 12, yy + 4, colour)
            xx += 14


def draw_tanker(page, x, y, width):
    """A tanker seen side-on; y is the waterline."""
    page.triangle([(x, y - 16), (x + width, y - 16),
                   (x + width - 12, y), (x + 8, y)], NAVY)
    for i in range(3):
        cx = x + 20 + i * 62
        page.disc(cx + 22, y - 10, 14, SNOW)
        page.ring(cx + 22, y - 10, 14, INK, 2)
    page.box(x + width - 26, y - 52, 9, 14, CRIMSON)
    page.disc(x + width - 21, y - 56, 4, ASH)
    page.disc(x + width - 32, y - 48, 5, ASH)


def draw_capitol(page, x, y, width, height):
    """A domed capitol: dome, drum, columns and steps.

    The columns run from the entablature down to the steps, so their
    height is always positive for the sizes this page uses.
    """
    page.box(x, y + height - 6, width, 6, NAVY)
    page.box(x + 10, y + height - 12, width - 20, 6, NAVY)
    col_top = y + 26
    col_bottom = y + height - 12
    for i in range(5):
        col_x = x + 16 + i * (width - 32) // 5
        page.box(col_x, col_top, 8, col_bottom - col_top, NAVY)
    page.box(x + 6, y + 20, width - 12, 6, NAVY)
    page.oval(x + width // 2, y + 16, width // 5, 10, NAVY)
    page.box(x + width // 2 - 2, y + 2, 4, 6, NAVY)
    page.disc(x + width // 2, y + 2, 3, GOLD)


def draw_scales(page, cx, top):
    """Balanced scales of justice: post, beam and two pans."""
    page.box(cx - 2, top, 4, 44, NAVY)
    page.box(cx - 34, top + 6, 68, 3, NAVY)
    page.disc(cx, top - 4, 4, GOLD)
    for side in (-1, 1):
        px = cx + side * 30
        page.segment(px, top + 7, px - 10, top + 26, NAVY)
        page.segment(px, top + 7, px + 10, top + 26, NAVY)
        page.triangle([(px - 12, top + 26), (px + 12, top + 26),
                       (px, top + 38)], CRIMSON)


def draw_rubble(page, x, y, width):
    """Broken blocks piled up, with a small flame on top."""
    page.box(x, y + 18, width // 2, 14, ASH)
    page.box(x + width // 3, y + 6, width // 2, 14, SMOKE)
    page.frame(x, y + 18, width // 2, 14, INK, 1)
    page.frame(x + width // 3, y + 6, width // 2, 14, INK, 1)
    page.triangle([(x + width // 2, y + 6), (x + width // 2 + 10, y - 12),
                   (x + width // 2 + 20, y + 6)], EMBER)
    page.triangle([(x + width // 2 + 12, y + 6), (x + width // 2 + 19, y - 6),
                   (x + width // 2 + 26, y + 6)], GOLD)


# ---------------------------------------------------------------- layout
def build_front():
    page = Page(PAGE_W, PAGE_H, CREAM)
    page.frame(20, 20, PAGE_W - 40, PAGE_H - 40, INK, 3)

    # Masthead and date banner.
    page.write_centred(38, 'THE WORLD IN ONE DAY', 6, INK)
    page.rule(28, 96, 968, CRIMSON, 4)
    page.box(28, 106, 968, 36, CRIMSON)
    page.write_centred(114, 'MONDAY 23 NOVEMBER 2026', 3, SNOW)

    # ---- Lead: COP31 collapses.
    page.frame(28, 154, 968, 300, INK, 2)
    page.write(48, 172, 'COP31 \u2022 ANTALYA, TURKEY', 2, CRIMSON)
    page.write(48, 196, 'CLIMATE TALKS', 5, INK)
    page.write(48, 244, 'COLLAPSE', 5, INK)
    page.paragraph(48, 292,
                   'AFTER TWO WEEKS OF TALKS AND TWO DAYS OF OVERTIME, '
                   'THE ANTALYA PACT WAS REJECTED ON SUNDAY. NO OVERARCHING '
                   'DEAL. THE FINAL TEXT NEVER MENTIONED COAL, OIL OR GAS. '
                   'THE EU AND 100+ COUNTRIES HAD PUSHED FOR FOSSIL-FUEL '
                   'WORDING. THE LONGEST COP EVER.',
                   2, 540)
    page.box(620, 170, 356, 268, PALE)
    page.frame(620, 170, 356, 268, INK, 2)
    draw_sun(page, 700, 232, 28)
    draw_globe(page, 856, 330, 64)
    draw_sea(page, 636, 404, 324)
    page.write(636, 178, 'ANTALYA', 2, TEAL)

    # ---- Row 2: the Gulf and Washington.
    page.frame(28, 470, 468, 228, INK, 2)
    page.box(44, 478, 436, 58, PALE)
    page.frame(44, 478, 436, 58, INK, 2)
    draw_sea(page, 48, 508, 428)
    draw_tanker(page, 90, 530, 330)
    page.write(44, 544, 'THE GULF', 2, CRIMSON)
    page.write(44, 568, 'GULF ON EDGE', 3, INK)
    page.paragraph(44, 598,
                   'TRUMP MAY RESUME STRIKES AFTER THE NEW YEAR IF NO DEAL '
                   'IS REACHED. IRAN STRUCK US PATRIOT RADARS IN BAHRAIN. '
                   'A CIVILIAN PLANT BURNED, 2 INJURED. TANKERS HIT NEAR '
                   'HORMUZ.',
                   2, 436)

    page.frame(528, 470, 468, 228, INK, 2)
    page.box(544, 478, 436, 58, SMOKE)
    page.frame(544, 478, 436, 58, INK, 2)
    draw_capitol(page, 624, 480, 276, 52)
    page.write(544, 544, 'WASHINGTON', 2, CRIMSON)
    page.write(544, 568, 'DEMOCRATS WIN BIG', 3, INK)
    page.paragraph(544, 598,
                   'DEMOCRATS CLINCHED AT LEAST 258 SEATS, THE LARGEST '
                   'HOUSE MAJORITY THIS CENTURY. IN NORTH CAROLINA, '
                   'HUBBARD BEAT FOXX BY UNDER 300 VOTES.',
                   2, 436)

    # ---- Row 3: the rescued boy, Myanmar, and the brief.
    page.frame(28, 714, 304, 220, INK, 2)
    draw_rubble(page, 60, 730, 240)
    page.write(44, 770, 'BOY, 7,', 3, INK)
    page.write(44, 796, 'RESCUED', 3, INK)
    page.paragraph(44, 822,
                   'A RUSSIAN STRIKE IN DYMER KILLED 11. DAVYD, 7, WAS '
                   'PULLED ALIVE AFTER HOURS UNDER RUBBLE. A WOMAN, 79, '
                   'ALSO RESCUED.',
                   2, 272)

    page.frame(360, 714, 304, 220, INK, 2)
    draw_scales(page, 512, 724)
    page.write(376, 776, 'MYANMAR GUILTY', 3, INK)
    page.paragraph(376, 806,
                   'THE WORLD COURT RULED 9-6 MYANMAR COMMITTED GENOCIDE '
                   'AGAINST THE ROHINGYA. A FIRST IN 80 YEARS. '
                   'REPARATIONS AND RETURN ORDERED.',
                   2, 272)

    page.frame(692, 714, 304, 220, INK, 2)
    page.write(708, 730, 'ALSO IN BRIEF', 3, INK)
    y = 768
    for item in ('\u2022 BANTEN: FIRE, 24 DEAD, 30 MISSING',
                 '\u2022 SEATTLE: ICE JET BRIDGE ARRESTS',
                 '\u2022 PIG KIDNEY: 1 YEAR, A RECORD'):
        y = page.paragraph(708, y, item, 2, 272)
        y += 8

    # Footer.
    page.rule(28, 950, 968, INK, 2)
    page.write_centred(962, '23 NOVEMBER 2026 \u2014 THE DAY IN BRIEF', 2, INK)
    return page


def main():
    out_dir = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
    os.makedirs(out_dir, exist_ok=True)
    data = encode_png(build_front())
    with open(os.path.join(out_dir, 'entry.png'), 'wb') as handle:
        handle.write(data)


if __name__ == '__main__':
    main()
