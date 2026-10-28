"""Build the animated SVG assets for the profile README (black / green theme)."""

import json
import math
import random
import re
import sys
from html import escape
from pathlib import Path

OUT = Path(sys.argv[1])
FONT = ("font-family:ui-monospace,SFMono-Regular,'Cascadia Code',Consolas,"
        "'Liberation Mono',Menlo,monospace")
BG = "#000000"
BORDER = "#262c33"
TEXT = "#E6EDF3"
MUTED = "#8B949E"

# The accent follows the time of day; panels stay black. use_theme() switches these globals.
ACCENTS = {
    # accent, dim accent, bright rain head, orbit core fill
    "dawn": ("#F2A65A", "#7A4E1F", "#FFE0B8", "#1A0F05"),
    "day": ("#58A6FF", "#1F4F8A", "#CFE6FF", "#05101F"),
    "sunset": ("#FF8A3D", "#7A3A12", "#FFD2B0", "#1F0B03"),
    "night": ("#3FB950", "#1F6F33", "#B7F7C4", "#03130A"),
}
PHASE, WEATHER, WEATHER_LINE = "night", "clear", None
STATUS, SEASON, PROJECT_UPDATES = None, "autumn", {}
GREEN, DIM_GREEN, HEAD, CORE = ACCENTS["night"]


def fog(width, height, strength):
    """Slow drifting bands of mist."""
    bands = []
    for index, (y, h, duration) in enumerate(((0.45, 0.35, 70), (0.65, 0.4, 50), (0.85, 0.3, 35))):
        bands.append(
            f'<g opacity="{strength * (0.5 + index * 0.25):.2f}">'
            f'<ellipse cx="{width * 0.5}" cy="{height * y:.0f}" rx="{width * 0.9}" ry="{height * h:.0f}" '
            f'fill="url(#mist)"/><ellipse cx="{width * 1.5}" cy="{height * y:.0f}" rx="{width * 0.9}" '
            f'ry="{height * h:.0f}" fill="url(#mist)"/>'
            f'<animateTransform attributeName="transform" type="translate" values="0,0;-{width},0" '
            f'dur="{duration}s" repeatCount="indefinite"/></g>'
        )
    return (
        '<radialGradient id="mist"><stop offset="0" stop-color="#C9D1D9" stop-opacity="0.5"/>'
        '<stop offset="1" stop-color="#C9D1D9" stop-opacity="0"/></radialGradient>' + "".join(bands)
    )


def weather_overlay(width, height):
    """Light rain, snow, fog or storm flicker for panels other than the footer."""
    rng = random.Random(5)
    if WEATHER == "fog":
        return fog(width, height, 0.3)
    if WEATHER in ("rain", "storm"):
        layer = f'<g opacity="0.5">{precipitation(rng, width, height, "rain")}</g>'
    elif WEATHER == "snow":
        layer = f'<g opacity="0.6">{precipitation(rng, width, height, "snow")}</g>'
    else:
        layer = ""
    if WEATHER == "storm":
        layer += (
            f'<rect width="{width}" height="{height}" fill="#FFFFFF" opacity="0">'
            '<animate attributeName="opacity" values="0;0;0.12;0;0.06;0;0" '
            'keyTimes="0;0.7;0.71;0.73;0.75;0.78;1" dur="9s" repeatCount="indefinite"/></rect>'
        )
    return layer


def use_theme(phase, weather, weather_line=None, status=None, season="autumn", project_updates=None):
    global PHASE, WEATHER, WEATHER_LINE, GREEN, DIM_GREEN, HEAD, CORE, STATUS, SEASON, PROJECT_UPDATES
    PHASE, WEATHER, WEATHER_LINE = phase, weather, weather_line
    STATUS, SEASON, PROJECT_UPDATES = status, season, project_updates or {}
    GREEN, DIM_GREEN, HEAD, CORE = ACCENTS[phase]


# Half-width katakana as in the film, plus a few kanji, Greek, Cyrillic and digits.
RAIN_CHARS = ("ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ"
              "日月火水木金土山川雨電光空"
              "λΣΩπ"
              "ЖЯФ"
              "0123456789")


def svg(width, height, label, body):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{label}">\n'
        f"<style>text{{{FONT};white-space:pre}}</style>\n{body}\n</svg>\n"
    )


def rain(width, height, seed, column_gap=18, opacity=0.55):
    """Falling columns of hex characters, faded at the top like digital rain."""
    rng = random.Random(seed)
    parts = [
        '<defs><linearGradient id="drop" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{GREEN}" stop-opacity="0"/>'
        f'<stop offset="0.85" stop-color="{GREEN}" stop-opacity="0.55"/>'
        f'<stop offset="1" stop-color="{HEAD}" stop-opacity="1"/>'
        "</linearGradient></defs>",
        f'<g opacity="{opacity}" font-size="13">',
    ]
    for x in range(8, width, column_gap):
        length = rng.randint(6, 16)
        chars = "".join(rng.choice(RAIN_CHARS) for _ in range(length))
        span = length * 15
        duration = rng.uniform(5, 11)
        delay = rng.uniform(0, duration)
        tspans = "".join(
            f'<tspan x="{x}" dy="15">{c}</tspan>' for c in chars
        )
        parts.append(
            f'<text fill="url(#drop)" transform="translate(0,{-span})">{tspans}'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="0,{-span - 20};0,{height + 20}" dur="{duration:.2f}s" '
            f'begin="-{delay:.2f}s" repeatCount="indefinite"/></text>'
        )
    parts.append("</g>")
    return "\n".join(parts)


GREETINGS = [
    "hello, world", "hallo, welt", "bonjour, le monde", "hola, mundo", "ciao, mondo",
    "olá, mundo", "hallo, wereld", "witaj, świecie", "привет, мир", "こんにちは、世界",
    "你好，世界", "안녕, 세상", "नमस्ते दुनिया", "merhaba, dünya", "γεια σου, κόσμε",
    "hej, världen", "përshëndetje, botë",
]


def header():
    """Matrix rain behind a greeting that cycles through languages, most widely spoken first."""
    width, height = 900, 140
    slot, boot = 2.6, 3.4
    cycle = boot + slot * len(GREETINGS)

    def kt(*seconds):
        return ";".join(f"{min(max(s, 0) / cycle, 1):.4f}" for s in seconds)

    greetings = []
    boot_lines = [("initializing", "..."), ("loading modules", "✓"), ("connection established", "✓")]
    for index, (label, status) in enumerate(boot_lines):
        start = 0.3 + index * 0.8
        greetings.append(
            f'<text x="{width / 2 - 120}" y="{50 + index * 20}" font-size="13" fill="{MUTED}" opacity="0">'
            f'{label} <tspan fill="{GREEN}">{status}</tspan>'
            f'<animate attributeName="opacity" values="0;0;1;1;0;0" '
            f'keyTimes="{kt(0, start, start + 0.05, boot - 0.4, boot - 0.1, cycle)}" '
            f'dur="{cycle:.1f}s" repeatCount="indefinite"/></text>'
        )
    for index, greeting in enumerate(GREETINGS):
        start = boot + index * slot
        times = kt(0, start, start + 0.35, start + slot - 0.35, start + slot, cycle)
        greetings.append(
            f'<g opacity="0">'
            f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="{times}" '
            f'dur="{cycle:.1f}s" repeatCount="indefinite"/>'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="0,6;0,6;0,0;0,0;0,-6;0,-6" keyTimes="{times}" dur="{cycle:.1f}s" repeatCount="indefinite"/>'
            f'<text x="{width / 2}" y="77" text-anchor="middle" font-size="18" fill="{TEXT}">'
            f'<tspan fill="{GREEN}">&gt; </tspan>{escape(greeting)}</text></g>'
        )
    body = "\n".join([
        f'<clipPath id="frame"><rect width="{width}" height="{height}" rx="12"/></clipPath>',
        '<radialGradient id="vignette" cx="0.5" cy="0.5" r="0.6">'
        f'<stop offset="0" stop-color="{BG}" stop-opacity="0.95"/>'
        f'<stop offset="0.55" stop-color="{BG}" stop-opacity="0.6"/>'
        f'<stop offset="1" stop-color="{BG}" stop-opacity="0"/></radialGradient>',
        '<g clip-path="url(#frame)">',
        f'<rect width="{width}" height="{height}" fill="{BG}"/>',
        '<linearGradient id="tint" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{sky_colors()[0]}" stop-opacity="0.7"/>'
        f'<stop offset="0.6" stop-color="{sky_colors()[1]}" stop-opacity="0.6"/>'
        f'<stop offset="1" stop-color="{sky_colors()[2]}" stop-opacity="0.5"/></linearGradient>',
        f'<rect width="{width}" height="{height}" fill="url(#tint)"/>',
        rain(width, height, seed=7, opacity=0.55 if WEATHER == "clear" else 0.35),
        f'<rect width="{width}" height="{height}" fill="url(#vignette)"/>',
        weather_overlay(width, height),
        '<linearGradient id="scan" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{GREEN}" stop-opacity="0"/>'
        f'<stop offset="1" stop-color="{GREEN}" stop-opacity="0.08"/></linearGradient>',
        f'<rect x="0" y="-24" width="{width}" height="24" fill="url(#scan)">'
        f'<animate attributeName="y" values="-24;{height}" dur="7s" repeatCount="indefinite"/></rect>',
        "</g>",
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="12" '
        f'fill="none" stroke="{BORDER}"/>',
        *greetings,
        f'<text x="18" y="{height - 12}" font-size="11" fill="{MUTED}"><tspan fill="{GREEN}">●</tspan> {escape(STATUS)}'
        '<animate attributeName="opacity" values="0.6;1;0.6" dur="4s" repeatCount="indefinite"/></text>'
        if STATUS else "",
    ])
    return svg(width, height, "hello, world in many languages", body)


INTRO = [
    ("cmd", "ls ~/stack"),
    ("out", "languages  web  ai-data  databases  desktop  tools"),
    ("cmd", "cat ~/stack/web ~/stack/ai-data"),
    ("out", "react  node.js  flask  material-ui  pwa"),
    ("out", "tensorflow  pytorch  keras  opencv  scikit-learn  pandas"),
    ("cmd", "gti status"),
    ("out", "bash: gti: command not found"),
    ("cmd", "git log --oneline -3"),
    ("log", ("0d2b6f3", "docs: explain the regex nobody understands")),
    ("log", ("e91a4c0", "fix: off-by-one error (the second one)")),
    ("log", ("5c7d2b1", "feat: dark mode, because light attracts bugs")),
    ("fix", ("npm run biuld", "npm run build")),
    ("bar", None),
    ("ok", "✓ built in 1.42s — 0 errors, 0 warnings"),
    ("cmd", "sudo rm -rf /"),
    ("out", "nice try."),
]

# One small command that reacts to the current weather or time of day.
WEATHER_COMMANDS = {
    "rain": ("umbrella --deploy", "ok", "✓ umbrella deployed"),
    "storm": ("ups --status", "ok", "✓ on battery, everything still running"),
    "snow": ("heater --on", "ok", "✓ heater on, the cat approves"),
    "fog": ("fog-lights --on", "ok", "✓ fog lights on"),
    "clouds": ("weather", "out", "cloudy. perfect coding weather."),
    "clear-day": ("sunglasses --on", "ok", "✓ sunglasses on"),
    "clear-night": ("sleep 8h", "out", "bash: sleep: command not found"),
}


