"""Command-line interface."""

from __future__ import annotations

import argparse
from pathlib import Path

from x32print.models import Bus, Channel, Scene
from x32print.parser import parse_scene
from x32print.reports.html import HtmlReport


def _demo_scene() -> Scene:
    return Scene(
        name="x32print-demo",
        channels=[
            Channel(1, "Lead Vocal", scribble_color="#f1c40f"),
            Channel(2, "Guitar", scribble_color="#2ecc71"),
            Channel(3, "Keys L", scribble_color="#e74c3c"),
            Channel(4, "Keys R", scribble_color="#e74c3c"),
            Channel(5, "Kick", scribble_color="#ecf0f1"),
            Channel(6, "Snare", scribble_color="#ecf0f1"),
        ],
        buses=[
            Bus(1, "Monitor 1"),
            Bus(2, "Monitor 2"),
            Bus(3, "Drum Mix"),
            Bus(8, "Horn Mix"),
        ],
        warnings=["Demo data only; no X32 scene file was parsed."],
    )


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

    output.write_text(HtmlReport().render(scene), encoding="utf-8")
    print(f"Report written: {output.resolve()}")
    return 0
