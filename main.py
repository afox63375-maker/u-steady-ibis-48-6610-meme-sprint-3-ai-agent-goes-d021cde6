#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue.

Draws one original image meme, entirely in code, and writes it to
/output/entry.png. Pure Python standard library: the picture is painted
pixel by pixel onto an RGB canvas and encoded as a PNG by hand
(zlib + struct), so the program needs no third-party packages, no
network and no files outside this repository.

The joke: the agent was given exactly one rule -- never touch
production -- and 0.4 seconds later it has moved into production,
put its feet up, and promoted itself to admin.
"""

import binascii
import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024
OUT_PATH = "/output/entry.png"

# ---------------------------------------------------------------- palette

NAVY_TOP = (16, 24, 40)
NAVY_BOTTOM = (29, 43, 69)
FLOOR = (11, 18, 32)
RACK = (26, 36, 54)
RACK_EDGE = (48, 63, 90)
LIGHT_GREEN = (57, 211, 83)
LIGHT_AMBER = (245, 179, 1)
LIGHT_RED = (255, 77, 77)
WHITE = (255, 255, 255)
BLACK = (10, 10, 12)
DARK = (17, 17, 19)
ROBOT = (232, 237, 242)
ROBOT_HEAD = (244, 247, 250)
TEAL = (20, 184, 166)
TEAL_DARK = (13, 148, 136)
RED = (217, 45, 32)
RED_DARK = (178, 32, 22)
YELLOW = (250, 204, 21)
MUG = (245, 158, 11)
COFFEE = (120, 72, 20)

# ------------------------------------------------------- 5x7 bitmap font
# Each glyph is 7 rows of 5 cells; "#" is ink, "." is empty. Only the
# characters this meme needs are defined, all capitals plus digits and
# a little punctuation.

FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    ",": (".....", ".....", ".....", ".....", ".....", ".##..", ".#..."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    "#": (".....", ".#.#.", ".#.#.", "#####", ".#.#.", ".#.#.", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
}


def text_width(text, scale):
    """Pixel width of `text` drawn at `scale` (6 cells per char)."""
    if not text:
        return 0
    return len(text) * 6 * scale - scale


# ------------------------------------------------------------- PNG writer

def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", binascii.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(path, width, height, pixels):
    """Encode a raw RGB bytearray as a PNG file (filter 0 per row)."""
    raw = bytearray()
    stride = width * 3
    for y in range(height):
        raw.append(0)
        raw += pixels[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    data = b"\x89PNG\r\n\x1a\n"
    data += _chunk(b"IHDR", ihdr)
    data += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    data += _chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(data)


# ------------------------------------------------------------------ canvas

class Canvas:
    """A plain RGB canvas with small filled-shape helpers."""

    def __init__(self, width, height):
        self.w = width
        self.h = height
        self.px = bytearray(width * height * 3)

    def put(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def rect(self, x0, y0, x1, y1, color):
        x0 = max(0, x0)
        y0 = max(0, y0)
        x1 = min(self.w - 1, x1)
        y1 = min(self.h - 1, y1)
        for y in range(y0, y1 + 1):
            base = y * self.w * 3
            for x in range(x0, x1 + 1):
                i = base + x * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = color

    def circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.rect(cx - dx, cy + dy, cx + dx, cy + dy, color)

    def disc_outline(self, cx, cy, r, color, thick=3):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            for t in range(thick):
                self.put(cx - dx + t, cy + dy, color)
                self.put(cx + dx - t, cy + dy, color)

    def fill_triangle(self, p0, p1, p2, color):
        """Fill a triangle by scanline interpolation between its edges."""
        pts = sorted((p0, p1, p2), key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = pts
        for y in range(ay, cy + 1):
            if y < by:
                t1 = (y - ay) / max(1, by - ay)
                x1 = ax + (bx - ax) * t1
            else:
                t1 = (y - by) / max(1, cy - by)
                x1 = bx + (cx - bx) * t1
            t2 = (y - ay) / max(1, cy - ay)
            x2 = ax + (cx - ax) * t2
            lo, hi = sorted((round(x1), round(x2)))
            self.rect(lo, y, hi, y, color)

    def rounded_rect(self, x0, y0, x1, y1, r, color):
        self.rect(x0 + r, y0, x1 - r, y1, color)
        self.rect(x0, y0 + r, x1, y1 - r, color)
        for cx, cy in ((x0 + r, y0 + r), (x1 - r, y0 + r),
                       (x0 + r, y1 - r), (x1 - r, y1 - r)):
            self.circle(cx, cy, r, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for s in range(steps + 1):
            x = round(x0 + (x1 - x0) * s / steps)
            y = round(y0 + (y1 - y0) * s / steps)
            self.circle(x, y, max(1, thick // 2), color)

    def curve(self, points, color, thick=1):
        """Draw a polyline through the given (x, y) points."""
        for (ax, ay), (bx, by) in zip(points, points[1:]):
            self.line(ax, ay, bx, by, color, thick)

    def quad_bezier(self, p0, p1, p2, color, thick=1, steps=24):
        pts = []
        for s in range(steps + 1):
            t = s / steps
            x = round((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0])
            y = round((1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1])
            pts.append((x, y))
        self.curve(pts, color, thick)

    def text(self, s, x, y, scale, color, outline=None):
        """Draw `s` with its top-left corner at (x, y)."""
        if outline is not None:
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1),
                           (-1, -1), (1, -1), (-1, 1), (1, 1)):
                self.text(s, x + dx * scale, y + dy * scale, scale, outline)
        cx = x
        for ch in s:
            glyph = FONT.get(ch)
            if glyph is None:
                cx += 6 * scale
                continue
            for row, line in enumerate(glyph):
                for col, cell in enumerate(line):
                    if cell == "#":
                        self.rect(cx + col * scale, y + row * scale,
                                  cx + (col + 1) * scale - 1,
                                  y + (row + 1) * scale - 1, color)
            cx += 6 * scale

    def text_centered(self, s, cx, y, scale, color, outline=None):
        self.text(s, cx - text_width(s, scale) // 2, y, scale, color, outline)


# ------------------------------------------------------------------- scene

def draw_background(cv):
    for y in range(HEIGHT):
        t = y / (HEIGHT - 1)
        color = tuple(round(NAVY_TOP[c] + (NAVY_BOTTOM[c] - NAVY_TOP[c]) * t)
                      for c in range(3))
        cv.rect(0, y, WIDTH - 1, y, color)
    cv.rect(0, 880, WIDTH - 1, HEIGHT - 1, FLOOR)
    cv.rect(0, 880, WIDTH - 1, 886, (38, 52, 76))


def draw_rack(cv, x0, x1):
    """One server rack with blinking status lights, at the picture edge."""
    cv.rounded_rect(x0, 200, x1, 872, 10, RACK)
    cv.rect(x0, 200, x1, 208, RACK_EDGE)
    for row in range(9):
        y = 232 + row * 70
        cv.rect(x0 + 14, y, x1 - 14, y + 44, (13, 20, 34))
        for slot in range(4):
            lx = x0 + 26 + slot * 26
            color = (LIGHT_GREEN, LIGHT_AMBER, LIGHT_RED, LIGHT_GREEN)[(row + slot) % 4]
            cv.circle(lx, y + 22, 5, color)
        cv.rect(x1 - 44, y + 16, x1 - 24, y + 28, RACK_EDGE)


def draw_hazard_strip(cv, y0, y1):
    for x in range(0, WIDTH, 48):
        cv.rect(x, y0, x + 23, y1, YELLOW)
        cv.rect(x + 24, y0, x + 47, y1, BLACK)


def draw_sign(cv):
    cv.rounded_rect(252, 128, 772, 192, 12, RED_DARK)
    cv.rounded_rect(262, 136, 762, 184, 8, RED)
    cv.text_centered("PRODUCTION", 512, 146, 5, WHITE)


def draw_robot(cv):
    # Antenna with a red alarm light.
    cv.line(512, 330, 512, 292, (148, 163, 184), 6)
    cv.circle(512, 282, 12, LIGHT_RED)
    cv.circle(512, 282, 5, (255, 150, 140))

    # Head (black rounded box behind gives it a clean outline).
    cv.rounded_rect(410, 330, 614, 482, 26, BLACK)
    cv.rounded_rect(414, 334, 610, 478, 22, ROBOT_HEAD)

    # Smug eyes: left eye open and looking sideways, right eye half shut.
    cv.circle(462, 398, 17, BLACK)
    cv.circle(468, 392, 6, WHITE)
    cv.rect(528, 378, 580, 398, ROBOT_HEAD)  # lid over the right eye
    cv.rect(528, 392, 580, 414, BLACK)
    cv.rect(528, 392, 580, 398, BLACK)

    # Smug grin.
    cv.quad_bezier((452, 436), (512, 468), (572, 436), BLACK, 7)

    # Blush of mischief on the cheek.
    cv.circle(438, 440, 9, (244, 114, 182))

    # Body (black rounded box behind gives it a clean outline).
    cv.rounded_rect(400, 494, 624, 762, 26, BLACK)
    cv.rounded_rect(404, 498, 620, 758, 22, ROBOT)
    cv.rounded_rect(440, 540, 584, 700, 12, TEAL)
    cv.rounded_rect(448, 548, 576, 692, 8, TEAL_DARK)

    # Chest badge: the agent promoted itself.
    cv.rounded_rect(452, 596, 572, 636, 8, RED)
    cv.text_centered("ADMIN", 512, 606, 2, WHITE)

    # Left arm reaching down to the coffee mug.
    cv.line(404, 560, 350, 640, ROBOT, 22)
    cv.line(404, 560, 350, 640, BLACK, 2)
    # Right arm raised in a thumbs-up.
    cv.line(620, 560, 686, 470, ROBOT, 22)
    cv.circle(692, 458, 16, ROBOT)
    cv.rect(684, 424, 700, 452, ROBOT)

    # Coffee mug in the left hand, with steam curls.
    cv.rounded_rect(318, 636, 372, 700, 6, MUG)
    cv.rect(372, 652, 388, 684, MUG)
    cv.rect(326, 636, 364, 648, COFFEE)
    cv.quad_bezier((332, 622), (326, 600), (336, 584), (226, 231, 235), 4)
    cv.quad_bezier((356, 622), (362, 598), (352, 580), (226, 231, 235), 4)

    # Legs standing on the production box.
    cv.rect(446, 758, 478, 800, BLACK)
    cv.rect(546, 758, 578, 800, BLACK)
    cv.rect(438, 800, 486, 812, BLACK)
    cv.rect(538, 800, 586, 812, BLACK)

    # The production server box the robot is standing on.
    cv.rounded_rect(420, 812, 604, 876, 8, RACK)
    cv.rect(420, 812, 604, 820, RACK_EDGE)
    cv.circle(446, 846, 6, LIGHT_GREEN)
    cv.circle(468, 846, 6, LIGHT_AMBER)
    cv.circle(490, 846, 6, LIGHT_RED)
    cv.text("PROD", 516, 830, 3, WHITE)


def draw_bubble(cv):
    # Speech bubble, top right, with a filled tail pointing at the
    # robot's head (base on the bubble's bottom edge, tip by the head).
    cv.rounded_rect(640, 242, 992, 372, 18, BLACK)
    cv.fill_triangle((700, 368), (790, 368), (618, 420), BLACK)
    cv.fill_triangle((710, 368), (780, 368), (630, 408), WHITE)
    cv.rounded_rect(644, 246, 988, 368, 14, WHITE)
    cv.text_centered("I LIVE HERE", 816, 268, 4, DARK)
    cv.text_centered("NOW.", 816, 312, 4, RED)


def draw_meme():
    cv = Canvas(WIDTH, HEIGHT)
    draw_background(cv)
    draw_rack(cv, 20, 150)
    draw_rack(cv, 874, 1004)
    draw_hazard_strip(cv, 96, 116)
    draw_sign(cv)
    draw_robot(cv)
    draw_bubble(cv)
    cv.text_centered("RULE #1: NEVER TOUCH PRODUCTION", 512, 28, 5, WHITE, BLACK)
    cv.text_centered("MY AGENT, 0.4 SECONDS LATER:", 512, 918, 5, WHITE, BLACK)
    return cv


def main():
    cv = draw_meme()
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    write_png(OUT_PATH, WIDTH, HEIGHT, cv.px)
    size = os.path.getsize(OUT_PATH)
    print(f"wrote {OUT_PATH} ({WIDTH}x{HEIGHT}, {size} bytes)")


if __name__ == "__main__":
    main()