def build_session():
    session = list(INTRO)
    if WEATHER_LINE:
        session[2:2] = [("cmd", "weather"), ("out", WEATHER_LINE)]
    key = WEATHER if WEATHER != "clear" else ("clear-night" if PHASE in ("night", "sunset") else "clear-day")
    command, kind, reply = WEATHER_COMMANDS[key]
    session += [("cmd", command), (kind, reply), ("cmd", "cat ~/.pet")]
    session += [("catpad", None)] * 5 + [("cat", None), ("cmd", "clear")]
    return session


CAT_FRAMES = {
    "walk_a": ["", "           /\\_/\\", "  ~(______( o.o )", "    /_/  /_/ >", ""],
    "walk_b": ["", "           /\\_/\\", "  ~(______( o.o )", "     \\_\\  \\_\\>", ""],
    "sit": ["    /\\_/\\", "   ( o.o )", "    > ^ <", "   /     \\", "  (_)_ _(_)~"],
    "sit_tail": ["    /\\_/\\", "   ( o.o )", "    > ^ <", "   /     \\", "  (_)_ _(_)_/"],
    "blink": ["    /\\_/\\", "   ( -.- )", "    > ^ <", "   /     \\", "  (_)_ _(_)~"],
    "look_l": ["    /\\_/\\", "   (o.o  )", "    > ^ <", "   /     \\", "  (_)_ _(_)~"],
    "look_r": ["    /\\_/\\", "   (  o.o)", "    > ^ <", "   /     \\", "  (_)_ _(_)~"],
    "look_up": ["    /\\_/\\", "   ( 'o' )", "    > ^ <", "   /     \\", "  (_)_ _(_)~"],
    "groom_a": ["    /\\_/\\", "   ( ^.^ )/", "    > ^ <", "   /     \\", "  (_)_ _(_)~"],
    "groom_b": ["    /\\_/\\", "   ( ^.- )|", "    > ^ <", "   /     \\", "  (_)_ _(_)-"],
    "yawn": ["    /\\_/\\", "   ( >O< )", "    > ^ <", "   /     \\", "  (_)_ _(_)~"],
    "bat_a": ["    /\\_/\\", "   ( O.O )", "    > ^ <__", "   /     \\", "  (_)_ _(_)~"],
    "bat_b": ["    /\\_/\\", "   ( O.O )", "    > ^ <", "   /     \\_", "  (_)_ _(_)~"],
    "back_a": ["", "    \\_/   \\_/", "     ( ^ω^ )", "   (__\"\"\"\"__)~", ""],
    "back_l": ["    \\_/", "     |    \\_/", "     ( °ω^ )", "   (__\"\"\"\"__)~", ""],
    "back_r": ["          \\_/", "    \\_/    |", "     ( ^ω° )", "   (__\"\"\"\"__)~", ""],
    "startle": ["    /\\_/\\", "   ( O_O )", "   /|^^^|\\", "    |   |", "   _|___|_~"],
    "shiver_a": ["    /\\_/\\", "   ( >.< )", "    > ^ <", "   /|   |\\", "  (_)_ _(_)"],
    "shiver_b": ["     /\\_/\\", "    ( >.< )", "     > ^ <", "    /|   |\\", "   (_)_ _(_)"],
    "loaf": ["", "", "    /\\_/\\____", "   ( ^.^     )~", "    \"\"\"\"\"\"\"\"\"\""],
    "shades_on": ["    /\\_/\\", "   ( o_o)>⌐■-■", "    > ^ <", "   /     \\", "  (_)_ _(_)~"],
    "loaf_shades": ["", "", "    /\\_/\\____", "   (⌐■_■     )~", "    \"\"\"\"\"\"\"\"\"\""],
    "stretch": ["", "                )~", "   /\\_/\\ ______/", "  ( -o- )      |", "   \\_\\_\\     /_/"],
    "knead_a": ["    /\\_/\\", "   ( ^_^ )", "    > ^ <", "   /     \\", "  (_)   _(_)~"],
    "knead_b": ["    /\\_/\\", "   ( ^_^ )", "    > ^ <", "   /     \\", "  (_)_   (_)~"],
    "sleep": ["", "", "    /\\_/\\_____", "   ( -.-       )~", "    (__)---(__)"],
}


def cat_steps():
    """The cat's routine as (frames, seconds, target share of the walkable width, label, jump)."""
    # Each pose flows into the next: lying down before rolling over, stretching before getting up.
    steps = [
        (("walk_a", "walk_b"), 6.0, 0.3, None, False),
        (("sit",), 1.0, None, None, False),
        (("look_l",), 0.7, None, None, False),
        (("look_r",), 0.7, None, None, False),
        (("blink",), 0.2, None, None, False),
        (("sit", "sit_tail"), 1.6, None, None, False),
        (("groom_a", "groom_b"), 4.0, None, None, False),
        (("yawn",), 1.2, None, None, False),
        (("look_r",), 1.4, None, "yarn_in", False),
        (("loaf",), 0.5, None, None, False),
        (("back_a", "back_l", "back_a", "back_r"), 9.6, None, "play", False),
        (("loaf",), 0.5, None, None, False),
        (("look_r",), 1.2, None, "yarn_off", False),
        (("sit", "sit_tail"), 1.0, None, None, False),
        (("look_l", "look_r"), 4.2, None, "bug", False),
        (("bat_a",), 0.5, None, None, False),
        (("sit",), 1.2, None, "bug_gone", False),
    ]
    if WEATHER in ("rain", "storm"):
        steps += [(("look_up", "look_l", "look_up", "look_r"), 6.0, None, "weather", False)]
        if WEATHER == "storm":
            steps += [(("startle",), 1.2, None, "flash", False), (("sit",), 1.0, None, None, False)]
        steps += [(("look_up", "blink"), 5.0, None, None, False)]
    elif WEATHER == "snow":
        steps += [(("walk_a", "walk_b"), 2.0, 0.42, "weather", False),
                  (("shiver_a", "shiver_b"), 4.0, None, None, False),
                  (("loaf",), 8.0, None, "warm", False)]
    elif WEATHER == "clear" and PHASE == "day":
        steps += [(("shades_on",), 1.6, None, "weather", False), (("loaf_shades",), 10.0, None, None, False)]
    else:
        steps += [(("loaf",), 9.0, None, "weather", False)]
    steps += [
        (("stretch",), 2.4, None, None, False),
        (("sit",), 0.6, None, None, False),
        (("knead_a", "knead_b"), 4.0, None, None, False),
        (("loaf",), 0.8, None, None, False),
        (("sleep",), 22.0 if PHASE == "night" else 13.0, None, "sleep", False),
        (("loaf",), 0.8, None, None, False),
        (("stretch",), 1.6, None, None, False),
        (("sit", "sit_tail"), 1.2, None, None, False),
        (("walk_a", "walk_b"), 5.0, 1.0, None, False),
    ]
    return steps


def cat_duration():
    return sum(step[1] for step in cat_steps())


def cat_show(start, y, left, width, line_h, kt, cycle, shown):
    """An ASCII cat that lives in the terminal for well over a minute and reacts to the weather."""
    distance = width - 240
    frames = {name: [] for name in CAT_FRAMES}
    labels = {}
    moves = [(start, 0.0, 0.0)]
    positions = {}
    t, x = start, 0.0
    for names, seconds, target, label, jump in cat_steps():
        if label:
            labels[label] = t
            positions[label] = x
        flip = (0.6 if names[0].startswith("look") else 0.25 if names[0].startswith("walk")
                else 0.08 if names[0].startswith("shiver") else 0.5 if names[0] == "sit" else 0.3)
        moment, index = t, 0
        while moment < t + seconds - 1e-6:
            frames[names[index % len(names)]].append((moment, min(moment + flip, t + seconds)))
            moment, index = moment + flip, index + 1
        if target is not None:
            if jump:
                moves.append((t + seconds / 2, (x + target * distance) / 2, -22.0))
            x = target * distance
            moves.append((t + seconds, x, 0.0))
        t += seconds

    def keyed(points):
        times = [0.0] + [p[0] for p in points] + [cycle]
        values = [f"{points[0][1]:.1f},{points[0][2]:.1f}"] + [f"{px:.1f},{py:.1f}" for _, px, py in points]
        values.append(values[-1])
        return values, times

    def toggles(intervals):
        values, times = ["0"], [0.0]
        for a, b in intervals:
            values += ["1", "0"]
            times += [a, b]
        return (f'<animate attributeName="opacity" calcMode="discrete" values="{";".join(values)}" '
                f'keyTimes="{kt(*times)}" dur="{cycle:.2f}s" repeatCount="indefinite"/>')

    def visible(a, b):
        return (f'<animate attributeName="opacity" values="0;0;1;1;0;0" '
                f'keyTimes="{kt(0, a, a + 0.05, b - 0.05, b, cycle)}" dur="{cycle:.2f}s" repeatCount="indefinite"/>')

    def moving(points, spline=False):
        values, times = keyed(points)
        ease = (f' calcMode="spline" keySplines="{";".join(["0.4 0 0.6 1"] * (len(times) - 1))}"'
                if spline else "")
        return (f'<animateTransform attributeName="transform" type="translate" values="{";".join(values)}" '
                f'keyTimes="{kt(*times)}" dur="{cycle:.2f}s" repeatCount="indefinite"{ease}/>')

    values, times = keyed(moves)
    parts = [f'<g opacity="0">{shown(start)}<g>'
             f'<animateTransform attributeName="transform" type="translate" values="{";".join(values)}" '
             f'keyTimes="{kt(*times)}" dur="{cycle:.2f}s" repeatCount="indefinite"/>']
    for name, rows in CAT_FRAMES.items():
        if not frames[name]:
            continue
        text = "".join(
            f'<text x="{left}" y="{y + i * line_h}" font-size="13" fill="{TEXT}">{escape(row)}</text>'
            for i, row in enumerate(rows) if row
        )
        parts.append(f'<g opacity="0">{toggles(frames[name])}{text}</g>')
    sleep_at = labels["sleep"]
    sleep_len = 22.0 if PHASE == "night" else 13.0
    for i in range(int(sleep_len / 1.6) - 1):
        z_start = sleep_at + 0.6 + i * 1.6
        parts.append(
            f'<text x="{left + 130}" y="{y + 2 * line_h}" font-size="{11 + (i % 3) * 2}" fill="{MUTED}" opacity="0">z'
            f'{visible(z_start, z_start + 1.5)}'
            f'<animateTransform attributeName="transform" type="translate" values="0,0;0,0;10,-26;10,-26" '
            f'keyTimes="{kt(0, z_start, z_start + 1.5, cycle)}" dur="{cycle:.2f}s" repeatCount="indefinite"/></text>'
        )
    if "warm" in labels or labels.get("weather") and WEATHER not in ("rain", "storm", "snow"):
        at = labels.get("warm", labels["weather"])
        parts.append(
            f'<text x="{left + 140}" y="{y + line_h + 6}" font-size="11" fill="{MUTED}" opacity="0">purr...'
            f'{visible(at + 1, at + 7)}</text>'
        )
    # A ball of yarn rolls up, the cat rolls onto its back and juggles it with its paws, then lets it roll away.
    # It is drawn inside the cat's group, so its position is relative to the cat and lines up with the paws.
    here = positions["yarn_in"]
    yarn_y = y + 4 * line_h
    play, off = labels["play"], labels["yarn_off"]
    # One spot per paw pose, in step with the frames: centre, up at the left paw, centre, up at the right paw.
    spots = [(left + 52, -3 * line_h - 12), (left + 30, -4 * line_h - 10),
             (left + 52, -3 * line_h - 24), (left + 76, -4 * line_h - 10)]
    yarn = [(labels["yarn_in"], width - 60 - here, 0), (play - 0.5, left + 110, 0), (play, *spots[0])]
    t, k = play, 0
    while t + 0.3 < off - 0.5:
        t, k = t + 0.3, k + 1
        yarn.append((t, *spots[k % 4]))
    yarn += [(off, left + 110, 0), (off + 1.6, width - 40 - here, 0)]
    parts.append(
        f'<g opacity="0">{visible(labels["yarn_in"], off + 1.6)}{moving(yarn)}'
        f'<text x="0" y="{yarn_y}" font-size="20" font-weight="700" fill="#FF7EB6">@'
        f'<animateTransform attributeName="transform" type="rotate" values="0 6 {yarn_y - 7};360 6 {yarn_y - 7}" '
        f'dur="0.8s" repeatCount="indefinite"/></text></g>'
    )
    parts.append("</g>")

    # A small bug buzzes around the cat's head, gets swatted at and flies off.
    bug_x = positions["bug"] + left
    bug = [
        (labels["bug"], bug_x + 160, y - 4),
        (labels["bug"] + 1.0, bug_x + 40, y + 10),
        (labels["bug"] + 2.0, bug_x + 120, y - 10),
        (labels["bug"] + 3.0, bug_x + 20, y + 4),
        (labels["bug_gone"], bug_x + 70, y - 2),
        (labels["bug_gone"] + 1.6, width - 20, y - 30),
    ]
    parts.append(
        f'<g opacity="0">{visible(labels["bug"], labels["bug_gone"] + 1.6)}{moving(bug, spline=True)}'
        f'<text x="0" y="0" font-size="12" fill="{GREEN}">*'
        '<animate attributeName="opacity" values="1;0.4;1" dur="0.2s" repeatCount="indefinite"/></text></g>'
    )

    # Weather props: raindrops to watch, a lightning flash, a heater, or the sun to bask in.
    at = labels["weather"]
    here = positions["weather"] + left
    if WEATHER in ("rain", "storm"):
        rng = random.Random(9)
        drops = []
        for _ in range(26):
            dx = rng.uniform(-40, 260)
            duration = rng.uniform(0.6, 1.0)
            drops.append(
                f'<line x1="{here + dx:.1f}" y1="{y - 40}" x2="{here + dx - 3:.1f}" y2="{y - 30}" '
                f'stroke="#9CC8EE" stroke-opacity="0.7"><animateTransform attributeName="transform" '
                f'type="translate" values="0,0;-6,{5 * line_h + 30}" dur="{duration:.2f}s" '
                f'begin="-{rng.uniform(0, duration):.2f}s" repeatCount="indefinite"/></line>'
            )
        parts.append(f'<g opacity="0">{visible(at, sleep_at)}{"".join(drops)}</g>')
        if "flash" in labels:
            flash = labels["flash"]
            parts.append(
                f'<rect x="0" y="0" width="{width}" height="{y + 6 * line_h}" fill="#FFFFFF" opacity="0">'
                f'<animate attributeName="opacity" values="0;0;0.25;0;0.12;0;0" '
                f'keyTimes="{kt(0, flash - 0.05, flash, flash + 0.1, flash + 0.2, flash + 0.35, cycle)}" '
                f'dur="{cycle:.2f}s" repeatCount="indefinite"/></rect>'
            )
    elif WEATHER == "snow":
        heater_x = 0.42 * distance + left + 200
        parts.append(
            f'<g opacity="0">{visible(at, sleep_at + 6)}'
            f'<text x="{heater_x:.1f}" y="{y + 3 * line_h}" font-size="13" fill="#FF8A3D">[≡≡≡]</text>'
            f'<text x="{heater_x + 8:.1f}" y="{y + 2 * line_h}" font-size="12" fill="#FF8A3D" opacity="0.6">~ ~ ~'
            '<animate attributeName="opacity" values="0.2;0.8;0.2" dur="1.6s" repeatCount="indefinite"/>'
            '<animateTransform attributeName="transform" type="translate" values="0,4;0,-4" dur="1.6s" '
            'repeatCount="indefinite"/></text></g>'
        )
    elif WEATHER == "clear" and PHASE == "day":
        parts.append(
            f'<g opacity="0">{visible(at, at + 11)}'
            f'<text x="{here + 280:.1f}" y="{y + line_h}" font-size="13" fill="#FFD866">\\ | /</text>'
            f'<text x="{here + 280:.1f}" y="{y + 2 * line_h}" font-size="13" fill="#FFD866">- O -</text>'
            f'<text x="{here + 280:.1f}" y="{y + 3 * line_h}" font-size="13" fill="#FFD866">/ | \\</text></g>'
        )
    parts.append("</g>")
    return "".join(parts)


