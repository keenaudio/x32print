"""Core data models. These classes deliberately know nothing about file syntax."""

from dataclasses import dataclass, field


@dataclass(slots=True)
class InputSource:
    """A normalized physical/logical input source.

    source_type is one of: "local", "aes50", "card", "aux", "usb", "fx",
    "bus", "off", "unresolved".
    """

    source_type: str
    port: int | None = None
    device: str | None = None
    display_name: str | None = None
    headamp_index: int | None = None

    def display(self) -> str:
        if self.display_name:
            return self.display_name
        prefix = {
            "local": "Local",
            "aes50": f"AES50 {self.device}" if self.device else "AES50",
            "card": "Card",
            "aux": "Aux In",
        }.get(self.source_type, self.device or self.source_type)
        if self.port is not None:
            return f"{prefix} {self.port:02d}"
        return prefix

    @property
    def has_preamp(self) -> bool:
        return self.headamp_index is not None


@dataclass(slots=True)
class Headamp:
    gain: float | None = None
    phantom: bool = False


@dataclass(slots=True)
class Channel:
    number: int
    label: str = ""
    source: InputSource | None = None
    scribble_color: str | None = None
    color_code: str | None = None
    icon: int | None = None
    notes: str = ""
    kind: str = "ch"  # "ch" or "auxin"
    source_index: int | None = None  # raw /config source value
    linked: bool = False  # stereo-linked with its odd/even partner
    trim: float | None = None
    hpf_on: bool = False
    hpf_freq: float | None = None
    gain: float | None = None
    phantom: bool | None = None

    @property
    def display_id(self) -> str:
        return f"Aux {self.number}" if self.kind == "auxin" else f"{self.number:02d}"


@dataclass(slots=True)
class Bus:
    number: int
    name: str = ""
    color: str | None = None
    icon: int | None = None
    notes: str = ""


@dataclass(slots=True)
class StageboxSocket:
    port: int
    channels: list[Channel] = field(default_factory=list)
    gain: float | None = None
    phantom: bool = False


@dataclass(slots=True)
class Stagebox:
    key: str  # e.g. "aes50:A"
    name: str
    sockets: list[StageboxSocket] = field(default_factory=list)


@dataclass(slots=True)
class RoutingMap:
    """Routing data, including raw tokens until decoding is verified."""

    input_tokens: list[str] = field(default_factory=list)
    output_tokens: list[str] = field(default_factory=list)
    # logical input number (1-32) -> physical source
    decoded_inputs: dict[int, InputSource] = field(default_factory=dict)
    # aux input number (1-6) -> physical source
    decoded_aux: dict[int, InputSource] = field(default_factory=dict)


@dataclass(slots=True)
class Scene:
    name: str
    channels: list[Channel] = field(default_factory=list)
    aux_inputs: list[Channel] = field(default_factory=list)
    buses: list[Bus] = field(default_factory=list)
    headamps: dict[int, Headamp] = field(default_factory=dict)
    routing: RoutingMap = field(default_factory=RoutingMap)
    stageboxes: list[Stagebox] = field(default_factory=list)
    raw_directives: dict[str, list[str]] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    source_file: str | None = None
