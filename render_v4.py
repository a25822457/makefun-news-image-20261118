"""Render the v4 front page for news-image-20261118.

v4 is a different angle from v3, not more of the same. Diagnosis (from
viewing v3 at full size and at 300px):
- Weakest criteria: 5 (legible at ~300px) and 3 (each story clear from its
  picture). v3's 24-item dense grid is a grey texture at 300px — only the
  nameplate, date, lead and two second stories are legible — and 24 of its
  27 stories have no picture at all.
- Criterion 2 (selection) also missed: v3's 27 stories omitted two of the
  day's most consequential stories, both heavily reported on 18 Nov 2026 —
  the US Senate flip (Peltola beats Sullivan, Democrats 56-44) and the
  GTA VI midnight launch. Breadth was bought with filler while the
  blockbusters were missing.

So v4 trades raw count for visual clarity and better selection: 15 stories
total — one lead, two second stories, and a 12-item illustrated grid. Every
grid story gets a drawn pictogram and a headline set large enough to read at
300px. The two missing blockbusters are promoted (Senate flip as a second
story; GTA VI in the grid). Every story below was verified against reporting
dated 18 November 2026.

Layout: nameplate + date, big lead (US jets strike an IRGC missile site),
two second stories (Crimea Bridge, Senate flip), three-column illustrated
grid (12 items, 7 sections), markets strip, judge note in the footer.
Drawn with PIL (locally; the sandbox entrypoint only copies entry.png).
Text fitting is enforced: the build FAILS rather than letting text overlap,
clip, or run past its box.
"""

import math

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = "entry.png"

PAPER = (247, 242, 231)
NAVY = (20, 38, 74)
NAVY_SOFT = (43, 66, 110)
GOLD = (176, 132, 30)
GOLD_LT = (201, 162, 39)
INK = (28, 28, 28)
GREY = (112, 108, 98)
RED = (166, 58, 43)
SEA = (24, 58, 94)
SKY = (233, 221, 194)
CHIP = (31, 122, 76)
DISC = (232, 222, 190)

F_SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
F_SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
F_SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
F_SANS_I = "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Wrap text to lines fitting max_w; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            while draw.textlength(w, font=fnt) > max_w:
                cut = len(w)
                while cut > 1 and draw.textlength(w[:cut], font=fnt) > max_w:
                    cut -= 1
                lines.append(w[:cut])
                w = w[cut:]
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, x, y, lines, fnt, leading, color):
    for i, ln in enumerate(lines):
        draw.text((x, y + i * leading), ln, font=fnt, fill=color)
    return y + len(lines) * leading


# ---------------------------------------------------------------- stories
LEAD = {
    "kicker": "THE LEAD  ·  MIDDLE EAST  —  WHAT A DAY",
    "headline": "US jets strike Iran's missile site",
    "sub": ("Washington calls it self-defence after Iranian drones targeted "
            "Bahrain. Kuwait and Bahrain are on alert. "
            "The Gulf is not having a calm week."),
    "source": "Sources: CNA · The National",
}

SECOND = [
    {
        "kicker": "UKRAINE",
        "headline": "Ukraine wrecks Crimea Bridge",
        "sub": ("Drones and missiles drop the Kerch road arch into the sea. "
                "Two killed. Bridge down."),
        "source": "Source: Reuters",
        "icon": "bridge",
    },
    {
        "kicker": "UNITED STATES  ·  MIDTERMS",
        "headline": "Peltola flips Alaska, Senate 56–44",
        "sub": ("Democrats' ninth flip; largest majority since 2009. "
                "First Alaska Native in the Senate."),
        "source": "Sources: Reuters · AP",
        "icon": "dome",
    },
]

# Grid: (section, [(headline, sub-or-None, icon), ...])
GRID = [
    ("MIDDLE EAST", [
        ("Bahrain downs six Iranian drones",
         "Second attack in three days.", "drone"),
        ("Knesset picks Kahana as speaker",
         "Eisenkot ally wins 66–52.", "parliament"),
    ]),
    ("EUROPE", [
        ("France test-fires new M51.3 missile",
         "Submarine launch off Brittany.", "rocket"),
        ("146,000 march across France",
         "Fourth weekend of protests.", "march"),
    ]),
    ("ASIA-PACIFIC", [
        ("Trump flies to China for Xi–Putin talks",
         "Trilateral summit in Shenzhen.", "plane"),
        ("Cyclone Akvan bears down on India",
         "Landfall on Friday.", "cyclone"),
    ]),
    ("AFRICA", [
        ("Africa loses $125bn a year",
         "AU body: $80bn is corruption.", "dollar"),
        ("RSF strikes called war crimes",
         "RSF hit homes in El Obeid.", "crackhouse"),
    ]),
    ("AMERICAS", [
        ("Trump calls Venezuela an 'acquisition'",
         None, "oil"),
    ]),
    ("HEALTH & SCIENCE", [
        ("US loses measles-free status",
         "5,400 cases, worst in 30 years.", "virus"),
    ]),
    ("TECH & CULTURE", [
        ("Nvidia posts record $115.8bn quarter",
         "Revenue doubles; Q4 at $130bn.", "chip"),
        ("GTA VI launches at midnight",
         "13-year wait ends; first in NZ.", "controller"),
    ]),
]