def terminal():
    """One continuous, scrolling shell session that clears itself and starts again."""
    width, top, left, line_h, char_w = 868, 58, 24, 22, 7.8
    rows = 10
    height = top + line_h * rows - 6
    bar_time, dots_time = 1.6, 1.2
    rng = random.Random(3)
    session = build_session()

    def keystrokes(text):
        return sum(rng.uniform(0.04, 0.12) for _ in text)

    starts, typing, fixes, t = [], [], {}, 0.8
    for index, (kind, content) in enumerate(session):
        if kind in ("cmd", "fix"):
            t += rng.uniform(0.5, 1.4)
            starts.append(t)
            if kind == "cmd":
                duration = keystrokes(content)
            else:
                wrong, right = content
                keep = next(i for i, (a, b) in enumerate(zip(wrong, right)) if a != b)
                typed = keystrokes(wrong)
                erase = (len(wrong) - keep) * 0.07
                retype = keystrokes(right[keep:])
                fixes[index] = (keep, typed, erase, retype)
                duration = typed + 0.35 + erase + retype
            typing.append(duration)
            t += duration + 0.35
        else:
            starts.append(t)
            typing.append(0)
            pause = {"bar": bar_time + 0.2, "dots": dots_time + 0.2, "cat": cat_duration() + 0.3, "catpad": 0.01}
            t += pause.get(kind, rng.uniform(0.12, 0.3))
    cycle = t + 0.6

    def kt(*seconds):
        return ";".join(f"{min(max(s, 0) / cycle, 1):.4f}" for s in seconds)

    def shown(start):
        return (
            f'<animate attributeName="opacity" values="0;0;1;1;0" '
            f'keyTimes="{kt(0, start, start + 0.01, cycle - 0.4, cycle)}" '
            f'dur="{cycle:.2f}s" repeatCount="indefinite"/>'
        )

    scroll_values, scroll_times = ["0,0"], [0.0]
    for index, start in enumerate(starts):
        shift = max(0, index - (rows - 2))
        if shift:
            scroll_values.append(f"0,{-shift * line_h}")
            scroll_times.append(start)
    scroll_values.append(scroll_values[-1])
    scroll_times.append(cycle)

    lines = []
    for index, ((kind, content), start, duration) in enumerate(zip(session, starts, typing)):
        y = top + index * line_h
        if kind == "cmd":
            full = (len(content) + 2) * char_w + 4
            clip = f"c{index}"
            lines.append(
                f'<clipPath id="{clip}"><rect x="{left}" y="{y - 15}" height="{line_h}" width="0">'
                f'<animate attributeName="width" values="0;0;{char_w * 2};{char_w * 2};{full};{full}" '
                f'keyTimes="{kt(0, start - 0.6, start - 0.59, start, start + duration, cycle)}" '
                f'dur="{cycle:.2f}s" repeatCount="indefinite"/></rect></clipPath>'
                f'<g clip-path="url(#{clip})">'
                f'<text x="{left}" y="{y}" font-size="13"><tspan fill="{GREEN}">$</tspan> '
                f'<tspan fill="{TEXT}">{escape(content)}</tspan></text></g>'
            )
            following = starts[index + 1] if index + 1 < len(starts) else cycle
            lines.append(
                f'<rect y="{y - 12}" width="{char_w}" height="15" fill="{GREEN}" opacity="0">'
                f'<animate attributeName="x" values="{left + 2 * char_w};{left + 2 * char_w};'
                f'{left + (len(content) + 2) * char_w};{left + (len(content) + 2) * char_w}" '
                f'keyTimes="{kt(0, start, start + duration, cycle)}" dur="{cycle:.2f}s" repeatCount="indefinite"/>'
                f'<animate attributeName="opacity" values="0;0;1;1;0;0" '
                f'keyTimes="{kt(0, start - 0.6, start - 0.59, following - 0.01, following, cycle)}" '
                f'dur="{cycle:.2f}s" repeatCount="indefinite"/></rect>'
            )
            continue
        if kind == "fix":
            wrong, right = content
            keep, typed, erase, retype = fixes[index]
            t1 = start + typed
            t2 = t1 + 0.35
            t3 = t2 + erase
            t4 = t3 + retype

            def width_at(count):
                return (count + 2) * char_w + 4

            for layer, (text, values, times) in enumerate((
                (wrong, [0, 0, char_w * 2, char_w * 2, width_at(len(wrong)), width_at(len(wrong)),
                         width_at(keep) - 5, width_at(keep) - 5],
                 (0, start - 0.6, start - 0.59, start, t1, t2, t3, cycle)),
                (right, [0, 0, width_at(keep), width_at(len(right)), width_at(len(right))],
                 (0, t3, t3 + 0.01, t4, cycle)),
            )):
                clip = f"c{index}_{layer}"
                lines.append(
                    f'<clipPath id="{clip}"><rect x="{left}" y="{y - 15}" height="{line_h}" width="0">'
                    f'<animate attributeName="width" values="{";".join(f"{v:.1f}" for v in values)}" '
                    f'keyTimes="{kt(*times)}" dur="{cycle:.2f}s" repeatCount="indefinite"/></rect></clipPath>'
                    f'<g clip-path="url(#{clip})">'
                    f'<text x="{left}" y="{y}" font-size="13"><tspan fill="{GREEN}">$</tspan> '
                    f'<tspan fill="{TEXT}">{escape(text)}</tspan></text></g>'
                )
            following = starts[index + 1]
            xs = [left + (n + 2) * char_w for n in (0, 0, len(wrong), len(wrong), keep, len(right), len(right))]
            lines.append(
                f'<rect y="{y - 12}" width="{char_w}" height="15" fill="{GREEN}" opacity="0">'
                f'<animate attributeName="x" values="{";".join(f"{x:.1f}" for x in xs)}" '
                f'keyTimes="{kt(0, start, t1, t2, t3, t4, cycle)}" dur="{cycle:.2f}s" repeatCount="indefinite"/>'
                f'<animate attributeName="opacity" values="0;0;1;1;0;0" '
                f'keyTimes="{kt(0, start - 0.6, start - 0.59, following - 0.01, following, cycle)}" '
                f'dur="{cycle:.2f}s" repeatCount="indefinite"/></rect>'
            )
            continue
        if kind == "dots":
            full = len(content) * char_w + 4
            clip = f"c{index}"
            lines.append(
                f'<clipPath id="{clip}"><rect x="{left}" y="{y - 15}" height="{line_h}" width="0">'
                f'<animate attributeName="width" values="0;0;{full};{full}" '
                f'keyTimes="{kt(0, start, start + dots_time, cycle)}" '
                f'dur="{cycle:.2f}s" repeatCount="indefinite"/></rect></clipPath>'
                f'<text x="{left}" y="{y}" font-size="13" fill="{GREEN}" clip-path="url(#{clip})">{content}</text>'
            )
            continue
        if kind == "catpad":
            continue
        if kind == "cat":
            lines.append(cat_show(start, y - 5 * line_h, left, width, line_h, kt, cycle, shown))
            continue
        if kind == "bar":
            track = 300
            lines.append(
                f'<g opacity="0">{shown(start)}'
                f'<rect x="{left}" y="{y - 10}" width="{track}" height="8" rx="4" fill="#161B22"/>'
                f'<rect x="{left}" y="{y - 10}" height="8" rx="4" fill="{GREEN}" width="0">'
                f'<animate attributeName="width" values="0;0;{track};{track}" '
                f'keyTimes="{kt(0, start, start + bar_time, cycle)}" '
                f'dur="{cycle:.2f}s" repeatCount="indefinite"/></rect></g>'
            )
            continue
        if kind == "blink":
            awake, asleep = (escape(face) for face in content)
            lines.append(
                f'<g opacity="0">{shown(start)}'
                f'<text x="{left}" y="{y}" font-size="13" fill="{TEXT}">{awake}'
                '<animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;0.85;0.86;0.95;1" '
                'dur="3s" repeatCount="indefinite"/></text>'
                f'<text x="{left}" y="{y}" font-size="13" fill="{TEXT}" opacity="0">{asleep}'
                '<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;0.85;0.86;0.95;1" '
                'dur="3s" repeatCount="indefinite"/></text></g>'
            )
            continue
        if kind == "steam":
            lines.append(
                f'<g opacity="0">{shown(start)}'
                f'<text x="{left}" y="{y}" font-size="13" fill="{MUTED}">{escape(content)}'
                '<animate attributeName="opacity" values="0.2;0.9;0.2" dur="2s" repeatCount="indefinite"/>'
                '<animateTransform attributeName="transform" type="translate" values="0,3;0,-3" '
                'dur="2s" repeatCount="indefinite"/></text></g>'
            )
            continue
        if kind == "fetch":
            art, key, value = content
            inner = (
                f'<tspan fill="{GREEN}">{escape(art)}</tspan>   '
                f'<tspan fill="{GREEN}">{key:<10}</tspan><tspan fill="{TEXT}">{escape(value)}</tspan>'
            )
        elif kind == "log":
            sha, message = content
            inner = f'<tspan fill="#D29922">{sha}</tspan>  <tspan fill="{MUTED}">{escape(message)}</tspan>'
        elif kind == "ok":
            inner = f'<tspan fill="{GREEN}">{escape(content)}</tspan>'
        elif kind == "art":
            inner = f'<tspan fill="{TEXT}">{escape(content)}</tspan>'
        else:
            inner = f'<tspan fill="{MUTED}">{escape(content)}</tspan>'
        lines.append(f'<text x="{left}" y="{y}" font-size="13" opacity="0">{inner}{shown(start)}</text>')

    parts = [
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10" '
        f'fill="{BG}" stroke="{BORDER}"/>',
        f'<line x1="0" y1="38" x2="{width}" y2="38" stroke="{BORDER}"/>',
        *(f'<circle cx="{22 + i * 18}" cy="19" r="5.5" fill="{c}"/>'
          for i, c in enumerate(("#FF5F57", "#FEBC2E", "#28C840"))),
        f'<text x="{width / 2}" y="23" text-anchor="middle" fill="{MUTED}" font-size="12">bash — ~/</text>',
        f'<clipPath id="screen"><rect x="0" y="40" width="{width}" height="{height - 44}"/></clipPath>',
        '<g clip-path="url(#screen)"><g>',
        f'<animateTransform attributeName="transform" type="translate" calcMode="discrete" '
        f'values="{";".join(scroll_values)}" keyTimes="{kt(*scroll_times)}" '
        f'dur="{cycle:.2f}s" repeatCount="indefinite"/>',
        *lines,
        "</g></g>",
    ]
    return svg(width, height, "Animated terminal session", "\n".join(parts)), cycle


