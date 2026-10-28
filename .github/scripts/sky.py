"""Pick the time of day and weather in Munich, then render the profile images for them."""

import json
import subprocess
import sys
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

# All times come back as Munich local time, so no time zone handling is needed here.
URL = (
    "https://api.open-meteo.com/v1/forecast?latitude=48.14&longitude=11.58"
    "&current=temperature_2m,weather_code&daily=sunrise,sunset&timezone=Europe%2FBerlin&forecast_days=1"
)
HOUR = timedelta(hours=1)

# WMO weather codes as used by Open-Meteo: https://open-meteo.com/en/docs
WEATHER_CODES = [
    ({0, 1}, "clear", "clear"),
    ({2}, "clouds", "partly cloudy"),
    ({3}, "clouds", "cloudy"),
    ({45, 48}, "fog", "fog"),
    ({51, 53, 55, 56, 57}, "rain", "drizzle"),
    ({61, 63, 66, 80, 81}, "rain", "rain"),
    ({65, 67, 82}, "rain", "heavy rain"),
    ({71, 73, 77, 85}, "snow", "snow"),
    ({75, 86}, "snow", "heavy snow"),
    ({95, 96, 99}, "storm", "thunderstorm"),
]


def phase_for(now, sunrise, sunset):
    """Dawn runs from 2 h before to 1 h after sunrise, sunset from 1 h before to 1 h after sunset."""
    if sunrise - 2 * HOUR <= now < sunrise + HOUR:
        return "dawn"
    if sunset - HOUR <= now < sunset + HOUR:
        return "sunset"
    return "day" if sunrise + HOUR <= now < sunset - HOUR else "night"


def weather_for(code):
    for codes, weather, label in WEATHER_CODES:
        if code in codes:
            return weather, label
    return "clouds", "cloudy"


def main():
    out = sys.argv[1]
    with urllib.request.urlopen(URL, timeout=20) as response:
        data = json.load(response)
    now = datetime.fromisoformat(data["current"]["time"])
    sunrise = datetime.fromisoformat(data["daily"]["sunrise"][0])
    sunset = datetime.fromisoformat(data["daily"]["sunset"][0])
    phase = phase_for(now, sunrise, sunset)
    weather, label = weather_for(data["current"]["weather_code"])
    line = f"munich · {round(data['current']['temperature_2m'])}°C · {label}"
    print(f"{now:%Y-%m-%d %H:%M} {phase} {weather} ({line})")
    design = Path(__file__).with_name("design.py")
    subprocess.run(
        [sys.executable, str(design), out, "--phase", phase, "--weather", weather, "--line", line],
        check=True,
    )


if __name__ == "__main__":
    main()