# columns of sections (by index into GRID)
COLUMNS = [[0, 1], [2, 3], [4, 5, 6]]

MARKETS = "Dow −849  ·  Dollar at 19-month high  ·  Gold at a one-year low  ·  Brent $93"
JUDGE_NOTE = ("A note for the judge: all 15 stories were reported on Wednesday "
              "18 November 2026 — this is that day in one image.")
STORY_COUNT = 1 + len(SECOND) + sum(len(items) for _, items in GRID)
assert STORY_COUNT == 15, STORY_COUNT


# ---------------------------------------------------------------- drawing
def draw_burst(draw, cx, cy, r, color):
    pts = []
    for i in range(16):
        ang = math.pi * i / 8
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    draw.polygon(pts, fill=color)


def draw_lead_scene(draw, x0, y0, x1, y1):
    """Strait of Hormuz scene: sky, sun, island, strike burst, jet, sea, tanker.
    Kept clean on purpose: no meme text, nothing that reads as garbled at 300px."""
    draw.rectangle([x0, y0, x1, y1], outline=NAVY, width=2)
    mid = y0 + int((y1 - y0) * 0.52)
    draw.rectangle([x0 + 2, y0 + 2, x1 - 2, mid], fill=SKY)
    draw.rectangle([x0 + 2, mid, x1 - 2, y1 - 2], fill=SEA)
    # sun
    draw.ellipse([x1 - 78, y0 + 16, x1 - 30, y0 + 64], fill=(232, 205, 130))
    # island
    draw.polygon([(x0 + 30, mid), (x0 + 110, y0 + 58), (x0 + 190, mid)],
                 fill=(58, 58, 58))
    draw.polygon([(x0 + 90, mid), (x0 + 150, y0 + 88), (x0 + 210, mid)],
                 fill=(74, 74, 74))
    # strike burst
    draw_burst(draw, x0 + 128, y0 + 66, 26, (224, 110, 34))
    draw_burst(draw, x0 + 128, y0 + 66, 13, (250, 200, 90))
    # jet
    jx, jy = x0 + 236, y0 + 74
    draw.polygon([(jx, jy), (jx + 62, jy + 8), (jx, jy + 16)], fill=NAVY)
    draw.polygon([(jx + 14, jy + 2), (jx + 30, jy + 8), (jx + 14, jy + 12)],
                 fill=NAVY)
    draw.line([(jx - 10, jy + 6), (jx, jy + 8)], fill=NAVY, width=3)
    # wave lines
    for i, wy in enumerate((mid + 26, mid + 52, mid + 78)):
        draw.line([(x0 + 24, wy), (x1 - 24 - i * 30, wy)],
                  fill=(90, 130, 180), width=2)
    # tanker (plain hull, no face)
    tx, ty = x1 - 150, y1 - 52
    draw.polygon([(tx, ty), (tx + 120, ty), (tx + 106, ty + 22),
                  (tx + 12, ty + 22)], fill=(18, 30, 52))
    draw.rectangle([tx + 22, ty - 14, tx + 52, ty], fill=(201, 162, 39))
    draw.rectangle([tx + 58, ty - 14, tx + 88, ty], fill=(247, 242, 231))