SKIES = {
    # top, middle, horizon colours; star opacity; cloud colour and strength; jet colour; (sun or moon, x share, glow)
    "dawn": ("#0B1026", "#3B2A4F", "#F28C5B", 0.35, "#F5C6A5", 1.4, "#1F2328", ("sun", 0.92, "#FFB37A")),
    "day": ("#1B4F8A", "#3C7DC4", "#9CC8EE", 0.0, "#FFFFFF", 2.6, "#1F2328", ("sun", 0.25, "#FFF4D6")),
    "sunset": ("#1A1033", "#7A2E5A", "#F59E42", 0.2, "#F8B88B", 1.6, "#1F2328", ("sun", 0.9, "#FF8A3D")),
    "night": (BG, "#03100A", "#0B2A16", 0.7, "#C9D1D9", 1.0, TEXT, ("moon", 0.15, "#E6EDF3")),
}
WEATHERS = ("clear", "clouds", "fog", "rain", "snow", "storm")


def jet(color):
    """Small side-view jet silhouette with a fading contrail, nose pointing right."""
    return (
        '<linearGradient id="trail" x1="0" x2="1">'
        f'<stop offset="0" stop-color="{color}" stop-opacity="0"/>'
        f'<stop offset="1" stop-color="{color}" stop-opacity="0.35"/></linearGradient>'
        '<rect x="-220" y="-1" width="206" height="1.6" rx="0.8" fill="url(#trail)"/>'
        f'<path d="M16 0 L10 -1.6 L-4 -2 L-10 -7 L-14 -7 L-11 -2 L-14 -1.4 L-14 1.4 L-4 1.8 '
        f'L-8 5 L-5 5 L4 1.8 L10 1.6 Z" fill="{color}"/>'
    )


def clouds(rng, count, y_range, scale, opacity, color):
    """A row of soft ellipse clouds, wider than the frame so it can scroll seamlessly."""
    parts = []
    for _ in range(count):
        x = rng.uniform(0, 1800)
        y = rng.uniform(*y_range)
        w = rng.uniform(60, 140) * scale
        for dx, dy, rw in ((0, 0, 1), (w * 0.35, -6 * scale, 0.6), (-w * 0.3, -3 * scale, 0.5)):
            parts.append(
                f'<ellipse cx="{x + dx:.1f}" cy="{y + dy:.1f}" rx="{w * rw:.1f}" ry="{9 * scale * rw + 4:.1f}" '
                f'fill="{color}" opacity="{min(opacity, 0.9):.2f}"/>'
            )
    return "".join(parts)


def precipitation(rng, width, height, kind):
    """Falling rain streaks or snowflakes."""
    parts = []
    for _ in range(90 if kind == "rain" else 70):
        x = rng.uniform(-40, width)
        duration = rng.uniform(0.5, 0.9) if kind == "rain" else rng.uniform(5, 9)
        delay = rng.uniform(0, duration)
        if kind == "rain":
            shape = f'<line x1="{x:.1f}" y1="0" x2="{x - 4:.1f}" y2="12" stroke="#9CC8EE" stroke-opacity="0.45"/>'
            drift = "-12"
        else:
            shape = f'<circle cx="{x:.1f}" cy="0" r="{rng.uniform(1, 2.2):.1f}" fill="#FFFFFF" opacity="0.75"/>'
            drift = f"{rng.uniform(-30, 30):.0f}"
        parts.append(
            f'<g>{shape}<animateTransform attributeName="transform" type="translate" '
            f'values="0,-20;{drift},{height + 10}" dur="{duration:.2f}s" begin="-{delay:.2f}s" '
            f'repeatCount="indefinite"/></g>'
        )
    return "".join(parts)


def sky_colors(phase=None, weather=None):
    """Top, middle and horizon colours of the sky for a time of day and weather."""
    phase, weather = phase or PHASE, weather or WEATHER
    top, middle, horizon = SKIES[phase][:3]
    if weather != "clear" and phase != "night":
        top, middle = "#3A4452", "#5B6676"
    return top, middle, horizon


def seasonal(width, height, phase, weather):
    """Falling leaves in autumn, petals in spring, a light frost sparkle in winter, fireflies on summer nights."""
    rng = random.Random(17)
    parts = []
    if SEASON in ("autumn", "spring"):
        colors = ("#D9822B", "#B5651D", "#E3A857") if SEASON == "autumn" else ("#F7B2C4", "#FAD1DC", "#F48FB1")
        for _ in range(14):
            x = rng.uniform(0, width)
            duration = rng.uniform(7, 12)
            parts.append(
                f'<g><ellipse cx="{x:.0f}" cy="-6" rx="3.2" ry="1.6" fill="{rng.choice(colors)}" opacity="0.85">'
                f'<animateTransform attributeName="transform" type="rotate" values="0 {x:.0f} -6;360 {x:.0f} -6" '
                f'dur="{rng.uniform(2, 4):.1f}s" repeatCount="indefinite"/></ellipse>'
                f'<animateTransform attributeName="transform" type="translate" '
                f'values="0,0;{rng.uniform(-60, -20):.0f},{height / 2:.0f};{rng.uniform(-120, -60):.0f},{height + 12}" '
                f'dur="{duration:.1f}s" begin="-{rng.uniform(0, duration):.1f}s" repeatCount="indefinite"/></g>'
            )
    elif SEASON == "winter" and weather != "snow":
        for _ in range(30):
            parts.append(
                f'<circle cx="{rng.uniform(0, width):.0f}" cy="{rng.uniform(height * 0.55, height):.0f}" r="0.9" '
                f'fill="#FFFFFF"><animate attributeName="opacity" values="0;0.9;0" dur="{rng.uniform(2, 4):.1f}s" '
                f'begin="-{rng.uniform(0, 4):.1f}s" repeatCount="indefinite"/></circle>'
            )
    elif SEASON == "summer" and phase == "night" and weather == "clear":
        for _ in range(16):
            x, y = rng.uniform(0, width), rng.uniform(height * 0.5, height - 10)
            parts.append(
                f'<circle cx="{x:.0f}" cy="{y:.0f}" r="1.6" fill="#E3F57A">'
                f'<animate attributeName="opacity" values="0;1;0" dur="{rng.uniform(1.5, 3):.1f}s" '
                f'begin="-{rng.uniform(0, 3):.1f}s" repeatCount="indefinite"/>'
                f'<animateTransform attributeName="transform" type="translate" values="0,0;{rng.uniform(-12, 12):.0f},'
                f'{rng.uniform(-8, 8):.0f};0,0" dur="{rng.uniform(4, 7):.1f}s" repeatCount="indefinite"/></circle>'
            )
    return "".join(parts)


