"""Mix-bus (monitor) send interpretation.

Builds a strip x bus matrix of sends from the parsed scene. Stereo-linked bus
pairs collapse into one column; the odd bus carries the level and pan for the
pair, so its send is the one shown.

Which buses are "monitor" mixes is not stored in the scene, so every bus that
is named or receives at least one active send is listed. Nothing is guessed
from bus names.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from x32print.models import Bus, Channel, Scene, Send

TAP_LABELS = {
    "IN/LC": "Input",
    "<-EQ": "Pre-EQ",
    "EQ->": "Post-EQ",
    "PRE": "Pre-fader",
    "POST": "Post-fader",
    "GRP": "Subgroup",
}


@dataclass(slots=True)
class MixColumn:
    buses: list[Bus]  # one bus, or an odd/even linked pair
    tap: str | None = None  # most common tap among active sends

    @property
    def number(self) -> int:
        return self.buses[0].number

    @property
    def stereo(self) -> bool:
        return len(self.buses) == 2

    @property
    def label(self) -> str:
        nums = "–".join(f"{b.number:02d}" for b in self.buses)
        return f"Bus {nums}"

    @property
    def name(self) -> str:
        names = [b.name for b in self.buses if b.name]
        if len(names) == 2 and names[0] != names[1]:
            return " / ".join(names)
        return names[0] if names else ""

    @property
    def color(self) -> str | None:
        return self.buses[0].color


@dataclass(slots=True)
class MixRow:
    strip: Channel
    cells: list[Send | None] = field(default_factory=list)  # aligned with columns


@dataclass(slots=True)
class MixMatrix:
    columns: list[MixColumn]
    rows: list[MixRow]


def _columns(scene: Scene) -> list[MixColumn]:
    by_number = {bus.number: bus for bus in scene.buses}
    columns: list[MixColumn] = []
    for bus in scene.buses:
        partner = by_number.get(bus.number + 1)
        if bus.number % 2 == 0 and bus.linked and bus.number - 1 in by_number:
            continue  # folded into the odd partner's column
        if bus.number % 2 == 1 and bus.linked and partner:
            columns.append(MixColumn([bus, partner]))
        else:
            columns.append(MixColumn([bus]))
    return columns


def build_mix_matrix(scene: Scene) -> MixMatrix:
    strips = [*scene.channels, *scene.aux_inputs, *scene.fx_returns]
    columns = _columns(scene)

    def cell(strip: Channel, column: MixColumn) -> Send | None:
        send = strip.sends.get(column.number)
        return send if send and send.active else None

    active_columns = [
        col for col in columns
        if any(b.name.strip() for b in col.buses) or any(cell(s, col) for s in strips)
    ]
    for col in active_columns:
        taps = Counter(send.tap for s in strips if (send := cell(s, col)) and send.tap)
        col.tap = taps.most_common(1)[0][0] if taps else None

    rows = []
    for strip in strips:
        cells = [cell(strip, col) for col in active_columns]
        if any(cells):
            rows.append(MixRow(strip, cells))
    return MixMatrix(active_columns, rows)


def fmt_pan(value: float | None) -> str:
    if value is None:
        return ""
    if abs(value) < 0.5:
        return "C"
    return f"{'L' if value < 0 else 'R'}{abs(value):.0f}"
