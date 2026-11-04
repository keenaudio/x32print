"""HTML report rendered with Jinja2."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from x32print.models import Scene
from x32print.reports.base import Report
from x32print.routing import channel_is_used
from x32print.validator import validate_scene

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"


def _fmt_gain(value: float | None) -> str:
    if value is None:
        return ""
    return f"{value:+.1f} dB"


def _fmt_freq(value: float | None) -> str:
    if value is None:
        return ""
    return f"{value / 1000:.1f}k" if value >= 1000 else f"{value:.0f} Hz"


def _text_color(hex_color: str | None) -> str:
    """Pick black or white text for legibility over a scribble color."""
    if not hex_color:
        return "#000"
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return "#000" if (0.299 * r + 0.587 * g + 0.114 * b) > 150 else "#fff"


class HtmlReport(Report):
    def __init__(self) -> None:
        self.env = Environment(
            loader=FileSystemLoader(TEMPLATE_DIR),
            autoescape=select_autoescape(["html", "j2"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self.env.filters["gain"] = _fmt_gain
        self.env.filters["freq"] = _fmt_freq
        self.env.filters["text_color"] = _text_color
        self.env.tests["used"] = channel_is_used

    def render(self, scene: Scene) -> str:
        template = self.env.get_template("report.html.j2")
        css = (TEMPLATE_DIR / "report.css").read_text(encoding="utf-8")
        return template.render(
            scene=scene,
            css=css,
            warnings=[*scene.warnings, *validate_scene(scene)],
            generated=datetime.now().strftime("%Y-%m-%d %H:%M"),
        )