def footer(phase="night", weather="clear"):
    """Sky above the clouds for a time of day and weather, with drifting cloud layers and a passing jet."""
    width, height = 900, 170
    top, middle, horizon, star_opacity, cloud_color, cloud_strength, jet_color, (kind, x_share, glow) = SKIES[phase]
    rng = random.Random(42)
    overcast = weather != "clear"
    if overcast:
        star_opacity = 0
        cloud_strength *= 2.2
        if phase != "night":
            top, middle = "#3A4452", "#5B6676"
    stars = "".join(
        f'<circle cx="{rng.uniform(0, width):.1f}" cy="{rng.uniform(0, 90):.1f}" '
        f'r="{rng.choice((0.6, 0.9))}" fill="{TEXT}">'
        f'<animate attributeName="opacity" values="{star_opacity * 0.15:.2f};{star_opacity:.2f};'
        f'{star_opacity * 0.15:.2f}" dur="{rng.uniform(2, 5):.1f}s" '
        f'begin="-{rng.uniform(0, 5):.1f}s" repeatCount="indefinite"/></circle>'
        for _ in range(45)
    ) if star_opacity else ""
    far = clouds(rng, 9, (120, 140), 0.7, 0.05 * cloud_strength, cloud_color)
    near = clouds(rng, 7, (150, 170), 1.2, 0.08 * cloud_strength, cloud_color)
    high = clouds(rng, 8, (20, 60), 1.0, 0.07 * cloud_strength, cloud_color) if overcast else ""
    body_x = width * x_share
    body_y = 120 if kind == "sun" and phase != "day" else 45
    celestial = "" if overcast else (
        f'<circle cx="{body_x:.0f}" cy="{body_y}" r="70" fill="url(#halo)"/>'
        f'<circle cx="{body_x:.0f}" cy="{body_y}" r="{14 if kind == "sun" else 10}" fill="{glow}" '
        f'opacity="{0.95 if kind == "sun" else 0.8}"/>'
    )
    weather_layer = ""
    if weather == "fog":
        weather_layer = fog(width, height, 0.55)
    if weather in ("rain", "storm"):
        weather_layer = precipitation(rng, width, height, "rain")
    elif weather == "snow":
        weather_layer = precipitation(rng, width, height, "snow")
    if weather == "storm":
        weather_layer += (
            f'<rect width="{width}" height="{height}" fill="#FFFFFF" opacity="0">'
            '<animate attributeName="opacity" values="0;0;0.35;0;0.2;0;0" '
            'keyTimes="0;0.7;0.71;0.73;0.75;0.78;1" dur="9s" repeatCount="indefinite"/></rect>'
        )
    meteor = (
        '<g transform="rotate(18)" opacity="0">'
        '<rect x="0" y="0" width="90" height="1.4" rx="0.7" fill="url(#meteor)"/>'
        '<animateTransform attributeName="transform" type="translate" additive="sum" '
        'values="120,-40;120,-40;520,-40;520,-40" keyTimes="0;0.6;0.66;1" dur="11s" repeatCount="indefinite"/>'
        '<animate attributeName="opacity" values="0;0;1;0;0" keyTimes="0;0.6;0.62;0.66;1" '
        'dur="11s" repeatCount="indefinite"/></g>'
    ) if phase == "night" and not overcast else ""
    body = "\n".join([
        f'<clipPath id="frame"><rect width="{width}" height="{height}" rx="12"/></clipPath>',
        '<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{top}"/><stop offset="0.6" stop-color="{middle}"/>'
        f'<stop offset="1" stop-color="{horizon}"/></linearGradient>',
        f'<radialGradient id="halo"><stop offset="0" stop-color="{glow}" stop-opacity="0.45"/>'
        f'<stop offset="1" stop-color="{glow}" stop-opacity="0"/></radialGradient>',
        '<linearGradient id="meteor" x1="0" x2="1">'
        f'<stop offset="0" stop-color="{TEXT}" stop-opacity="0"/>'
        f'<stop offset="1" stop-color="{TEXT}"/></linearGradient>',
        '<g clip-path="url(#frame)">',
        f'<rect width="{width}" height="{height}" fill="url(#sky)"/>',
        stars,
        celestial,
        meteor,
        f'<g>{high}<animateTransform attributeName="transform" type="translate" '
        f'values="0,0;-900,0" dur="120s" repeatCount="indefinite"/></g>' if high else "",
        f'<g>{far}<animateTransform attributeName="transform" type="translate" '
        f'values="0,0;-900,0" dur="90s" repeatCount="indefinite"/></g>',
        f'<g>{jet(jet_color)}<animateMotion dur="16s" repeatCount="indefinite" '
        f'path="M -40 110 C 300 95, 600 70, 1150 55" rotate="auto"/></g>',
        f'<g>{near}<animateTransform attributeName="transform" type="translate" '
        f'values="0,0;-900,0" dur="45s" repeatCount="indefinite"/></g>',
        weather_layer,
        seasonal(width, height, phase, weather),
        "</g>",
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="12" fill="none" stroke="{BORDER}"/>',
    ])
    return svg(width, height, f"Sky over Munich: {phase}, {weather}", body)


# Main languages are shown a little stronger than the ones used extensively before.
ORBITS = [
    (150, 38, 24, ["Python", "C", "TypeScript"]),
    (270, 66, 40, ["Java", "PHP", "C++", "Bash"]),
    (390, 94, 60, ["JavaScript", "HTML", "SQL", "CSS"]),
]
MAIN_LANGUAGES = {"Python", "C", "TypeScript", "Java", "C++"}


