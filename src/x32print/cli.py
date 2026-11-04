"""Command-line interface."""

from __future__ import annotations

import argparse
from pathlib import Path

from x32print.parser import parse_scene, parse_scene_text
from x32print.reports.html import HtmlReport
from x32print.routing import decode_input_routing

_DEMO_SCN = """\
#4.0# "x32print-demo" "" %000000000 1
/config/chlink OFF ON OFF OFF OFF OFF OFF OFF OFF OFF OFF OFF OFF OFF OFF OFF
/config/routing/IN A1-8 A9-16 B1-8 B9-16 AN1-4
/ch/01/config "Lead Vocal" 50 YE 1
/ch/02/config "Guitar" 17 GN 2
/ch/03/config "Keys L" 33 RD 17
/ch/04/config "Keys R" 33 RD 18
/ch/05/config "Kick" 2 WH 25
/ch/06/config "Snare" 4 WH 26
/bus/01/config "Monitor 1" 63 YE
/bus/02/config "Monitor 2" 63 GN
/headamp/032 +30.0 ON
/headamp/033 +20.0 OFF
/headamp/080 +10.0 OFF
/headamp/081 +10.0 OFF
"""


def _demo_scene():
    scene = parse_scene_text(_DEMO_SCN, name="x32print-demo")
    scene.warnings.append("Demo data only; no X32 scene file was parsed.")
    return scene


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="x32print",
        description="Generate printable HTML documentation from an X32 scene.",
    )
    parser.add_argument("scene", nargs="?", help="Path to an X32 .scn scene file")
    parser.add_argument("--output", "-o", help="Output HTML path")
    parser.add_argument("--demo", action="store_true", help="Generate a report using built-in demo data")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.demo:
        scene = _demo_scene()
        output = Path(args.output) if args.output else Path("x32print-demo.html")
    elif args.scene:
        scene_path = Path(args.scene)
        if not scene_path.is_file():
            print(f"Error: scene file not found: {scene_path}")
            return 2
        try:
            scene = parse_scene(scene_path)
        except OSError as exc:
            print(f"Error reading scene file: {exc}")
            return 2
        output = Path(args.output) if args.output else scene_path.with_suffix(".html")
    else:
        build_parser().print_help()
        return 2

    decode_input_routing(scene)
    output.write_text(HtmlReport().render(scene), encoding="utf-8")
    print(f"Report written: {output.resolve()}")
    return 0
