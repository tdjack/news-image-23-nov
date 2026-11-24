#!/usr/bin/env python3
"""Sum up 23 November 2026's world news in one image.

A newspaper front page, drawn entirely with the Python standard
library. The picture is built on a plain dict surface (an RGB
bytearray plus its width and height), glyphs are stored as tuples of
'#' / '.' strings, and the page is laid out from a PANELS table that
draw_panel walks. The program writes /output/entry.png (or the
directory in MAKEFUN_OUTPUT_DIR) and is fully deterministic: two
runs write the same bytes.
"""

import os
import struct
import zlib

PAPER = (238, 232, 214)
INK = (20, 20, 20)
RED = (178, 34, 34)
WHITE = (255, 255, 255)
SKY = (200, 225, 235)
SEA = (40, 110, 140)
LAND = (90, 150, 80)
GOLD = (220, 150, 30)
NAVY = (25, 45, 70)
GREY = (120, 120, 120)
TEAL = (60, 140, 140)
ORANGE = (220, 110, 40)

# 5x7 bitmap font. Each glyph is 7 strings of 5 characters; '#'
# paints a pixel, '.' leaves the paper showing. Written out by hand,
# one letter at a time.
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("..#..", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
}

FONT.update({
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "(": ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ")": ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    "%": ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    "/": ("....#", "....#", "...#.", "...#.", "..#..", ".#...", "#...."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
})


def glyph_rows(ch):
    """The 7 rows for one character, each padded to exactly 5 cells."""
    rows = FONT.get(ch)
    if rows is None:
        return (".....",) * 7
    return tuple(row.ljust(5, ".")[:5] for row in rows)


def new_surface(w, h, rgb):
    """A blank page: width, height and an RGB bytearray full of rgb."""
    return {"w": w, "h": h, "px": bytearray(bytes(rgb) * (w * h))}


def set_px(s, x, y, rgb):
    if 0 <= x < s["w"] and 0 <= y < s["h"]:
        at = (y * s["w"] + x) * 3
        s["px"][at:at + 3] = bytes(rgb)


def fill_rect(s, x, y, w, h, rgb):
    """Paint a solid rectangle, clipped to the page edges."""
    x0 = max(x, 0)
    y0 = max(y, 0)
    x1 = min(x + w, s["w"])
    y1 = min(y + h, s["h"])
    band = bytes(rgb) * (x1 - x0)
    for yy in range(y0, y1):
        at = (yy * s["w"] + x0) * 3
        s["px"][at:at + len(band)] = band


def outline_rect(s, x, y, w, h, rgb):
    fill_rect(s, x, y, w, 1, rgb)
    fill_rect(s, x, y + h - 1, w, 1, rgb)
    fill_rect(s, x, y, 1, h, rgb)
    fill_rect(s, x + w - 1, y, 1, h, rgb)


def disc(s, cx, cy, r, rgb):
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r:
                set_px(s, cx + dx, cy + dy, rgb)


def hline(s, x, y, length, rgb):
    fill_rect(s, x, y, length, 1, rgb)


def vline(s, x, y, length, rgb):
    fill_rect(s, x, y, 1, length, rgb)


def tri_up(s, x, y, w, h, rgb):
    """Filled triangle with its point at the top."""
    for i in range(h):
        wide = w * (i + 1) // h
        fill_rect(s, x + (w - wide) // 2, y + i, wide, 1, rgb)


def tri_down(s, x, y, w, h, rgb):
    """Filled triangle with its point at the bottom."""
    for i in range(h):
        wide = w - (w * i // h)
        fill_rect(s, x + (w - wide) // 2, y + i, wide, 1, rgb)


def draw_text(s, x, y, text, scale, rgb):
    """Draw text left to right; each glyph is 6*scale pixels wide."""
    cx = x
    for ch in text:
        for ry, row in enumerate(glyph_rows(ch)):
            for rx, cell in enumerate(row):
                if cell == "#":
                    fill_rect(s, cx + rx * scale, y + ry * scale,
                              scale, scale, rgb)
        cx += 6 * scale


def wrap_text(text, max_chars):
    """Greedy word wrap; returns a list of lines no longer than max_chars."""
    if max_chars < 1:
        max_chars = 1
    lines = []
    for word in text.split(" "):
        if not lines or len(lines[-1]) + 1 + len(word) > max_chars:
            lines.append(word)
        else:
            lines[-1] += " " + word
    return lines


def save_png(path, s):
    """Write the surface out as a PNG with filter byte 0 on every row."""
    w, h, px = s["w"], s["h"], s["px"]
    raw = bytearray()
    stride = w * 3
    for yy in range(h):
        raw.append(0)
        raw += px[yy * stride:(yy + 1) * stride]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    blob = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 6))
            + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(blob)


def pic_globe(s, x, y, w, h):
    """Antalya sky: sun, sea lines and a cracked-looking globe."""
    fill_rect(s, x, y, w, h, SKY)
    disc(s, x + 55, y + 40, 26, GOLD)
    hline(s, x + 55 - 40, y + 40, 12, GOLD)
    hline(s, x + 55 + 28, y + 40, 12, GOLD)
    vline(s, x + 55, y + 40 - 40, 12, GOLD)
    vline(s, x + 55, y + 40 + 28, 12, GOLD)
    for yy in (y + h - 24, y + h - 16, y + h - 8):
        hline(s, x + 8, yy, w - 16, TEAL)
    cx, cy = x + w - 110, y + h - 95
    disc(s, cx, cy, 58, SEA)
    disc(s, cx - 18, cy - 20, 12, LAND)
    disc(s, cx + 14, cy - 28, 9, LAND)
    disc(s, cx + 8, cy + 16, 11, LAND)
    disc(s, cx - 26, cy + 8, 7, WHITE)
    disc(s, cx + 26, cy - 4, 6, WHITE)
    # a red crack across the globe
    hline(s, cx - 40, cy - 8, 26, RED)
    hline(s, cx - 16, cy + 2, 22, RED)
    hline(s, cx + 4, cy + 12, 26, RED)


def pic_tanker(s, x, y, w, h):
    """A tanker crossing the Gulf, seen from the side."""
    fill_rect(s, x, y, w, h, SKY)
    for yy in (y + h - 10, y + h - 5):
        hline(s, x + 6, yy, w - 12, TEAL)
    vline(s, x + w - 70, y + 6, 18, INK)
    fill_rect(s, x + w - 70, y + 6, 16, 8, RED)
    fill_rect(s, x + 30, y + 22, w - 60, 18, NAVY)
    for px in (x + 70, x + 130, x + 190, x + 250, x + 310):
        disc(s, px, y + 31, 5, WHITE)


def pic_capitol(s, x, y, w, h):
    """The US Capitol dome, drawn as columns, a base and a dome."""
    fill_rect(s, x, y, w, h, SKY)
    cx = x + w // 2
    disc(s, cx, y + 12, 12, NAVY)
    fill_rect(s, cx - 12, y + 12, 24, 6, NAVY)
    disc(s, cx, y + 2, 3, GOLD)
    for i in range(5):
        col_x = x + 60 + i * 68
        fill_rect(s, col_x, y + 24, 12, 12, NAVY)
    fill_rect(s, x + 50, y + 36, w - 100, 12, NAVY)


def pic_rubble(s, x, y, w, h):
    """Broken blocks of a struck building, with one warning flame."""
    fill_rect(s, x, y, w, h, (200, 200, 200))
    fill_rect(s, x + 20, y + 24, 70, 20, GREY)
    fill_rect(s, x + 110, y + 14, 60, 30, (90, 90, 90))
    fill_rect(s, x + 200, y + 28, 60, 16, GREY)
    tri_up(s, x + 128, y + 2, 24, 12, ORANGE)


def pic_scales(s, x, y, w, h):
    """The scales of justice: a beam on a post, two red pans."""
    fill_rect(s, x, y, w, h, PAPER)
    cx = x + w // 2
    disc(s, cx, y + 4, 4, GOLD)
    vline(s, cx, y + 8, 32, INK)
    hline(s, x + 24, y + 12, w - 48, INK)
    tri_down(s, x + 24, y + 14, 36, 12, RED)
    tri_down(s, x + w - 60, y + 14, 36, 12, RED)
    fill_rect(s, cx - 14, y + 40, 28, 4, INK)


PICTURES = {
    "globe": pic_globe,
    "tanker": pic_tanker,
    "capitol": pic_capitol,
    "rubble": pic_rubble,
    "scales": pic_scales,
}


# Each panel: x, y, w, h, kicker, headline, deck, picture name,
# headline scale, deck scale, layout ("side" puts the picture on the
# right, "top" puts a picture strip above the text).
PANELS = [
    (24, 134, 976, 258, "COP31 - ANTALYA, TURKEY", "CLIMATE TALKS COLLAPSE",
     "AFTER TWO WEEKS OF TALKS AND TWO DAYS OF OVERTIME, THE ANTALYA "
     "PACT WAS REJECTED ON SUNDAY. NO OVERARCHING DEAL. THE FINAL TEXT "
     "NEVER MENTIONED COAL, OIL OR GAS. THE EU AND 100+ COUNTRIES HAD "
     "PUSHED FOR FOSSIL-FUEL WORDING. THE LONGEST COP EVER.",
     "globe", 5, 2, "side"),
    (24, 404, 480, 248, "THE GULF", "GULF ON EDGE",
     "TRUMP MAY RESUME STRIKES AFTER THE NEW YEAR IF NO DEAL IS "
     "REACHED. IRAN STRUCK US PATRIOT RADARS IN BAHRAIN. A CIVILIAN "
     "PLANT BURNED, 2 INJURED. TANKERS HIT NEAR HORMUZ.",
     "tanker", 3, 2, "top"),
    (520, 404, 480, 248, "WASHINGTON", "DEMOCRATS WIN BIG",
     "DEMOCRATS CLINCHED AT LEAST 258 SEATS, THE LARGEST HOUSE "
     "MAJORITY THIS CENTURY. IN NORTH CAROLINA, HUBBARD BEAT FOXX BY "
     "UNDER 300 VOTES.",
     "capitol", 3, 2, "top"),
    (24, 664, 314, 266, "", "BOY, 7, RESCUED",
     "A RUSSIAN STRIKE IN DYMER KILLED 11. DAVYD, 7, WAS PULLED ALIVE "
     "AFTER HOURS UNDER RUBBLE. A WOMAN, 79, WAS ALSO RESCUED.",
     "rubble", 2, 2, "top"),
    (354, 664, 314, 266, "", "MYANMAR GUILTY",
     "THE WORLD COURT RULED 9-6 MYANMAR COMMITTED GENOCIDE AGAINST THE "
     "ROHINGYA. A FIRST IN 80 YEARS. REPARATIONS AND RETURN ORDERED.",
     "scales", 2, 2, "top"),
    (684, 664, 314, 266, "", "ALSO IN BRIEF",
     "- BANTEN: FIRE, 24 DEAD, 30 MISSING\n"
     "- SEATTLE: ICE JET BRIDGE ARRESTS\n"
     "- PIG KIDNEY: 1 YEAR, A RECORD",
     None, 2, 2, "top"),
]


def draw_panel(s, panel):
    (x, y, w, h, kicker, headline, deck,
     picture, hscale, dscale, layout) = panel
    outline_rect(s, x, y, w, h, INK)
    outline_rect(s, x + 1, y + 1, w - 2, h - 2, INK)
    if layout == "side":
        px, py, pw, ph = x + w - 376, y + 16, 360, h - 32
        tx, tw = x + 16, w - 376 - 32
        cy = y + 16
    elif picture:
        px, py, pw, ph = x + 12, y + 12, w - 24, 52
        tx, tw = x + 16, w - 32
        cy = y + 72
    else:
        tx, tw = x + 16, w - 32
        cy = y + 16
    if picture:
        PICTURES[picture](s, px, py, pw, ph)
        outline_rect(s, px, py, pw, ph, INK)
    if kicker:
        draw_text(s, tx, cy, kicker, 1, RED)
        cy += 14
    for ln in wrap_text(headline, tw // (6 * hscale)):
        draw_text(s, tx, cy, ln, hscale, INK)
        cy += 7 * hscale + 6
    cy += 6
    dmax = tw // (6 * dscale)
    for para in deck.split("\n"):
        for ln in wrap_text(para, dmax):
            draw_text(s, tx, cy, ln, dscale, INK)
            cy += 7 * dscale + 2
        cy += 4


def main():
    s = new_surface(1024, 1024, PAPER)
    outline_rect(s, 8, 8, 1008, 1008, INK)
    outline_rect(s, 10, 10, 1004, 1004, INK)
    draw_text(s, 212, 26, "THE WORLD IN ONE DAY", 5, INK)
    fill_rect(s, 24, 74, 976, 4, RED)
    fill_rect(s, 24, 88, 976, 34, RED)
    draw_text(s, 368, 99, "MONDAY 23 NOVEMBER 2026", 2, WHITE)
    for panel in PANELS:
        draw_panel(s, panel)
    draw_text(s, 404, 946, "23 NOVEMBER 2026 - THE DAY IN BRIEF", 1, INK)
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out, exist_ok=True)
    save_png(os.path.join(out, "entry.png"), s)


if __name__ == "__main__":
    main()