# Brand logos from Simple Icons (CC0, simpleicons.org), drawn on a 24 x 24 grid.
LOGOS = {
    "Python": "M14.25.18l.9.2.73.26.59.3.45.32.34.34.25.34.16.33.1.3.04.26.02.2-.01.13V8.5l-.05.63-.13.55-.21.46-.26.38-.3.31-.33.25-.35.19-.35.14-.33.1-.3.07-.26.04-.21.02H8.77l-.69.05-.59.14-.5.22-.41.27-.33.32-.27.35-.2.36-.15.37-.1.35-.07.32-.04.27-.02.21v3.06H3.17l-.21-.03-.28-.07-.32-.12-.35-.18-.36-.26-.36-.36-.35-.46-.32-.59-.28-.73-.21-.88-.14-1.05-.05-1.23.06-1.22.16-1.04.24-.87.32-.71.36-.57.4-.44.42-.33.42-.24.4-.16.36-.1.32-.05.24-.01h.16l.06.01h8.16v-.83H6.18l-.01-2.75-.02-.37.05-.34.11-.31.17-.28.25-.26.31-.23.38-.2.44-.18.51-.15.58-.12.64-.1.71-.06.77-.04.84-.02 1.27.05zm-6.3 1.98l-.23.33-.08.41.08.41.23.34.33.22.41.09.41-.09.33-.22.23-.34.08-.41-.08-.41-.23-.33-.33-.22-.41-.09-.41.09zm13.09 3.95l.28.06.32.12.35.18.36.27.36.35.35.47.32.59.28.73.21.88.14 1.04.05 1.23-.06 1.23-.16 1.04-.24.86-.32.71-.36.57-.4.45-.42.33-.42.24-.4.16-.36.09-.32.05-.24.02-.16-.01h-8.22v.82h5.84l.01 2.76.02.36-.05.34-.11.31-.17.29-.25.25-.31.24-.38.2-.44.17-.51.15-.58.13-.64.09-.71.07-.77.04-.84.01-1.27-.04-1.07-.14-.9-.2-.73-.25-.59-.3-.45-.33-.34-.34-.25-.34-.16-.33-.1-.3-.04-.25-.02-.2.01-.13v-5.34l.05-.64.13-.54.21-.46.26-.38.3-.32.33-.24.35-.2.35-.14.33-.1.3-.06.26-.04.21-.02.13-.01h5.84l.69-.05.59-.14.5-.21.41-.28.33-.32.27-.35.2-.36.15-.36.1-.35.07-.32.04-.28.02-.21V6.07h2.09l.14.01zm-6.47 14.25l-.23.33-.08.41.08.41.23.33.33.23.41.08.41-.08.33-.23.23-.33.08-.41-.08-.41-.23-.33-.33-.23-.41-.08-.41.08z",
    "Java": "M11.915 0 11.7.215C9.515 2.4 7.47 6.39 6.046 10.483c-1.064 1.024-3.633 2.81-3.711 3.551-.093.87 1.746 2.611 1.55 3.235-.198.625-1.304 1.408-1.014 1.939.1.188.823.011 1.277-.491a13.389 13.389 0 0 0-.017 2.14c.076.906.27 1.668.643 2.232.372.563.956.911 1.667.911.397 0 .727-.114 1.024-.264.298-.149.571-.33.91-.5.68-.34 1.634-.666 3.53-.604 1.903.062 2.872.39 3.559.704.687.314 1.15.664 1.925.664.767 0 1.395-.336 1.807-.9.412-.563.631-1.33.72-2.24.06-.623.055-1.32 0-2.066.454.45 1.117.604 1.213.424.29-.53-.816-1.314-1.013-1.937-.198-.624 1.642-2.366 1.549-3.236-.08-.748-2.707-2.568-3.748-3.586C16.428 6.374 14.308 2.394 12.13.215zm.175 6.038a2.95 2.95 0 0 1 2.943 2.942 2.95 2.95 0 0 1-2.943 2.943A2.95 2.95 0 0 1 9.148 8.98a2.95 2.95 0 0 1 2.942-2.942zM8.685 7.983a3.515 3.515 0 0 0-.145.997c0 1.951 1.6 3.55 3.55 3.55 1.95 0 3.55-1.598 3.55-3.55 0-.329-.046-.648-.132-.951.334.095.64.208.915.336a42.699 42.699 0 0 1 2.042 5.829c.678 2.545 1.01 4.92.846 6.607-.082.844-.29 1.51-.606 1.94-.315.431-.713.651-1.315.651-.593 0-.932-.27-1.673-.61-.741-.338-1.825-.694-3.792-.758-1.974-.064-3.073.293-3.821.669-.375.188-.659.373-.911.5s-.466.2-.752.2c-.53 0-.876-.209-1.16-.64-.285-.43-.474-1.101-.545-1.948-.141-1.693.176-4.069.823-6.614a43.155 43.155 0 0 1 1.934-5.783c.348-.167.749-.31 1.192-.425zm-3.382 4.362a.216.216 0 0 1 .13.031c-.166.56-.323 1.116-.463 1.665a33.849 33.849 0 0 0-.547 2.555 3.9 3.9 0 0 0-.2-.39c-.58-1.012-.914-1.642-1.16-2.08.315-.24 1.679-1.755 2.24-1.781zm13.394.01c.562.027 1.926 1.543 2.24 1.783-.246.438-.58 1.068-1.16 2.08a4.428 4.428 0 0 0-.163.309 32.354 32.354 0 0 0-.562-2.49 40.579 40.579 0 0 0-.482-1.652.216.216 0 0 1 .127-.03z",
    "TypeScript": "M1.125 0C.502 0 0 .502 0 1.125v21.75C0 23.498.502 24 1.125 24h21.75c.623 0 1.125-.502 1.125-1.125V1.125C24 .502 23.498 0 22.875 0zm17.363 9.75c.612 0 1.154.037 1.627.111a6.38 6.38 0 0 1 1.306.34v2.458a3.95 3.95 0 0 0-.643-.361 5.093 5.093 0 0 0-.717-.26 5.453 5.453 0 0 0-1.426-.2c-.3 0-.573.028-.819.086a2.1 2.1 0 0 0-.623.242c-.17.104-.3.229-.393.374a.888.888 0 0 0-.14.49c0 .196.053.373.156.529.104.156.252.304.443.444s.423.276.696.41c.273.135.582.274.926.416.47.197.892.407 1.266.628.374.222.695.473.963.753.268.279.472.598.614.957.142.359.214.776.214 1.253 0 .657-.125 1.21-.373 1.656a3.033 3.033 0 0 1-1.012 1.085 4.38 4.38 0 0 1-1.487.596c-.566.12-1.163.18-1.79.18a9.916 9.916 0 0 1-1.84-.164 5.544 5.544 0 0 1-1.512-.493v-2.63a5.033 5.033 0 0 0 3.237 1.2c.333 0 .624-.03.872-.09.249-.06.456-.144.623-.25.166-.108.29-.234.373-.38a1.023 1.023 0 0 0-.074-1.089 2.12 2.12 0 0 0-.537-.5 5.597 5.597 0 0 0-.807-.444 27.72 27.72 0 0 0-1.007-.436c-.918-.383-1.602-.852-2.053-1.405-.45-.553-.676-1.222-.676-2.005 0-.614.123-1.141.369-1.582.246-.441.58-.804 1.004-1.089a4.494 4.494 0 0 1 1.47-.629 7.536 7.536 0 0 1 1.77-.201zm-15.113.188h9.563v2.166H9.506v9.646H6.789v-9.646H3.375z",
    "JavaScript": "M0 0h24v24H0V0zm22.034 18.276c-.175-1.095-.888-2.015-3.003-2.873-.736-.345-1.554-.585-1.797-1.14-.091-.33-.105-.51-.046-.705.15-.646.915-.84 1.515-.66.39.12.75.42.976.9 1.034-.676 1.034-.676 1.755-1.125-.27-.42-.404-.601-.586-.78-.63-.705-1.469-1.065-2.834-1.034l-.705.089c-.676.165-1.32.525-1.71 1.005-1.14 1.291-.811 3.541.569 4.471 1.365 1.02 3.361 1.244 3.616 2.205.24 1.17-.87 1.545-1.966 1.41-.811-.18-1.26-.586-1.755-1.336l-1.83 1.051c.21.48.45.689.81 1.109 1.74 1.756 6.09 1.666 6.871-1.004.029-.09.24-.705.074-1.65l.046.067zm-8.983-7.245h-2.248c0 1.938-.009 3.864-.009 5.805 0 1.232.063 2.363-.138 2.711-.33.689-1.18.601-1.566.48-.396-.196-.597-.466-.83-.855-.063-.105-.11-.196-.127-.196l-1.825 1.125c.305.63.75 1.172 1.324 1.517.855.51 2.004.675 3.207.405.783-.226 1.458-.691 1.811-1.411.51-.93.402-2.07.397-3.346.012-2.054 0-4.109 0-6.179l.004-.056z",
    "C": "M16.5921 9.1962s-.354-3.298-3.627-3.39c-3.2741-.09-4.9552 2.474-4.9552 6.14 0 3.6651 1.858 6.5972 5.0451 6.5972 3.184 0 3.5381-3.665 3.5381-3.665l6.1041.365s.36 3.31-2.196 5.836c-2.552 2.5241-5.6901 2.9371-7.8762 2.9201-2.19-.017-5.2261.034-8.1602-2.97-2.938-3.0101-3.436-5.9302-3.436-8.8002 0-2.8701.556-6.6702 4.047-9.5502C7.444.72 9.849 0 12.254 0c10.0422 0 10.7172 9.2602 10.7172 9.2602z",
    "C++": "M22.394 6c-.167-.29-.398-.543-.652-.69L12.926.22c-.509-.294-1.34-.294-1.848 0L2.26 5.31c-.508.293-.923 1.013-.923 1.6v10.18c0 .294.104.62.271.91.167.29.398.543.652.69l8.816 5.09c.508.293 1.34.293 1.848 0l8.816-5.09c.254-.147.485-.4.652-.69.167-.29.27-.616.27-.91V6.91c.003-.294-.1-.62-.268-.91zM12 19.11c-3.92 0-7.109-3.19-7.109-7.11 0-3.92 3.19-7.11 7.11-7.11a7.133 7.133 0 016.156 3.553l-3.076 1.78a3.567 3.567 0 00-3.08-1.78A3.56 3.56 0 008.444 12 3.56 3.56 0 0012 15.555a3.57 3.57 0 003.08-1.778l3.078 1.78A7.135 7.135 0 0112 19.11zm7.11-6.715h-.79v.79h-.79v-.79h-.79v-.79h.79v-.79h.79v.79h.79zm2.962 0h-.79v.79h-.79v-.79h-.79v-.79h.79v-.79h.79v.79h.79z",
    "PHP": "M7.01 10.207h-.944l-.515 2.648h.838c.556 0 .97-.105 1.242-.314.272-.21.455-.559.55-1.049.092-.47.05-.802-.124-.995-.175-.193-.523-.29-1.047-.29zM12 5.688C5.373 5.688 0 8.514 0 12s5.373 6.313 12 6.313S24 15.486 24 12c0-3.486-5.373-6.312-12-6.312zm-3.26 7.451c-.261.25-.575.438-.917.551-.336.108-.765.164-1.285.164H5.357l-.327 1.681H3.652l1.23-6.326h2.65c.797 0 1.378.209 1.744.628.366.418.476 1.002.33 1.752a2.836 2.836 0 0 1-.305.847c-.143.255-.33.49-.561.703zm4.024.715l.543-2.799c.063-.318.039-.536-.068-.651-.107-.116-.336-.174-.687-.174H11.46l-.704 3.625H9.388l1.23-6.327h1.367l-.327 1.682h1.218c.767 0 1.295.134 1.586.401s.378.7.263 1.299l-.572 2.944h-1.389zm7.597-2.265a2.782 2.782 0 0 1-.305.847c-.143.255-.33.49-.561.703a2.44 2.44 0 0 1-.917.551c-.336.108-.765.164-1.286.164h-1.18l-.327 1.682h-1.378l1.23-6.326h2.649c.797 0 1.378.209 1.744.628.366.417.477 1.001.331 1.751zM17.766 10.207h-.943l-.516 2.648h.838c.557 0 .971-.105 1.242-.314.272-.21.455-.559.551-1.049.092-.47.049-.802-.125-.995s-.524-.29-1.047-.29z",
    "SQL": "M23.5594 14.7228a.5269.5269 0 0 0-.0563-.1191c-.139-.2632-.4768-.3418-1.0074-.2321-1.6533.3411-2.2935.1312-2.5256-.0191 1.342-2.0482 2.445-4.522 3.0411-6.8297.2714-1.0507.7982-3.5237.1222-4.7316a1.5641 1.5641 0 0 0-.1509-.235C21.6931.9086 19.8007.0248 17.5099.0005c-1.4947-.0158-2.7705.3461-3.1161.4794a9.449 9.449 0 0 0-.5159-.0816 8.044 8.044 0 0 0-1.3114-.1278c-1.1822-.0184-2.2038.2642-3.0498.8406-.8573-.3211-4.7888-1.645-7.2219.0788C.9359 2.1526.3086 3.8733.4302 6.3043c.0409.818.5069 3.334 1.2423 5.7436.4598 1.5065.9387 2.7019 1.4334 3.582.553.9942 1.1259 1.5933 1.7143 1.7895.4474.1491 1.1327.1441 1.8581-.7279.8012-.9635 1.5903-1.8258 1.9446-2.2069.4351.2355.9064.3625 1.39.3772a.0569.0569 0 0 0 .0004.0041 11.0312 11.0312 0 0 0-.2472.3054c-.3389.4302-.4094.5197-1.5002.7443-.3102.064-1.1344.2339-1.1464.8115-.0025.1224.0329.2309.0919.3268.2269.4231.9216.6097 1.015.6331 1.3345.3335 2.5044.092 3.3714-.6787-.017 2.231.0775 4.4174.3454 5.0874.2212.5529.7618 1.9045 2.4692 1.9043.2505 0 .5263-.0291.8296-.0941 1.7819-.3821 2.5557-1.1696 2.855-2.9059.1503-.8707.4016-2.8753.5388-4.1012.0169-.0703.0357-.1207.057-.1362.0007-.0005.0697-.0471.4272.0307a.3673.3673 0 0 0 .0443.0068l.2539.0223.0149.001c.8468.0384 1.9114-.1426 2.5312-.4308.6438-.2988 1.8057-1.0323 1.5951-1.6698zM2.371 11.8765c-.7435-2.4358-1.1779-4.8851-1.2123-5.5719-.1086-2.1714.4171-3.6829 1.5623-4.4927 1.8367-1.2986 4.8398-.5408 6.108-.13-.0032.0032-.0066.0061-.0098.0094-2.0238 2.044-1.9758 5.536-1.9708 5.7495-.0002.0823.0066.1989.0162.3593.0348.5873.0996 1.6804-.0735 2.9184-.1609 1.1504.1937 2.2764.9728 3.0892.0806.0841.1648.1631.2518.2374-.3468.3714-1.1004 1.1926-1.9025 2.1576-.5677.6825-.9597.5517-1.0886.5087-.3919-.1307-.813-.5871-1.2381-1.3223-.4796-.839-.9635-2.0317-1.4155-3.5126zm6.0072 5.0871c-.1711-.0428-.3271-.1132-.4322-.1772.0889-.0394.2374-.0902.4833-.1409 1.2833-.2641 1.4815-.4506 1.9143-1.0002.0992-.126.2116-.2687.3673-.4426a.3549.3549 0 0 0 .0737-.1298c.1708-.1513.2724-.1099.4369-.0417.156.0646.3078.26.3695.4752.0291.1016.0619.2945-.0452.4444-.9043 1.2658-2.2216 1.2494-3.1676 1.0128zm2.094-3.988-.0525.141c-.133.3566-.2567.6881-.3334 1.003-.6674-.0021-1.3168-.2872-1.8105-.8024-.6279-.6551-.9131-1.5664-.7825-2.5004.1828-1.3079.1153-2.4468.079-3.0586-.005-.0857-.0095-.1607-.0122-.2199.2957-.2621 1.6659-.9962 2.6429-.7724.4459.1022.7176.4057.8305.928.5846 2.7038.0774 3.8307-.3302 4.7363-.084.1866-.1633.3629-.2311.5454zm7.3637 4.5725c-.0169.1768-.0358.376-.0618.5959l-.146.4383a.3547.3547 0 0 0-.0182.1077c-.0059.4747-.054.6489-.115.8693-.0634.2292-.1353.4891-.1794 1.0575-.11 1.4143-.8782 2.2267-2.4172 2.5565-1.5155.3251-1.7843-.4968-2.0212-1.2217a6.5824 6.5824 0 0 0-.0769-.2266c-.2154-.5858-.1911-1.4119-.1574-2.5551.0165-.5612-.0249-1.9013-.3302-2.6462.0044-.2932.0106-.5909.019-.8918a.3529.3529 0 0 0-.0153-.1126 1.4927 1.4927 0 0 0-.0439-.208c-.1226-.4283-.4213-.7866-.7797-.9351-.1424-.059-.4038-.1672-.7178-.0869.067-.276.1831-.5875.309-.9249l.0529-.142c.0595-.16.134-.3257.213-.5012.4265-.9476 1.0106-2.2453.3766-5.1772-.2374-1.0981-1.0304-1.6343-2.2324-1.5098-.7207.0746-1.3799.3654-1.7088.5321a5.6716 5.6716 0 0 0-.1958.1041c.0918-1.1064.4386-3.1741 1.7357-4.4823a4.0306 4.0306 0 0 1 .3033-.276.3532.3532 0 0 0 .1447-.0644c.7524-.5706 1.6945-.8506 2.802-.8325.4091.0067.8017.0339 1.1742.081 1.939.3544 3.2439 1.4468 4.0359 2.3827.8143.9623 1.2552 1.9315 1.4312 2.4543-1.3232-.1346-2.2234.1268-2.6797.779-.9926 1.4189.543 4.1729 1.2811 5.4964.1353.2426.2522.4522.2889.5413.2403.5825.5515.9713.7787 1.2552.0696.087.1372.1714.1885.245-.4008.1155-1.1208.3825-1.0552 1.717-.0123.1563-.0423.4469-.0834.8148-.0461.2077-.0702.4603-.0994.7662zm.8905-1.6211c-.0405-.8316.2691-.9185.5967-1.0105a2.8566 2.8566 0 0 0 .135-.0406 1.202 1.202 0 0 0 .1342.103c.5703.3765 1.5823.4213 3.0068.1344-.2016.1769-.5189.3994-.9533.6011-.4098.1903-1.0957.333-1.7473.3636-.7197.0336-1.0859-.0807-1.1721-.151zm.5695-9.2712c-.0059.3508-.0542.6692-.1054 1.0017-.055.3576-.112.7274-.1264 1.1762-.0142.4368.0404.8909.0932 1.3301.1066.887.216 1.8003-.2075 2.7014a3.5272 3.5272 0 0 1-.1876-.3856c-.0527-.1276-.1669-.3326-.3251-.6162-.6156-1.1041-2.0574-3.6896-1.3193-4.7446.3795-.5427 1.3408-.5661 2.1781-.463zm.2284 7.0137a12.3762 12.3762 0 0 0-.0853-.1074l-.0355-.0444c.7262-1.1995.5842-2.3862.4578-3.4385-.0519-.4318-.1009-.8396-.0885-1.2226.0129-.4061.0666-.7543.1185-1.0911.0639-.415.1288-.8443.1109-1.3505.0134-.0531.0188-.1158.0118-.1902-.0457-.4855-.5999-1.938-1.7294-3.253-.6076-.7073-1.4896-1.4972-2.6889-2.0395.5251-.1066 1.2328-.2035 2.0244-.1859 2.0515.0456 3.6746.8135 4.8242 2.2824a.908.908 0 0 1 .0667.1002c.7231 1.3556-.2762 6.2751-2.9867 10.5405zm-8.8166-6.1162c-.025.1794-.3089.4225-.6211.4225a.5821.5821 0 0 1-.0809-.0056c-.1873-.026-.3765-.144-.5059-.3156-.0458-.0605-.1203-.178-.1055-.2844.0055-.0401.0261-.0985.0925-.1488.1182-.0894.3518-.1226.6096-.0867.3163.0441.6426.1938.6113.4186zm7.9305-.4114c.0111.0792-.049.201-.1531.3102-.0683.0717-.212.1961-.4079.2232a.5456.5456 0 0 1-.075.0052c-.2935 0-.5414-.2344-.5607-.3717-.024-.1765.2641-.3106.5611-.352.297-.0414.6111.0088.6356.1851z",
    "Bash": "M21.038,4.9l-7.577-4.498C13.009,0.134,12.505,0,12,0c-0.505,0-1.009,0.134-1.462,0.403L2.961,4.9 C2.057,5.437,1.5,6.429,1.5,7.503v8.995c0,1.073,0.557,2.066,1.462,2.603l7.577,4.497C10.991,23.866,11.495,24,12,24 c0.505,0,1.009-0.134,1.461-0.402l7.577-4.497c0.904-0.537,1.462-1.529,1.462-2.603V7.503C22.5,6.429,21.943,5.437,21.038,4.9z M15.17,18.946l0.013,0.646c0.001,0.078-0.05,0.167-0.111,0.198l-0.383,0.22c-0.061,0.031-0.111-0.007-0.112-0.085L14.57,19.29 c-0.328,0.136-0.66,0.169-0.872,0.084c-0.04-0.016-0.057-0.075-0.041-0.142l0.139-0.584c0.011-0.046,0.036-0.092,0.069-0.121 c0.012-0.011,0.024-0.02,0.036-0.026c0.022-0.011,0.043-0.014,0.062-0.006c0.229,0.077,0.521,0.041,0.802-0.101 c0.357-0.181,0.596-0.545,0.592-0.907c-0.003-0.328-0.181-0.465-0.613-0.468c-0.55,0.001-1.064-0.107-1.072-0.917 c-0.007-0.667,0.34-1.361,0.889-1.8l-0.007-0.652c-0.001-0.08,0.048-0.168,0.111-0.2l0.37-0.236 c0.061-0.031,0.111,0.007,0.112,0.087l0.006,0.653c0.273-0.109,0.511-0.138,0.726-0.088c0.047,0.012,0.067,0.076,0.048,0.151 l-0.144,0.578c-0.011,0.044-0.036,0.088-0.065,0.116c-0.012,0.012-0.025,0.021-0.038,0.028c-0.019,0.01-0.038,0.013-0.057,0.009 c-0.098-0.022-0.332-0.073-0.699,0.113c-0.385,0.195-0.52,0.53-0.517,0.778c0.003,0.297,0.155,0.387,0.681,0.396 c0.7,0.012,1.003,0.318,1.01,1.023C16.105,17.747,15.736,18.491,15.17,18.946z M19.143,17.859c0,0.06-0.008,0.116-0.058,0.145 l-1.916,1.164c-0.05,0.029-0.09,0.004-0.09-0.056v-0.494c0-0.06,0.037-0.093,0.087-0.122l1.887-1.129 c0.05-0.029,0.09-0.004,0.09,0.056V17.859z M20.459,6.797l-7.168,4.427c-0.894,0.523-1.553,1.109-1.553,2.187v8.833 c0,0.645,0.26,1.063,0.66,1.184c-0.131,0.023-0.264,0.039-0.398,0.039c-0.42,0-0.833-0.114-1.197-0.33L3.226,18.64 c-0.741-0.44-1.201-1.261-1.201-2.142V7.503c0-0.881,0.46-1.702,1.201-2.142l7.577-4.498c0.363-0.216,0.777-0.33,1.197-0.33 c0.419,0,0.833,0.114,1.197,0.33l7.577,4.498c0.624,0.371,1.046,1.013,1.164,1.732C21.686,6.557,21.12,6.411,20.459,6.797z",
    "HTML": "M1.5 0h21l-1.91 21.563L11.977 24l-8.564-2.438L1.5 0zm7.031 9.75l-.232-2.718 10.059.003.23-2.622L5.412 4.41l.698 8.01h9.126l-.326 3.426-2.91.804-2.955-.81-.188-2.11H6.248l.33 4.171L12 19.351l5.379-1.443.744-8.157H8.531z",
    "CSS": "M1.5 0h21l-1.91 21.563L11.977 24l-8.565-2.438L1.5 0zm17.09 4.413L5.41 4.41l.213 2.622 10.125.002-.255 2.716h-6.64l.24 2.573h6.182l-.366 3.523-2.91.804-2.956-.81-.188-2.11h-2.61l.29 3.855L12 19.288l5.373-1.53L18.59 4.414z",
}


