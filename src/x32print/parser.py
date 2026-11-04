"""Parser for text-based X32 scene (.scn) files.

The parser preserves every directive it reads in Scene.raw_directives and
extracts channel, aux-input, bus and headamp data. It does not interpret
routing; that is routing.py's job.

Relevant line formats (firmware 4.x):
    /ch/01/config "Name" <icon> <color> <source>
    /ch/01/preamp <trim> <invert> <hpf on> <hpf slope> <hpf freq>
    /auxin/01/config "Name" <icon> <color> <source>
    /bus/01/config "Name" <icon> <color>
    /headamp/032 <gain> <phantom>
    /config/chlink ON|OFF x16   (pairs 1-2, 3-4 ... 31-32)
    /config/routing/IN <blk 1-8> <blk 9-16> <blk 17-24> <blk 25-32> <aux blk>
"""

from __future__ import annotations

import re
from pathlib import Path

from x32print.colors import color_hex, normalize_color
from x32print.models import Bus, Channel, Headamp, Scene

_DIRECTIVE_RE = re.compile(r"^\s*(/\S+)\s*(.*?)\s*$")
_TOKEN_RE = re.compile(r'"((?:[^"\\]|\\.)*)"|(\S+)')
_STRIP_CONFIG_RE = re.compile(r"^/(ch|auxin|bus)/(\d{1,2})/config$", re.I)
_PREAMP_RE = re.compile(r"^/(ch|auxin)/(\d{1,2})/preamp$", re.I)
_HEADAMP_RE = re.compile(r"^/headamp/(\d{1,3})$", re.I)


def tokenize(payload: str) -> list[str]:
    """Split a directive payload into tokens, honouring double quotes."""
    tokens = []
    for quoted, bare in _TOKEN_RE.findall(payload):
        if bare:
            tokens.append(bare)
        else:
            tokens.append(quoted.replace(r"\"", '"').replace("\\\\", "\\"))
    return tokens


def _to_int(value: str | None) -> int | None:
    try:
        return int(value) if value is not None else None
    except ValueError:
        return None


def _to_float(value: str | None) -> float | None:
    if value is None:
        return None
    text = value.strip()
    if text in ("-oo", "-inf"):
        return float("-inf")
    try:
        # X32 writes kHz values like "3k20" meaning 3.20 kHz
        if "k" in text:
            whole, _, frac = text.partition("k")
            return float(f"{whole}.{frac or 0}") * 1000
        return float(text)
    except ValueError:
        return None


def _on(value: str | None) -> bool:
    return (value or "").upper() == "ON"


def parse_scene(path: str | Path) -> Scene:
    scene_path = Path(path)
    return parse_scene_text(
        scene_path.read_text(encoding="utf-8", errors="replace"),
        name=scene_path.stem,
        source_file=str(scene_path),
    )


def parse_scene_text(text: str, name: str = "scene", source_file: str | None = None) -> Scene:
    raw: dict[str, list[str]] = {}
    strips: dict[tuple[str, int], list[str]] = {}
    preamps: dict[tuple[str, int], list[str]] = {}
    headamps: dict[int, Headamp] = {}
    scene_name = name

    for line in text.splitlines():
        if line.startswith("#"):
            # Header, e.g. #4.0# "X32-badcat-11.04" "" %000000000 1
            header_tokens = tokenize(line.split("#", 2)[-1])
            if header_tokens and header_tokens[0]:
                scene_name = header_tokens[0]
            continue
        match = _DIRECTIVE_RE.match(line)
        if not match:
            continue
        address, payload = match.groups()
        raw.setdefault(address, []).append(payload)

        if m := _STRIP_CONFIG_RE.match(address):
            strips[(m.group(1).lower(), int(m.group(2)))] = tokenize(payload)
        elif m := _PREAMP_RE.match(address):
            preamps[(m.group(1).lower(), int(m.group(2)))] = tokenize(payload)
        elif m := _HEADAMP_RE.match(address):
            tokens = tokenize(payload)
            headamps[int(m.group(1))] = Headamp(
                gain=_to_float(tokens[0]) if tokens else None,
                phantom=_on(tokens[1]) if len(tokens) > 1 else False,
            )

    links = [_on(t) for t in tokenize(raw.get("/config/chlink", [""])[-1])]
    aux_links = [_on(t) for t in tokenize(raw.get("/config/auxlink", [""])[-1])]

    def build_strip(kind: str, number: int, tokens: list[str]) -> Channel:
        color = tokens[2] if len(tokens) > 2 else None
        pre = preamps.get((kind, number), [])
        pair_links = links if kind == "ch" else aux_links
        pair = (number - 1) // 2
        return Channel(
            number=number,
            kind=kind,
            label=tokens[0] if tokens else "",
            icon=_to_int(tokens[1]) if len(tokens) > 1 else None,
            color_code=normalize_color(color),
            scribble_color=color_hex(color),
            source_index=_to_int(tokens[3]) if len(tokens) > 3 else None,
            linked=pair < len(pair_links) and pair_links[pair],
            trim=_to_float(pre[0]) if pre else None,
            hpf_on=_on(pre[2]) if len(pre) > 2 else False,
            hpf_freq=_to_float(pre[4]) if len(pre) > 4 else None,
        )

    channels = [build_strip("ch", n, t) for (k, n), t in sorted(strips.items()) if k == "ch"]
    aux_inputs = [build_strip("auxin", n, t) for (k, n), t in sorted(strips.items()) if k == "auxin"]
    buses = []
    for (kind, number), tokens in sorted(strips.items()):
        if kind != "bus":
            continue
        color = tokens[2] if len(tokens) > 2 else None
        buses.append(Bus(
            number=number,
            name=tokens[0] if tokens else "",
            icon=_to_int(tokens[1]) if len(tokens) > 1 else None,
            color=color_hex(color),
        ))

    warnings = []
    if "/config/routing/IN" not in raw:
        warnings.append("No /config/routing/IN directive found; input sources are unresolved.")

    return Scene(
        name=scene_name,
        channels=channels,
        aux_inputs=aux_inputs,
        buses=buses,
        headamps=headamps,
        raw_directives=raw,
        warnings=warnings,
        source_file=source_file,
    )
