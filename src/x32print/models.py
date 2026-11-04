"""Core data models. These classes deliberately know nothing about file syntax."""

from dataclasses import dataclass, field


@dataclass(slots=True)
class InputSource:
    """A normalized physical/logical input source."""

    source_type: str
    port: int | None = None
    device: str | None = None
    display_name: str | None = None

    def display(self) -> str:
        if self.display_name:
            return self.display_name
        if self.port is not None:
            prefix = self.device or self.source_type
            return f"{prefix} {self.port:02d}"
        return self.device or self.source_type


@dataclass(slots=True)
class Channel:
    number: int
    label: str = ""
    source: InputSource | None = None
    scribble_color: str | None = None
    icon: int | None = None
    notes: str = ""


@dataclass(slots=True)
class Bus:
    number: int
    name: str = ""
    color: str | None = None
    icon: int | None = None
    notes: str = ""


@dataclass(slots=True)
class RoutingMap:
    """Routing data, including raw tokens until decoding is verified."""

    input_tokens: list[str] = field(default_factory=list)
    output_tokens: list[str] = field(default_factory=list)
    decoded_inputs: dict[int, InputSource] = field(default_factory=dict)


@dataclass(slots=True)
class Scene:
    name: str
    channels: list[Channel] = field(default_factory=list)
    buses: list[Bus] = field(default_factory=list)
    routing: RoutingMap = field(default_factory=RoutingMap)
    raw_directives: dict[str, list[str]] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