def languages():
    """Language logos orbiting a core with depth, booting in with a flicker, one highlighted at a time."""
    width, height = 900, 240
    cx, cy = width / 2, height / 2
    names = [name for *_, ring in ORBITS for name in ring]
    scan_slot = 2.2
    scan_cycle = scan_slot * len(names)
    parts = [
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="12" fill="{BG}" stroke="{BORDER}"/>',
        f'<text x="24" y="30" font-size="11" fill="{MUTED}">LANGUAGES</text>',
    ]
    for rx, ry, *_ in ORBITS:
        parts.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="{GREEN}" '
                     'stroke-opacity="0.32" stroke-width="1.2" stroke-dasharray="3 5"/>')
    parts += [
        f'<radialGradient id="coreglow"><stop offset="0" stop-color="{GREEN}" stop-opacity="0.35"/>'
        f'<stop offset="1" stop-color="{GREEN}" stop-opacity="0"/></radialGradient>',
        f'<circle cx="{cx}" cy="{cy}" r="46" fill="url(#coreglow)">'
        '<animate attributeName="opacity" values="0.5;1;0.5" dur="4s" repeatCount="indefinite"/></circle>',
        f'<circle cx="{cx}" cy="{cy}" r="22" fill="{CORE}" stroke="{GREEN}" stroke-opacity="0.5">'
        f'<animate attributeName="r" values="21;24;21;21" keyTimes="0;0.06;0.2;1" '
        f'dur="{ORBITS[0][2] / len(ORBITS[0][3]):.2f}s" repeatCount="indefinite"/></circle>',
        f'<circle cx="{cx}" cy="{cy}" r="30" fill="none" stroke="{GREEN}" stroke-width="1.5" '
        f'stroke-dasharray="34 60" stroke-linecap="round" opacity="0.8">'
        f'<animateTransform attributeName="transform" type="rotate" values="0 {cx} {cy};360 {cx} {cy}" '
        'dur="9s" repeatCount="indefinite"/></circle>',
        f'<circle cx="{cx}" cy="{cy}" r="35" fill="none" stroke="{GREEN}" stroke-width="1" '
        f'stroke-dasharray="14 40 6 40" stroke-linecap="round" opacity="0.5">'
        f'<animateTransform attributeName="transform" type="rotate" values="360 {cx} {cy};0 {cx} {cy}" '
        'dur="14s" repeatCount="indefinite"/></circle>',
        f'<text x="{cx}" y="{cy + 5}" text-anchor="middle" font-size="14" fill="{GREEN}">&lt;/&gt;'
        '<animate attributeName="opacity" calcMode="discrete" values="1;0;1" keyTimes="0;0.5;1" '
        'dur="8s" repeatCount="indefinite"/></text>',
        f'<g opacity="0"><animate attributeName="opacity" calcMode="discrete" values="0;1;0" keyTimes="0;0.5;1" '
        'dur="8s" repeatCount="indefinite"/>'
        f'<text x="{cx - 9}" y="{cy + 5}" font-size="14" fill="{GREEN}">&gt;</text>'
        f'<rect x="{cx + 1}" y="{cy + 3}" width="8" height="2" fill="{GREEN}">'
        '<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1s" '
        'repeatCount="indefinite"/></rect></g>',
    ]
    steps = 36
    boot, order = 0.3, 0
    for rx, ry, period, ring in ORBITS:
        for index, name in enumerate(ring):
            main = name in MAIN_LANGUAGES
            strength = 1.0 if main else 0.82
            phase = index / len(ring)
            points, scales, fades = [], [], []
            for k in range(steps + 1):
                angle = 2 * math.pi * (phase + k / steps)
                depth = (math.sin(angle) + 1) / 2  # 1 at the front (bottom of the ellipse), 0 at the back
                points.append(f"{cx + rx * math.cos(angle):.1f},{cy + ry * math.sin(angle):.1f}")
                scales.append(f"{0.78 + 0.34 * depth:.3f}")
                fades.append(f"{(0.4 + 0.6 * depth) * strength:.2f}")
            timing = f'dur="{period}s" repeatCount="indefinite"'
            pill = len(name) * 7.8 + 38
            lit = order * scan_slot
            parts.append(
                f'<g><animateTransform attributeName="transform" type="translate" values="{";".join(points)}" {timing}/>'
                f'<g><animateTransform attributeName="transform" type="scale" values="{";".join(scales)}" {timing}/>'
                f'<animate attributeName="opacity" values="{";".join(fades)}" {timing}/>'
                f'<g opacity="0"><animate attributeName="opacity" values="0;1;0.2;1" keyTimes="0;0.4;0.6;1" '
                f'begin="{boot:.1f}s" dur="0.5s" fill="freeze"/>'
                f'<rect x="{-pill / 2:.1f}" y="-12" width="{pill:.1f}" height="24" rx="12" fill="{BG}" '
                f'stroke="{GREEN}" stroke-opacity="{0.85 if main else 0.5}" '
                f'stroke-width="{1.4 if main else 1}"/>'
                f'<rect x="{-pill / 2:.1f}" y="-12" width="{pill:.1f}" height="24" rx="12" fill="{GREEN}" '
                f'fill-opacity="0.18" stroke="{GREEN}" stroke-width="1.5" opacity="0">'
                f'<animate attributeName="opacity" values="0;0;1;1;0;0" '
                f'keyTimes="0;{lit / scan_cycle:.4f};{(lit + 0.3) / scan_cycle:.4f};{(lit + scan_slot - 0.3) / scan_cycle:.4f};'
                f'{(lit + scan_slot) / scan_cycle:.4f};1" dur="{scan_cycle:.1f}s" repeatCount="indefinite"/></rect>'
                f'<path transform="translate({-pill / 2 + 9:.1f},-6.5) scale(0.54)" d="{LOGOS[name]}" fill="{GREEN}"/>'
                f'<text x="{-pill / 2 + 27:.1f}" y="4" font-size="12" fill="{TEXT}" '
                f'font-weight="{700 if main else 400}">{escape(name)}</text>'
                "</g></g></g>"
            )
            boot += 0.15
            order += 1
    return svg(width, height, "Languages: " + ", ".join(names), "\n".join(parts))