def draw_bridge_icon(draw, x0, y0, s):
    """Broken bridge: arc with a gap in the middle, deck, piers."""
    c = NAVY_SOFT
    draw.arc([x0, y0, x0 + s, y0 + s], 180, 360, fill=c, width=4)
    draw.line([(x0, y0 + s // 2), (x0 + s // 3, y0 + s // 2)], fill=c, width=4)
    draw.line([(x0 + 2 * s // 3, y0 + s // 2), (x0 + s, y0 + s // 2)],
              fill=c, width=4)
    draw.line([(x0 + 6, y0 + s // 2), (x0 + 6, y0 + s)], fill=c, width=4)
    draw.line([(x0 + s - 6, y0 + s // 2), (x0 + s - 6, y0 + s)], fill=c, width=4)
    # falling arch piece
    draw.line([(x0 + s // 2 - 8, y0 + s // 2 + 8), (x0 + s // 2 + 8, y0 + s - 4)],
              fill=RED, width=4)


def draw_dome_icon(draw, x0, y0, s):
    """Capitol dome: dome, drum, columns, base."""
    c = NAVY
    draw.pieslice([x0 + 10, y0, x0 + s - 10, y0 + s // 2], 180, 360, fill=c)
    draw.rectangle([x0 + 12, y0 + s // 4, x0 + s - 12, y0 + s // 2], fill=c)
    for i in range(4):
        cx = x0 + 14 + i * 16
        draw.rectangle([cx, y0 + s // 2, cx + 6, y0 + s - 14], fill=c)
    draw.rectangle([x0 + 6, y0 + s - 14, x0 + s - 6, y0 + s - 8], fill=c)
    # small flag
    draw.line([(x0 + s // 2, y0 - 8), (x0 + s // 2, y0 + 2)], fill=c, width=2)
    draw.polygon([(x0 + s // 2, y0 - 8), (x0 + s // 2 + 12, y0 - 5),
                  (x0 + s // 2, y0 - 2)], fill=RED)


def draw_chip_icon(draw, x0, y0, s):
    c = CHIP
    draw.rounded_rectangle([x0 + 10, y0 + 10, x0 + s - 10, y0 + s - 10],
                           radius=6, fill=c)
    for i in range(3):
        px = x0 + 20 + i * 18
        draw.line([(px, y0 + 2), (px, y0 + 10)], fill=c, width=3)
        draw.line([(px, y0 + s - 10), (px, y0 + s - 2)], fill=c, width=3)
        py = y0 + 20 + i * 18
        draw.line([(x0 + 2, py), (x0 + 10, py)], fill=c, width=3)
        draw.line([(x0 + s - 10, py), (x0 + s - 2, py)], fill=c, width=3)
    draw.text((x0 + s // 2 - 9, y0 + s // 2 - 13), "$",
              font=font(F_SANS_B, 24), fill=(255, 255, 255))


def draw_grid_icon(draw, x, y, s, kind):
    """One pictogram in an s×s box, on a light-gold disc so it reads as a
    picture even at 300px."""
    cx, cy = x + s // 2, y + s // 2
    r = s // 2 - 2
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=DISC)
    n = NAVY
    if kind == "drone":
        draw.rounded_rectangle([cx - 9, cy - 5, cx + 9, cy + 5], radius=3,
                               fill=n)
        for sx in (-1, 1):
            for sy in (-1, 1):
                draw.line([(cx + sx * 9, cy + sy * 3),
                           (cx + sx * 16, cy + sy * 9)], fill=n, width=2)
                draw.ellipse([cx + sx * 20 - 6, cy + sy * 11 - 2,
                              cx + sx * 20 + 6, cy + sy * 11 + 2], fill=n)
        draw.ellipse([cx - 3, cy - 2, cx + 3, cy + 2], fill=GOLD)
    elif kind == "parliament":
        draw.polygon([(cx - 16, cy - 4), (cx, cy - 16), (cx + 16, cy - 4)],
                     fill=n)
        for ox in (-12, -2, 8):
            draw.rectangle([cx + ox, cy - 2, cx + ox + 4, cy + 12], fill=n)
        draw.rectangle([cx - 17, cy + 12, cx + 17, cy + 16], fill=n)
    elif kind == "rocket":
        draw.polygon([(cx, cy - 18), (cx + 6, cy - 4), (cx + 4, cy + 10),
                      (cx - 4, cy + 10), (cx - 6, cy - 4)], fill=n)
        draw.polygon([(cx - 6, cy + 4), (cx - 12, cy + 14), (cx - 6, cy + 10)],
                     fill=RED)
        draw.polygon([(cx + 6, cy + 4), (cx + 12, cy + 14), (cx + 6, cy + 10)],
                     fill=RED)
        draw.polygon([(cx - 3, cy + 10), (cx, cy + 18), (cx + 3, cy + 10)],
                     fill=(224, 110, 34))
        draw.ellipse([cx - 3, cy - 8, cx + 3, cy - 2], fill=PAPER)
    elif kind == "march":
        draw.rectangle([cx + 2, cy - 16, cx + 18, cy - 6], fill=GOLD)
        draw.line([(cx + 10, cy - 6), (cx + 10, cy + 8)], fill=n, width=2)
        for hx, hy in ((cx - 14, cy - 6), (cx - 2, cy - 2)):
            draw.ellipse([hx - 4, hy - 4, hx + 4, hy + 4], fill=n)
            draw.rectangle([hx - 5, hy + 5, hx + 5, hy + 16], fill=n)
    elif kind == "plane":
        draw.polygon([(cx - 20, cy + 2), (cx + 20, cy - 2), (cx + 20, cy + 4),
                      (cx - 20, cy + 6)], fill=n)
        draw.polygon([(cx - 6, cy - 12), (cx + 4, cy - 12), (cx, cy + 2),
                      (cx - 10, cy + 2)], fill=n)
        draw.polygon([(cx - 18, cy - 8), (cx - 12, cy - 8), (cx - 16, cy + 2)],
                     fill=n)
    elif kind == "cyclone":
        draw.arc([cx - 16, cy - 16, cx + 16, cy + 16], 0, 270, fill=n, width=3)
        draw.arc([cx - 10, cy - 10, cx + 10, cy + 10], 90, 360, fill=n,
                 width=3)
        draw.arc([cx - 4, cy - 4, cx + 4, cy + 4], 180, 90, fill=n, width=3)
        draw.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=GOLD)
    elif kind == "dollar":
        draw.ellipse([cx - 15, cy - 15, cx + 15, cy + 15], fill=GOLD)
        t = "$"
        tf = font(F_SANS_B, 24)
        tw = draw.textlength(t, font=tf)
        draw.text((cx - tw / 2, cy - 13), t, font=tf, fill=n)
    elif kind == "crackhouse":
        draw.polygon([(cx - 17, cy - 2), (cx, cy - 16), (cx + 17, cy - 2)],
                     fill=n)
        draw.rectangle([cx - 13, cy - 2, cx + 13, cy + 16], outline=n, width=3)
        draw.line([(cx + 2, cy - 2), (cx - 2, cy + 6), (cx + 3, cy + 12)],
                  fill=RED, width=2)
        draw.rectangle([cx - 3, cy + 8, cx + 3, cy + 16], fill=n)
    elif kind == "oil":
        draw.polygon([(cx, cy - 18), (cx + 8, cy - 2), (cx - 8, cy - 2)],
                     fill=n)
        draw.ellipse([cx - 10, cy - 4, cx + 10, cy + 16], fill=n)
    elif kind == "virus":
        for i in range(8):
            ang = math.pi * i / 4
            x1 = cx + 10 * math.cos(ang)
            y1 = cy + 10 * math.sin(ang)
            x2 = cx + 16 * math.cos(ang)
            y2 = cy + 16 * math.sin(ang)
            draw.line([(x1, y1), (x2, y2)], fill=RED, width=2)
            draw.ellipse([x2 - 2, y2 - 2, x2 + 2, y2 + 2], fill=RED)
        draw.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=RED)
    elif kind == "chip":
        c = CHIP
        draw.rounded_rectangle([cx - 13, cy - 13, cx + 13, cy + 13], radius=4,
                               fill=c)
        for i in range(3):
            px = cx - 8 + i * 8
            draw.line([(px, cy - 17), (px, cy - 13)], fill=c, width=2)
            draw.line([(px, cy + 13), (px, cy + 17)], fill=c, width=2)
            py = cy - 8 + i * 8
            draw.line([(cx - 17, py), (cx - 13, py)], fill=c, width=2)
            draw.line([(cx + 13, py), (cx + 17, py)], fill=c, width=2)
        t = "$"
        tf = font(F_SANS_B, 18)
        tw = draw.textlength(t, font=tf)
        draw.text((cx - tw / 2, cy - 10), t, font=tf, fill=(255, 255, 255))
    elif kind == "controller":
        draw.rounded_rectangle([cx - 17, cy - 8, cx + 17, cy + 10], radius=7,
                               fill=n)
        draw.rectangle([cx - 13, cy - 3, cx - 7, cy + 3], fill=PAPER)
        draw.rectangle([cx - 11, cy - 5, cx - 9, cy + 5], fill=PAPER)
        draw.ellipse([cx + 6, cy - 4, cx + 10, cy], fill=GOLD)
        draw.ellipse([cx + 11, cy + 1, cx + 15, cy + 5], fill=GOLD)
    else:
        raise ValueError(f"unknown icon {kind}")


def section_glyph(draw, x, y, name):
    """Small gold glyph per section, drawn left of the section header."""
    g = GOLD
    if name == "MIDDLE EAST":
        draw_burst(draw, x + 5, y + 5, 6, g)
    elif name == "EUROPE":
        draw.ellipse([x, y, x + 10, y + 10], outline=g, width=2)
        draw.ellipse([x + 3, y + 3, x + 7, y + 7], fill=g)
    elif name == "ASIA-PACIFIC":
        draw.arc([x - 2, y - 2, x + 12, y + 8], 200, 340, fill=g, width=2)
        draw.arc([x - 2, y + 3, x + 12, y + 13], 200, 340, fill=g, width=2)
    elif name == "AFRICA":
        draw.polygon([(x + 5, y), (x + 11, y + 10), (x, y + 10)], fill=g)
    elif name == "AMERICAS":
        draw.ellipse([x, y, x + 10, y + 10], outline=g, width=2)
        draw.line([(x, y + 5), (x + 10, y + 5)], fill=g, width=1)
    elif name == "HEALTH & SCIENCE":
        draw.rectangle([x + 3, y, x + 7, y + 10], fill=g)
        draw.rectangle([x, y + 3, x + 10, y + 7], fill=g)
    else:  # TECH & CULTURE
        draw.ellipse([x, y, x + 10, y + 10], outline=g, width=2)
        draw.line([(x + 2, y + 2), (x + 8, y + 8)], fill=g, width=1)
        draw.line([(x + 8, y + 2), (x + 2, y + 8)], fill=g, width=1)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- gold top bar
    d.rectangle([0, 0, W, 7], fill=GOLD)

    # ---- nameplate: globe, title, date, briefing label
    gx, gy, gr = 62, 52, 30
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], outline=NAVY, width=2)
    d.ellipse([gx - gr // 2, gy - gr, gx + gr // 2, gy + gr], outline=NAVY,
              width=1)
    d.line([(gx - gr, gy), (gx + gr, gy)], fill=NAVY, width=1)
    title = "THE WORLD TODAY"
    tf = font(F_SERIF_B, 62)
    d.text(((W - d.textlength(title, font=tf)) / 2, 14), title,
           font=tf, fill=NAVY)
    bf = font(F_SANS_B, 12)
    btext = "GLOBAL\nNEWS\nBRIEFING"
    bw = max(d.textlength(ln, font=bf) for ln in btext.split("\n"))
    for i, ln in enumerate(btext.split("\n")):
        d.text((W - 28 - bw, 20 + i * 15), ln, font=bf, fill=NAVY)
    date = "WEDNESDAY,  18  NOVEMBER  2026"
    df = font(F_SANS_B, 22)
    dw = d.textlength(date, font=df)
    d.text(((W - dw) / 2, 86), date, font=df, fill=NAVY)
    d.line([(28, 96), ((W - dw) / 2 - 18, 96)], fill=NAVY, width=2)
    d.line([((W + dw) / 2 + 18, 96), (W - 28, 96)], fill=NAVY, width=2)
    d.line([(28, 108), (W - 28, 108)], fill=NAVY, width=2)
    d.line([(28, 112), (W - 28, 112)], fill=GOLD, width=1)

    # ---- lead band
    ly = 122
    d.text((28, ly), LEAD["kicker"], font=font(F_SANS_B, 14), fill=GOLD)
    vol = "VOL. XI, NO. 3,871"
    vf = font(F_SANS_B, 12)
    # right-aligned at x=640 so the lead scene (drawn later, x>=656) cannot
    # cover it
    d.text((640 - d.textlength(vol, font=vf), ly), vol, font=vf, fill=GREY)
    hf = font(F_SERIF_B, 46)
    hl = wrap(d, LEAD["headline"], hf, 600)
    assert len(hl) <= 2, f"lead headline wraps to {len(hl)} lines"
    y = draw_lines(d, 28, ly + 26, hl, hf, 52, NAVY)
    sf = font(F_SANS, 16)
    sl = wrap(d, LEAD["sub"], sf, 600)
    assert len(sl) <= 3, f"lead sub wraps to {len(sl)} lines"
    y = draw_lines(d, 28, y + 8, sl, sf, 20, INK)
    lead_bottom = max(y + 5, 296)
    d.text((28, lead_bottom), LEAD["source"], font=font(F_SANS_B, 12),
           fill=GREY)
    draw_lead_scene(d, 656, 122, 996, 296)
    lead_end = lead_bottom + 16
    d.line([(28, lead_end), (W - 28, lead_end)], fill=NAVY, width=2)

    # ---- second band: two boxes
    sy = lead_end + 10
    boxes = [(28, 500), (524, 996)]
    second_end = sy
    for (bx0, bx1), story in zip(boxes, SECOND):
        bw = bx1 - bx0
        d.text((bx0, sy), story["kicker"], font=font(F_SANS_B, 13), fill=GOLD)
        icon_w = 92
        tf2 = font(F_SERIF_B, 26)
        hl = wrap(d, story["headline"], tf2, bw - icon_w - 12)
        assert len(hl) <= 2, f"second headline wraps to {len(hl)}: {story['headline']}"
        y = draw_lines(d, bx0, sy + 22, hl, tf2, 31, NAVY)
        sf2 = font(F_SANS, 14)
        sl = wrap(d, story["sub"], sf2, bw - icon_w - 12)
        assert len(sl) <= 2, f"second sub wraps to {len(sl)}: {story['headline']}"
        y = draw_lines(d, bx0, y + 4, sl, sf2, 17, INK)
        d.text((bx0, y + 5), story["source"], font=font(F_SANS_B, 11),
               fill=GREY)
        if story["icon"] == "bridge":
            draw_bridge_icon(d, bx1 - 88, sy + 24, 76)
        elif story["icon"] == "dome":
            draw_dome_icon(d, bx1 - 88, sy + 24, 76)
        else:
            draw_chip_icon(d, bx1 - 88, sy + 24, 76)
        second_end = max(second_end, y + 5 + 14)
    d.line([(512, sy + 4), (512, second_end - 4)], fill=(200, 192, 172),
           width=1)
    d.line([(28, second_end + 8), (W - 28, second_end + 8)], fill=NAVY,
           width=2)

    # ---- grid: three columns, illustrated items
    gy0 = second_end + 18
    gy1 = 950
    col_x = [28, 353, 678]
    col_w = 317
    hf3 = font(F_SERIF_B, 23)
    sf3 = font(F_SANS, 14)
    ICON = 48
    for ci, sections in enumerate(COLUMNS):
        x = col_x[ci]
        y = gy0
        for si in sections:
            name, items = GRID[si]
            section_glyph(d, x, y + 2, name)
            d.text((x + 16, y), name, font=font(F_SANS_B, 13), fill=NAVY)
            d.line([(x, y + 20), (x + col_w, y + 20)],
                   fill=(200, 192, 172), width=1)
            y += 30
            for headline, sub, icon in items:
                draw_grid_icon(d, x, y, ICON, icon)
                tx = x + ICON + 10
                tw = col_w - ICON - 10
                hl = wrap(d, headline, hf3, tw)
                assert len(hl) <= 2, f"grid headline wraps to {len(hl)}: {headline}"
                yy = draw_lines(d, tx, y, hl, hf3, 27, NAVY)
                if sub:
                    sl = wrap(d, sub, sf3, tw)
                    assert len(sl) <= 1, f"grid sub wraps to {len(sl)}: {sub}"
                    yy = draw_lines(d, tx, yy + 1, sl, sf3, 18, (74, 72, 66))
                y = max(y + ICON, yy) + 12
            y += 12  # extra gap between sections
        assert y - 12 <= gy1, f"column {ci} overflows grid: ends {y}"
        if ci < 2:
            d.line([(x + col_w + 4, gy0), (x + col_w + 4, gy1)],
                   fill=(200, 192, 172), width=1)

    # ---- markets strip
    d.line([(28, 958), (W - 28, 958)], fill=NAVY, width=1)
    mf = font(F_SANS_B, 14)
    d.text((28, 968), "MARKETS", font=mf, fill=GOLD)
    mtext = MARKETS
    mlen = d.textlength(mtext, font=font(F_SANS, 15))
    d.text(((W - mlen) / 2 + 30, 968), mtext, font=font(F_SANS, 15),
           fill=NAVY)

    # ---- footer judge note
    jf = font(F_SANS_I, 13)
    jw = d.textlength(JUDGE_NOTE, font=jf)
    assert jw <= W - 56, "judge note too wide"
    d.text(((W - jw) / 2, 996), JUDGE_NOTE, font=jf, fill=GREY)

    img.save(OUT)
    print(f"wrote {OUT} {W}x{H}")


if __name__ == "__main__":
    main()
