import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (250, 247, 240)
INK = (32, 38, 48)
MUTED = (96, 104, 116)
NAVY = (24, 48, 84)
RED = (178, 58, 48)
TEAL = (20, 112, 116)
AMBER = (217, 154, 38)
GREEN = (46, 125, 79)
PURPLE = (104, 72, 148)
LINE = (214, 208, 194)
CARD = (255, 255, 255)

# Six verified stories of Thursday 26 November 2026, each first reported or
# occurring that day: (category, headline, one-sentence summary, accent).
NEWS = [
    ("TRADE", "BEIJING REJECTS NEW US TARIFFS",
     "China firmly opposed proposed US Section 301 tariffs on 14 economies and urged talks instead.", NAVY),
    ("MARKETS", "SEOUL HIKES, ASIA STOCKS REBOUND",
     "The Bank of Korea raised rates to 3.25% as Asian shares rebounded and the AI trade steadied.", TEAL),
    ("MIDDLE EAST", "TWO ITALIANS KILLED IN KUWAIT",
     "Kuwait and Italy blamed Iranian drones for an attack that killed two technicians, which Tehran denied.", RED),
    ("NORTH KOREA", "KIM ORDERS WIDER NUCLEAR USE",
     "KCNA said Kim Jong Un urged wider tactical nuclear deployment and more nuclear material output.", PURPLE),
    ("SPACE", "CHINA LAUNCHES YAOGAN-49",
     "A Long March-2D rocket put the Yaogan-49 01 remote sensing satellite group into orbit from Xichang.", GREEN),
    ("DIPLOMACY", "CHINA AND RUSSIA HOLD TALKS",
     "Chinese and Russian militaries pledged closer coordination to safeguard regional security by video.", AMBER),
]

pixels = bytearray(W * H * 3)


def set_px(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        pixels[i:i + 3] = bytes(color)


def rect(x0, y0, x1, y1, color):
    for y in range(max(0, y0), min(H, y1)):
        base = y * W * 3
        for x in range(max(0, x0), min(W, x1)):
            i = base + x * 3
            pixels[i:i + 3] = bytes(color)


FONT = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    "D": ["11100", "10010", "10001", "10001", "10001", "10010", "11100"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
    "J": ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "10101", "01010"],
    "X": ["10001", "01010", "00100", "00100", "00100", "01010", "10001"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00110", "01000", "10000", "11111"],
    "3": ["11110", "00001", "00001", "01110", "00001", "00001", "11110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    "6": ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    ".": ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    ",": ["00000", "00000", "00000", "00000", "01100", "01100", "00100"],
    "-": ["00000", "00000", "00000", "01110", "00000", "00000", "00000"],
    "'": ["00100", "00100", "01000", "00000", "00000", "00000", "00000"],
    ":": ["00000", "01100", "01100", "00000", "01100", "01100", "00000"],
    "%": ["11001", "11010", "00010", "00100", "01000", "01011", "10011"],
    "$": ["00100", "01111", "10100", "01110", "00101", "11110", "00100"],
    " ": ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
}


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def draw_text(text, x, y, scale, color):
    for ch in text:
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            for col in range(5):
                if glyph[row][col] == "1":
                    rect(x + col * scale, y + row * scale,
                         x + (col + 1) * scale, y + (row + 1) * scale, color)
        x += 6 * scale


def draw_centered(text, cx, y, scale, color):
    draw_text(text, cx - text_width(text, scale) // 2, y, scale, color)


def wrap(text, scale, max_width):
    words = text.upper().split()
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if text_width(trial, scale) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_card(x, y, w, h, item):
    category, headline, summary, accent = item
    rect(x, y, x + w, y + h, CARD)
    rect(x, y, x + w, y + 8, accent)
    rect(x, y + h - 2, x + w, y + h, LINE)
    rect(x, y, x + 2, y + h, LINE)
    rect(x + w - 2, y, x + w, y + h, LINE)
    draw_text(category, x + 22, y + 24, 3, accent)
    hy = y + 62
    for line in wrap(headline, 4, w - 44)[:3]:
        draw_text(line, x + 22, hy, 4, INK)
        hy += 36
    rect(x + 22, hy + 2, x + 86, hy + 6, accent)
    sy = hy + 16
    for line in wrap(summary, 2, w - 44)[:4]:
        draw_text(line, x + 22, sy, 2, MUTED)
        sy += 20


def draw_scene():
    rect(0, 0, W, H, PAPER)
    rect(0, 0, W, 150, NAVY)
    draw_centered("26 NOVEMBER 2026", W // 2, 34, 8, (255, 255, 255))
    draw_centered("THE WORLD IN ONE IMAGE", W // 2, 104, 3, (190, 205, 225))
    margin = 36
    gap = 20
    card_w = (W - margin * 2 - gap) // 2
    card_h = 252
    top = 176
    for i, item in enumerate(NEWS):
        col = i % 2
        row = i // 2
        x = margin + col * (card_w + gap)
        y = top + row * (card_h + gap)
        draw_card(x, y, card_w, card_h, item)
    draw_centered("SIX STORIES THAT MADE THE DAY", W // 2, H - 44, 3, MUTED)


def write_png(path):
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw.extend(pixels[y * W * 3:(y + 1) * W * 3])

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


def main():
    assert W <= 1024 and H <= 1024
    assert len(NEWS) == 6
    draw_scene()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    write_png(path)
    os.chmod(path, 0o644)
    assert os.path.getsize(path) <= 1048576


if __name__ == "__main__":
    main()