LOADOUT = [
    ("web", ["react", "node.js", "flask", "material-ui", "pwa"]),
    ("ai-data", ["tensorflow", "pytorch", "keras", "opencv", "scikit-learn", "numpy", "pandas",
                 "matplotlib", "ollama", "tableau", "scrapy"]),
    ("databases", ["mysql", "sqlite", "sqlalchemy"]),
    ("desktop", ["javafx", "tkinter", "maven", "junit"]),
    ("tools", ["git", "docker", "github-actions", "jira", "jupyter"]),
]


def loadout():
    """Cards per category: the title types itself, then the items appear one by one; loops."""
    width, card_h, gap, char_w = 900, 74, 12, 7.8
    height = len(LOADOUT) * (card_h + gap) + gap
    cycle = 14.0

    def kt(*seconds):
        return ";".join(f"{min(max(s, 0) / cycle, 1):.4f}" for s in seconds)

    parts = [f'<rect width="{width}" height="{height}" rx="12" fill="{BG}" stroke="{BORDER}"/>']
    t = 0.3
    for row, (title, items) in enumerate(LOADOUT):
        y = gap + row * (card_h + gap)
        label = f"~/stack/{title}"
        typed = len(label) * 0.04
        parts.append(
            f'<rect x="{gap}" y="{y}" width="{width - 2 * gap}" height="{card_h}" rx="8" '
            f'fill="#05090A" stroke="{GREEN}" stroke-opacity="0.25">'
            f'<animate attributeName="stroke-opacity" values="0.15;0.5;0.15" dur="4s" '
            f'begin="-{row * 0.8}s" repeatCount="indefinite"/></rect>'
        )
        clip = f"title{row}"
        full = len(label) * char_w + 4
        parts.append(
            f'<clipPath id="{clip}"><rect x="{gap + 16}" y="{y + 8}" height="20" width="0">'
            f'<animate attributeName="width" values="0;0;{full};{full}" '
            f'keyTimes="{kt(0, t, t + typed, cycle)}" dur="{cycle}s" repeatCount="indefinite"/></rect></clipPath>'
            f'<text x="{gap + 16}" y="{y + 23}" font-size="12" fill="{GREEN}" clip-path="url(#{clip})">{label}</text>'
        )
        t += typed + 0.1
        x = gap + 16
        for item in items:
            pill = len(item) * 7.2 + 16
            if x + pill > width - gap - 16:
                break
            parts.append(
                f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0" '
                f'keyTimes="{kt(0, t, t + 0.15, cycle - 0.6, cycle)}" dur="{cycle}s" repeatCount="indefinite"/>'
                f'<rect x="{x:.1f}" y="{y + 36}" width="{pill:.1f}" height="24" rx="5" fill="#0D1117" '
                f'stroke="{BORDER}"/>'
                f'<text x="{x + pill / 2:.1f}" y="{y + 52}" text-anchor="middle" font-size="12" '
                f'fill="{TEXT}">{item}</text></g>'
            )
            x += pill + 8
            t += 0.08
    return svg(width, height, "Frameworks and tools", "\n".join(parts))


PROJECTS = [
    ("ClarifAI", "AI tool that structures and standardizes messy enterprise data"),
    ("ContractGuard", "serverless contract risk analysis on AWS · hackathon winner"),
    ("RoadSignDetection", "ML system that detects and classifies road signs"),
    ("ModernTaskManager", "task manager with React and Flask"),
    ("JavaMp3Player", "JavaFX audio player for mp3, wav and ogg"),
]


def projects():
    """`tree ~/projects`: the command types itself, then the tree prints line by line; loops."""
    width, left, line_h, char_w = 900, 24, 24, 7.8
    lines = ["~/projects"] + [
        f"{'└──' if i == len(PROJECTS) - 1 else '├──'} {name + '/':<20} " for i, (name, _) in enumerate(PROJECTS)
    ] + [f"{len(PROJECTS)} directories"]
    height = 30 + line_h * (len(lines) + 2)
    cycle = 16.0
    command = "tree ~/projects"
    rng = random.Random(11)

    def kt(*seconds):
        return ";".join(f"{min(max(s, 0) / cycle, 1):.4f}" for s in seconds)

    # One keyframe per keystroke, with uneven gaps, so the typing feels human.
    times, t = [0.0, 0.8], 0.8
    for _ in command:
        t += rng.uniform(0.05, 0.16)
        times.append(t)
    widths = [0] + [(n + 2) * char_w for n in range(len(command) + 1)]
    times.append(cycle)
    widths.append(widths[-1])
    end_of_typing = times[-2]
    after = end_of_typing + 0.4
    parts = [
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="12" fill="{BG}" stroke="{BORDER}"/>',
        f'<clipPath id="cmd"><rect x="{left}" y="18" height="24" width="0">'
        f'<animate attributeName="width" calcMode="discrete" values="{";".join(f"{w:.1f}" for w in widths)}" '
        f'keyTimes="{kt(*times)}" dur="{cycle}s" repeatCount="indefinite"/></rect></clipPath>',
        f'<text x="{left}" y="34" font-size="13" clip-path="url(#cmd)"><tspan fill="{GREEN}">$</tspan> '
        f'<tspan fill="{TEXT}">{command}</tspan></text>',
        f'<rect y="22" width="{char_w}" height="15" fill="{GREEN}" opacity="0">'
        f'<animate attributeName="x" calcMode="discrete" '
        f'values="{";".join(f"{left + max(w, 2 * char_w):.1f}" for w in widths)}" '
        f'keyTimes="{kt(*times)}" dur="{cycle}s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="0;1;1;0;0" '
        f'keyTimes="{kt(0, 0.8, after, after + 0.01, cycle)}" dur="{cycle}s" repeatCount="indefinite"/></rect>',
    ]
    t = after
    for index, line in enumerate(lines):
        y = 34 + (index + 1) * line_h
        if 0 < index <= len(PROJECTS):
            description = PROJECTS[index - 1][1]
            updated = PROJECT_UPDATES.get(PROJECTS[index - 1][0])
            inner = (f'<tspan fill="{MUTED}">{line[:4]}</tspan><tspan fill="{GREEN}">{escape(line[4:])}</tspan>'
                     f'<tspan fill="{MUTED}">{escape(description)}</tspan>'
                     + (f'<tspan fill="{BORDER}">  ·  </tspan><tspan fill="#6E7681">{escape(updated)}</tspan>'
                        if updated else ""))
        else:
            inner = f'<tspan fill="{TEXT if index == 0 else MUTED}">{escape(line)}</tspan>'
        parts.append(
            f'<text x="{left}" y="{y}" font-size="13" opacity="0">{inner}'
            f'<animate attributeName="opacity" values="0;0;1;1;0" '
            f'keyTimes="{kt(0, t, t + 0.01, cycle - 0.6, cycle)}" dur="{cycle}s" repeatCount="indefinite"/></text>'
        )
        t += rng.uniform(0.05, 0.2)
    y = 34 + (len(lines) + 1) * line_h
    parts.append(
        f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0" '
        f'keyTimes="{kt(0, t + 0.3, t + 0.31, cycle - 0.6, cycle)}" dur="{cycle}s" repeatCount="indefinite"/>'
        f'<text x="{left}" y="{y}" font-size="13" fill="{GREEN}">$</text>'
        f'<rect x="{left + 2 * char_w}" y="{y - 12}" width="{char_w}" height="15" fill="{GREEN}">'
        '<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1.1s" '
        'repeatCount="indefinite"/></rect></g>'
    )
    return svg(width, height, "Projects: " + ", ".join(name for name, _ in PROJECTS), "\n".join(parts))


def nest(piece, prefix, x, y, width):
    """Embed one generated SVG inside another at (x, y), scaled to `width`, with ids made unique."""
    head, rest = piece.split(">", 1)
    view = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', head)
    w, h = float(view.group(1)), float(view.group(2))
    body = rest.rsplit("</svg>", 1)[0]
    body = re.sub(r'id="([^"]+)"', rf'id="{prefix}\1"', body)
    body = re.sub(r"url\(#([^)]+)\)", rf"url(#{prefix}\1)", body)
    height = h * width / w
    return (f'<svg x="{x}" y="{y}" width="{width}" height="{height:.1f}" viewBox="0 0 {w} {h}">{body}</svg>',
            height)


def hero(pieces):
    """One seamless black panel holding the header, terminal and languages, with a breathing glow on the terminal."""
    width, pad, gap = 900, 16, 14
    inner = width - 2 * pad
    parts, y = [], pad
    for name, piece in pieces:
        nested, height = nest(piece, f"{name}_", pad, y, inner)
        if name == "term":
            parts.append(
                f'<rect x="{pad}" y="{y}" width="{inner}" height="{height:.1f}" rx="10" fill="none" '
                f'stroke="{GREEN}" stroke-width="6" filter="url(#glow)" opacity="0.15">'
                '<animate attributeName="opacity" values="0.08;0.3;0.08" dur="5s" repeatCount="indefinite"/></rect>'
            )
        parts.append(nested)
        y += height + gap
    total = y - gap + pad
    return svg(width, round(total), "Header, terminal and languages", "\n".join([
        '<filter id="glow" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="6"/></filter>',
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{total - 1:.1f}" rx="14" fill="{BG}" stroke="{BORDER}"/>',
        *parts,
    ]))


def render(out):
    out.mkdir(parents=True, exist_ok=True)
    term, cycle = terminal()
    (out / "hero.svg").write_text(hero([("head", header()), ("term", term), ("lang", languages())]),
                                  encoding="utf-8")
    (out / "loadout.svg").write_text(loadout(), encoding="utf-8")
    (out / "projects.svg").write_text(projects(), encoding="utf-8")
    (out / "footer.svg").write_text(footer(PHASE, WEATHER), encoding="utf-8")
    return cycle


def option(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


if "--variants" in sys.argv:
    OUT.mkdir(parents=True, exist_ok=True)
    for phase in SKIES:
        for weather in WEATHERS:
            (OUT / f"footer-{phase}-{weather}.svg").write_text(footer(phase, weather), encoding="utf-8")
elif "--previews" in sys.argv:
    for phase, weather, line in (("dawn", "clear", "munich · 4°C · clear"), ("day", "clear", "munich · 14°C · clear"),
                                 ("sunset", "clouds", "munich · 9°C · cloudy"), ("night", "clear", None),
                                 ("day", "rain", "munich · 8°C · light rain"),
                                 ("night", "snow", "munich · -2°C · snow")):
        use_theme(phase, weather, line)
        render(OUT / f"{phase}-{weather}")
else:
    updates = option("--projects")
    use_theme(option("--phase", "night"), option("--weather", "clear"), option("--line"), option("--status"),
              option("--season", "autumn"), json.loads(updates) if updates else None)
    print(f"terminal cycle {render(OUT):.1f}s")
