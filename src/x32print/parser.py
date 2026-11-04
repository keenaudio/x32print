"""Conservative parser for text-based X32 scene directives.

The parser preserves every directive it can read. Semantic extraction is
intentionally limited until confirmed against representative scene files.
"""

from __future__ import annotations

import re
from pathlib import Path

from x32print.colors import color_hex
from x32print.models import Bus, Channel, Scene

_DIRECTIVE_RE = re.compile(r"^\s*(/\S+)\s*(.*?)\s*$")
_CHANNEL_RE = re.compile(r"^/ch/(\d{1,2})/config/(name|color|icon)$", re.I)
_BUS_RE = re.compile(r"^/bus/(\d{1,2})/config/(name|color|icon)$", re.I)
_ROUTING_IN_RE = re.compile(r"^/config/routing/IN$", re.I)


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1].replace(r'\"', '"').replace(r'\\', '\\')
    return value


def parse_scene(path: str | Path) -> Scene:
    """Parse a scene file into a Scene model.

    Unknown directives are retained. Routing tokens are captured but not
    interpreted because their encoding needs fixture-backed verification.
    """
    scene_path = Path(path)
    text = scene_path.read_text(encoding="utf-8", errors="replace")
    raw: dict[str, list[str]] = {}
    channel_data: dict[int, dict[str, str]] = {}
    bus_data: dict[int, dict[str, str]] = {}
    routing_tokens: list[str] = []

    for line in text.splitlines():
        match = _DIRECTIVE_RE.match(line)
        if not match:
            continue
        address, payload = match.groups()
        raw.setdefault(address, []).append(payload)
        channel_match = _CHANNEL_RE.match(address)
        bus_match = _BUS_RE.match(address)
        if channel_match:
            number, field_name = int(channel_match.group(1)), channel_match.group(2).lower()
            channel_data.setdefault(number, {})[field_name] = _unquote(payload)
        elif bus_match:
            number, field_name = int(bus_match.group(1)), bus_match.group(2).lower()
            bus_data.setdefault(number, {})[field_name] = _unquote(payload)
        elif _ROUTING_IN_RE.match(address):
            routing_tokens.extend(payload.split())

    channels = []
    for number in sorted(channel_data):
        data = channel_data[number]
        try:
            color_code = int(data["color"]) if "color" in data else None
        except ValueError:
            color_code = None
        try:
            icon = int(data["icon"]) if "icon" in data else None
        except ValueError:
            icon = None
        channels.append(Channel(
            number=number,
            label=data.get("name", ""),
            scribble_color=color_hex(color_code),
            icon=icon,
        ))

    buses = []
    for number in sorted(bus_data):
        data = bus_data[number]
        try:
            color_code = int(data["color"]) if "color" in data else None
        except ValueError:
            color_code = None
        try:
            icon = int(data["icon"]) if "icon" in data else None
        except ValueError:
            icon = None
        buses.append(Bus(
            number=number,
            name=data.get("name", ""),
            color=color_hex(color_code),
            icon=icon,
        ))

    return Scene(
        name=scene_path.stem,
        channels=channels,
        buses=buses,
        raw_directives=raw,
        warnings=[
            "Input routing was captured as raw scene data but has not yet been decoded."
        ] if routing_tokens else [
            "No /config/routing/IN directive was found; input sources are unresolved."
        ],
    )
