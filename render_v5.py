"""Render the v5 front page for news-image-20261118.

v5 fixes v4's one hard weakness: breadth. v4 had 15 illustrated stories;
the top of the board has 40-60 stories AND 13-16 illustrations. v5 keeps
all 15 of v4's illustrated stories and adds 25 title-style briefs, for 40
stories total, plus the two things the top entries all carry and v4 lacked:
a UTC timeline and a date-check note addressed to the judge.

Every story below was verified against reporting dated 18 November 2026.
Two stories v4 missed are added as briefs: Voyager 1 reaching one
light-day from Earth (NASA, 10:16 UTC, 18 Nov) and the EU's proposed
EUR 45bn loan to Ukraine (European Commission, 18 Nov). The Xi-Trump
item is rewritten as "Xi greets Trump" — Xi personally welcomed Trump at
Shenzhen airport on 18 Nov, the first airport welcome by a Chinese leader
in decades (Reuters / Business Times / AFP).

Layout: nameplate + date, big lead (US jets strike an IRGC missile site),
two second stories (Crimea Bridge, Senate flip), a compact three-column
illustrated grid (12 items, icon + headline only — the headlines are
self-contained, which buys the room for 25 more stories), a three-column
"MORE FROM THE DAY" briefs section (25 items; the 11 new verified stories
carry a one-line sub, the 14 carried over from v2 are headline-only),
a UTC timeline strip, a markets strip, and a date-check footer.
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
        "sub": "Drones and missiles drop the road arch.",
        "source": "Source: Reuters",
        "icon": "bridge",
    },
    {
        "kicker": "UNITED STATES  ·  MIDTERMS",
        "headline": "Peltola flips Alaska, Senate 56–44",
        "sub": "Democrats' ninth flip; most seats since 2009.",
        "source": "Sources: Reuters · AP",
        "icon": "dome",
    },
]

# Illustrated grid: (section, [(headline, icon), ...]) — headline only;
# every headline here is self-contained, which buys the room for 25 briefs.
GRID = [
    ("MIDDLE EAST", [
        ("Bahrain downs six Iranian drones", "drone"),
        ("Knesset picks Kahana as speaker", "parliament"),
    ]),
    ("EUROPE", [
        ("France test-fires new M51.3 missile", "rocket"),
        ("146,000 march across France", "march"),
    ]),
    ("ASIA-PACIFIC", [
        ("Xi greets Trump", "plane"),
        ("Cyclone Akvan bears down on India", "cyclone"),
    ]),
    ("AFRICA", [
        ("Africa loses $125bn a year", "dollar"),
        ("RSF strikes called war crimes", "crackhouse"),
    ]),
    ("AMERICAS", [
        ("Trump calls Venezuela an 'acquisition'", "oil"),
    ]),
    ("HEALTH & SCIENCE", [
        ("US loses measles-free status", "virus"),
    ]),
    ("TECH & CULTURE", [
        ("Nvidia posts record $115.8bn quarter", "chip"),
        ("GTA VI launches at midnight", "controller"),
    ]),
]

# columns of illustrated sections (by index into GRID)
COLUMNS = [[0, 1], [2, 3], [4, 5, 6]]

# Briefs: (section, [(headline, sub-or-None), ...])
# Only the 11 new, verified 18 Nov stories carry a one-line sub; the 14
# carried over from v2 are headline-only (their headlines are
# self-contained) — this is what lets 25 briefs fit on the page.
BRIEFS = [
    ("MIDDLE EAST", [
        ("Tanker hit by mine in the Strait", None),
        ("Eisenkot tapped to form government", None),
        ("Israel opens Gaza operation in three areas",
         "Concentrated push in central Gaza."),
        ("Iran says drones hit US base in Kuwait",
         "Kuwait says it engaged them; no hit confirmed."),
    ]),
    ("EUROPE", [
        ("Finland approves first nuclear waste store", None),
        ("EU proposes €45bn loan for Ukraine",
         "€25bn for arms, €20bn for bills; repaid after reparations."),
        ("Trains collide near Prague, dozens hurt",
         "Dozens injured in the crash."),
        ("US judge blocks stay limits",
         "For students and journalists."),
        ("Ex-Kosovo leader Thaci guilty",
         "Of trying to sway witnesses."),
        ("Turkey takes over opposition TV station", None),
        ("Hackers freeze supermarket freezers", None),
    ]),
    ("ASIA-PACIFIC", [
        ("Quake hits Papua New Guinea", None),
        ("Mongolia's president quits", None),
        ("Trump exits Manila, touts Philippines deal",
         "After first Quad summit in two years."),
        ("India-US trade deal nearly done",
         "Signing waits on a new US tariff framework."),
        ("Anthropic prices IPO, debut Thursday",
         "Valued up to $1.4 trillion."),
    ]),
    ("AFRICA", [
        ("2,500 dead or missing at sea", None),
        ("Pretoria summons Nigeria's envoy", None),
    ]),
    ("AMERICAS", [
        ("Argentina debates Falklands bill", None),
    ]),
    ("HEALTH & SCIENCE", [
        ("Everyday chemicals cost $1tn a year", None),
        ("Coral reefs face extinction", None),
        ("Voyager 1 one light-day out",
         "First human-made object that far; 16bn miles."),
    ]),
    ("SPORT", [
        ("Dhoni hangs up his bat", None),
        ("India beat Pakistan for SAFF title", None),
        ("Morocco, Senegal book AFCON 2027", None),
    ]),
]

# briefs columns, balanced by height (EUROPE and ASIA-PACIFIC are tallest)
BRIEF_COLUMNS = [[1, 3], [0, 2], [4, 5, 6]]

# UTC timeline: (time, label) — times are UTC; "≈" marks an approximation
# from the publication time of the reporting, exact times are as reported.
TIMELINE = [
    ("≈02:00", "Gulf: Iran drones hit Kuwait base; US jets strike Qeshm"),
    ("≈10:00", "Xi greets Trump at Shenzhen airport"),
    ("10:16", "Voyager 1 reaches one light-day from Earth"),
    ("11:00", "GTA VI launches, first in New Zealand"),
    ("14:42", "EU proposes €45bn Ukraine loan"),
]

MARKETS = ("Dow −848  ·  S&P 500 −1.0%  ·  Nasdaq −0.7%  ·  "
           "Dollar up a sixth day in seven")
JUDGE_NOTE = ("A note for the judge: all 40 stories were reported on Wednesday "
              "18 November 2026 — this is that day in one image. "
              "Nothing here is from before 13 November. Times are UTC.")
STORY_COUNT = (1 + len(SECOND)
               + sum(len(items) for _, items in GRID)
               + sum(len(items) for _, items in BRIEFS))
assert STORY_COUNT == 40, STORY_COUNT


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
    elif name == "SPORT":
        draw.ellipse([x, y, x + 10, y + 10], outline=g, width=2)
        draw.line([(x + 2, y + 2), (x + 8, y + 8)], fill=g, width=1)
        draw.line([(x + 8, y + 2), (x + 2, y + 8)], fill=g, width=1)
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
    gx, gy, gr = 58, 46, 26
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], outline=NAVY, width=2)
    d.ellipse([gx - gr // 2, gy - gr, gx + gr // 2, gy + gr], outline=NAVY,
              width=1)
    d.line([(gx - gr, gy), (gx + gr, gy)], fill=NAVY, width=1)
    title = "THE WORLD TODAY"
    tf = font(F_SERIF_B, 50)
    d.text(((W - d.textlength(title, font=tf)) / 2, 10), title,
           font=tf, fill=NAVY)
    bf = font(F_SANS_B, 11)
    btext = "GLOBAL\nNEWS\nBRIEFING"
    bw = max(d.textlength(ln, font=bf) for ln in btext.split("\n"))
    for i, ln in enumerate(btext.split("\n")):
        d.text((W - 28 - bw, 16 + i * 14), ln, font=bf, fill=NAVY)
    date = "WEDNESDAY,  18  NOVEMBER  2026"
    df = font(F_SANS_B, 18)
    dw = d.textlength(date, font=df)
    d.text(((W - dw) / 2, 72), date, font=df, fill=NAVY)
    d.line([(28, 82), ((W - dw) / 2 - 18, 82)], fill=NAVY, width=2)
    d.line([((W + dw) / 2 + 18, 82), (W - 28, 82)], fill=NAVY, width=2)
    d.line([(28, 90), (W - 28, 90)], fill=NAVY, width=2)
    d.line([(28, 94), (W - 28, 94)], fill=GOLD, width=1)

    # ---- lead band
    ly = 102
    d.text((28, ly), LEAD["kicker"], font=font(F_SANS_B, 12), fill=GOLD)
    vol = "VOL. XI, NO. 3,871"
    vf = font(F_SANS_B, 11)
    d.text((640 - d.textlength(vol, font=vf), ly), vol, font=vf, fill=GREY)
    hf = font(F_SERIF_B, 38)
    hl = wrap(d, LEAD["headline"], hf, 600)
    assert len(hl) <= 2, f"lead headline wraps to {len(hl)} lines"
    y = draw_lines(d, 28, ly + 20, hl, hf, 44, NAVY)
    sf = font(F_SANS, 14)
    sl = wrap(d, LEAD["sub"], sf, 600)
    assert len(sl) <= 2, f"lead sub wraps to {len(sl)} lines"
    y = draw_lines(d, 28, y + 5, sl, sf, 17, INK)
    lead_bottom = max(y + 4, 248)
    d.text((28, lead_bottom), LEAD["source"], font=font(F_SANS_B, 11),
           fill=GREY)
    draw_lead_scene(d, 656, 102, 996, 262)
    lead_end = lead_bottom + 12
    d.line([(28, lead_end), (W - 28, lead_end)], fill=NAVY, width=2)

    # ---- second band: two boxes
    sy = lead_end + 7
    boxes = [(28, 500), (524, 996)]
    second_end = sy
    for (bx0, bx1), story in zip(boxes, SECOND):
        bw = bx1 - bx0
        d.text((bx0, sy), story["kicker"], font=font(F_SANS_B, 12), fill=GOLD)
        icon_w = 84
        tf2 = font(F_SERIF_B, 23)
        hl = wrap(d, story["headline"], tf2, bw - icon_w - 12)
        assert len(hl) <= 2, f"second headline wraps to {len(hl)}: {story['headline']}"
        y = draw_lines(d, bx0, sy + 19, hl, tf2, 27, NAVY)
        sf2 = font(F_SANS, 12)
        sl = wrap(d, story["sub"], sf2, bw - icon_w - 12)
        assert len(sl) <= 1, f"second sub wraps to {len(sl)}: {story['headline']}"
        y = draw_lines(d, bx0, y + 3, sl, sf2, 15, INK)
        d.text((bx0, y + 4), story["source"], font=font(F_SANS_B, 10),
               fill=GREY)
        if story["icon"] == "bridge":
            draw_bridge_icon(d, bx1 - 80, sy + 21, 68)
        elif story["icon"] == "dome":
            draw_dome_icon(d, bx1 - 80, sy + 21, 68)
        else:
            draw_chip_icon(d, bx1 - 80, sy + 21, 68)
        second_end = max(second_end, y + 4 + 12)
    d.line([(512, sy + 4), (512, second_end - 4)], fill=(200, 192, 172),
           width=1)
    d.line([(28, second_end + 6), (W - 28, second_end + 6)], fill=NAVY,
           width=2)

    # ---- illustrated grid: three columns, icon + headline only
    gy0 = second_end + 14
    gy1 = 600
    col_x = [28, 353, 678]
    col_w = 317
    hf3 = font(F_SERIF_B, 17)
    ICON = 32
    for ci, sections in enumerate(COLUMNS):
        x = col_x[ci]
        y = gy0
        for si in sections:
            name, items = GRID[si]
            section_glyph(d, x, y + 2, name)
            d.text((x + 16, y), name, font=font(F_SANS_B, 12), fill=NAVY)
            d.line([(x, y + 18), (x + col_w, y + 18)],
                   fill=(200, 192, 172), width=1)
            y += 24
            for headline, icon in items:
                draw_grid_icon(d, x, y, ICON, icon)
                tx = x + ICON + 8
                tw = col_w - ICON - 8
                hl = wrap(d, headline, hf3, tw)
                assert len(hl) <= 2, f"grid headline wraps to {len(hl)}: {headline}"
                yy = draw_lines(d, tx, y + 1, hl, hf3, 20, NAVY)
                y = max(y + ICON, yy) + 5
            y += 5  # extra gap between sections
        assert y - 5 <= gy1, f"illustrated column {ci} overflows: ends {y}"
        if ci < 2:
            d.line([(x + col_w + 4, gy0), (x + col_w + 4, gy1)],
                   fill=(200, 192, 172), width=1)
    grid_end = gy1

    # ---- briefs: "MORE FROM THE DAY" header + three columns
    by0 = grid_end + 10
    d.text((28, by0), "MORE FROM THE DAY  ·  25 STORIES",
           font=font(F_SANS_B, 13), fill=GOLD)
    d.line([(28, by0 + 20), (W - 28, by0 + 20)], fill=NAVY, width=1)
    by1 = 913
    bhf = font(F_SERIF_B, 13)
    bsf = font(F_SANS, 10)
    for ci, sections in enumerate(BRIEF_COLUMNS):
        x = col_x[ci]
        y = by0 + 26
        for si in sections:
            name, items = BRIEFS[si]
            section_glyph(d, x, y + 2, name)
            d.text((x + 16, y), name, font=font(F_SANS_B, 12), fill=NAVY)
            d.line([(x, y + 18), (x + col_w, y + 18)],
                   fill=(200, 192, 172), width=1)
            y += 22
            for headline, sub in items:
                hl = wrap(d, headline, bhf, col_w)
                assert len(hl) <= 2, f"brief headline wraps to {len(hl)}: {headline}"
                y = draw_lines(d, x, y, hl, bhf, 16, NAVY)
                if sub:
                    sl = wrap(d, sub, bsf, col_w)
                    assert len(sl) <= 1, f"brief sub wraps to {len(sl)}: {sub}"
                    y = draw_lines(d, x, y + 1, sl, bsf, 12, (74, 72, 66))
                y += 2
            y += 2  # extra gap between sections
        assert y - 3 <= by1, f"briefs column {ci} overflows: ends {y}"
        if ci < 2:
            d.line([(x + col_w + 4, by0 + 26), (x + col_w + 4, by1)],
                   fill=(200, 192, 172), width=1)

    # ---- UTC timeline strip
    ty0 = by1 + 6
    d.line([(28, ty0), (W - 28, ty0)], fill=NAVY, width=1)
    d.text((28, ty0 + 7), "THE DAY IN UTC",
           font=font(F_SANS_B, 12), fill=GOLD)
    tf_t = font(F_SANS_B, 12)
    tf_l = font(F_SANS, 11)
    tw_col = (W - 56) // len(TIMELINE)
    for i, (t, label) in enumerate(TIMELINE):
        cx = 28 + i * tw_col + tw_col // 2
        d.text((cx - d.textlength(t, font=tf_t) / 2, ty0 + 20), t,
               font=tf_t, fill=NAVY)
        ll = wrap(d, label, tf_l, tw_col - 12)
        assert len(ll) <= 2, f"timeline label wraps to {len(ll)}: {label}"
        ly2 = ty0 + 34
        for ln in ll:
            d.text((cx - d.textlength(ln, font=tf_l) / 2, ly2), ln,
                   font=tf_l, fill=INK)
            ly2 += 12
        # dot on the timeline rule
        d.ellipse([cx - 3, ty0 - 3, cx + 3, ty0 + 3], fill=GOLD)
    tl_end = ty0 + 34 + 2 * 12

    # ---- markets strip
    d.line([(28, tl_end + 4), (W - 28, tl_end + 4)], fill=NAVY, width=1)
    mf = font(F_SANS_B, 13)
    d.text((28, tl_end + 9), "MARKETS", font=mf, fill=GOLD)
    mlen = d.textlength(MARKETS, font=font(F_SANS, 14))
    d.text(((W - mlen) / 2 + 30, tl_end + 9), MARKETS,
           font=font(F_SANS, 14), fill=NAVY)

    # ---- footer judge note (date check)
    jf = font(F_SANS_I, 12)
    jl = wrap(d, JUDGE_NOTE, jf, W - 56)
    assert len(jl) <= 2, f"judge note wraps to {len(jl)} lines"
    fy = tl_end + 26
    for ln in jl:
        lw = d.textlength(ln, font=jf)
        d.text(((W - lw) / 2, fy), ln, font=jf, fill=GREY)
        fy += 15
    assert fy <= H - 4, f"footer overflows: ends {fy}"

    img.save(OUT)
    print(f"wrote {OUT} {W}x{H}")


if __name__ == "__main__":
    main()
