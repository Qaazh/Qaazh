"""Build the animated SVG assets for the profile README (black / green theme)."""

import json
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
    "crouch_a": ["", "", "    /\\_/\\", "   ( O.O )_____", "   /_/_/___/_/ )~"],
    "crouch_b": ["", "", "    /\\_/\\", "   ( O.O )_____", "   /_/_/___/_/ )-"],
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
    steps = [
        (("walk_a", "walk_b"), 6.0, 0.3, None, False),
        (("sit",), 1.2, None, None, False),
        (("look_l",), 0.8, None, None, False),
        (("look_r",), 0.8, None, None, False),
        (("blink",), 0.25, None, None, False),
        (("sit", "sit_tail"), 2.0, None, None, False),
        (("groom_a", "groom_b"), 4.0, None, None, False),
        (("yawn",), 1.4, None, None, False),
        (("sit",), 2.0, None, "yarn_in", False),
        (("bat_a", "bat_b"), 5.0, None, "bat", False),
        (("crouch_a", "crouch_b"), 2.2, None, "crouch", False),
        (("walk_a",), 1.0, 0.55, "pounce", True),
        (("sit", "sit_tail"), 2.4, None, None, False),
        (("look_l", "look_r"), 4.2, None, "bug", False),
        (("bat_a",), 0.5, None, None, False),
        (("sit",), 1.6, None, "bug_gone", False),
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
        (("stretch",), 3.0, None, None, False),
        (("knead_a", "knead_b"), 4.0, None, None, False),
        (("sleep",), 22.0 if PHASE == "night" else 13.0, None, "sleep", False),
        (("blink",), 0.4, None, None, False),
        (("sit", "sit_tail"), 2.0, None, None, False),
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
    parts.append("</g>")

    # A ball of yarn rolls in, gets batted around, then rolls away for the pounce.
    cat_x = positions["yarn_in"] + left
    yarn_y = y + 4 * line_h
    yarn = [
        (labels["yarn_in"], width - 60, 0),
        (labels["bat"], cat_x + 110, 0),
        (labels["bat"] + 1.2, cat_x + 130, -8),
        (labels["bat"] + 2.4, cat_x + 105, 0),
        (labels["bat"] + 3.6, cat_x + 135, -6),
        (labels["crouch"], cat_x + 120, 0),
        (labels["pounce"], 0.55 * distance + left + 150, 0),
        (labels["pounce"] + 3.0, width - 40, 0),
    ]
    parts.append(
        f'<g opacity="0">{visible(labels["yarn_in"], labels["pounce"] + 3.0)}{moving(yarn)}'
        f'<text x="0" y="{yarn_y}" font-size="15" fill="#F778BA">@'
        f'<animateTransform attributeName="transform" type="rotate" values="0 4 {yarn_y - 5};360 4 {yarn_y - 5}" '
        f'dur="1s" repeatCount="indefinite"/></text>'
        f'<text x="-34" y="{yarn_y}" font-size="13" fill="#F778BA" opacity="0.6">~~~~</text></g>'
    )

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


ORBITS = [
    (150, 38, 26, ["Python", "Java", "TypeScript"]),
    (270, 66, 40, ["JavaScript", "C", "C++", "PHP"]),
    (390, 94, 58, ["SQL", "Bash", "HTML", "CSS"]),
]


def languages():
    """Language names orbiting a core, each booting in with a short flicker."""
    width, height = 900, 240
    cx, cy = width / 2, height / 2
    parts = [
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="12" fill="{BG}" stroke="{BORDER}"/>',
        f'<text x="24" y="30" font-size="11" fill="{MUTED}">LANGUAGES</text>',
        f'<circle cx="{cx}" cy="{cy}" r="22" fill="{CORE}" stroke="{GREEN}" stroke-opacity="0.6">'
        f'<animate attributeName="r" values="21;27;21;21" keyTimes="0;0.06;0.2;1" '
        f'dur="{ORBITS[0][2] / len(ORBITS[0][3]):.2f}s" repeatCount="indefinite"/></circle>',
        f'<text x="{cx}" y="{cy + 5}" text-anchor="middle" font-size="14" fill="{GREEN}">&lt;/&gt;</text>',
    ]
    boot = 0.3
    for rx, ry, period, names in ORBITS:
        path = f"M {cx - rx} {cy} A {rx} {ry} 0 1 0 {cx + rx} {cy} A {rx} {ry} 0 1 0 {cx - rx} {cy} Z"
        parts.append(f'<path d="{path}" fill="none" stroke="{GREEN}" stroke-opacity="0.15" stroke-dasharray="2 6"/>')
        for index, name in enumerate(names):
            pill = len(name) * 7.8 + 18
            offset = period * index / len(names)
            parts.append(
                f'<g opacity="0">'
                f'<animate attributeName="opacity" values="0;1;0.2;1" keyTimes="0;0.4;0.6;1" '
                f'begin="{boot:.1f}s" dur="0.5s" fill="freeze"/>'
                f'<animateMotion dur="{period}s" begin="-{offset:.2f}s" repeatCount="indefinite" path="{path}"/>'
                f'<rect x="{-pill / 2:.1f}" y="-11" width="{pill:.1f}" height="22" rx="11" '
                f'fill="{BG}" stroke="{GREEN}" stroke-opacity="0.5"/>'
                f'<text x="0" y="4" text-anchor="middle" font-size="12" fill="{TEXT}">{name}</text></g>'
            )
            boot += 0.15
    return svg(width, height, "Languages: " + ", ".join(n for *_, ns in ORBITS for n in ns), "\n".join(parts))


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
