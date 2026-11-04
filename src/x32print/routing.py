"""Routing interpretation layer.

X32 input routing works in two stages:

1. /config/routing/IN assigns a physical block of 8 sockets to each group of
   logical inputs (In 1-8, 9-16, 17-24, 25-32), plus a fifth block for
   Aux In 1-4. Block tokens look like AN1-8 (local), A9-16 (AES50 A),
   B1-8 (AES50 B), CARD17-24 (expansion card), AUX1-4.
2. Each channel's /config source index then picks a logical input:
   0 OFF, 1-32 In 01-32, 33-38 Aux 1-6, 39-40 USB L/R, 41-48 FX 1L-4R,
   49-64 Bus 01-16.

Preamp gain/phantom lives in /headamp/NNN, indexed by physical socket:
000-031 local, 032-079 AES50 A 1-48, 080-127 AES50 B 1-48.
"""

from __future__ import annotations

import re

from x32print.models import Channel, InputSource, Scene, Stagebox, StageboxSocket

_BLOCK_RE = re.compile(r"^(AN|A|B|CARD|AUX)(\d+)-(\d+)$", re.I)

_HEADAMP_BASE = {"local": 0, ("aes50", "A"): 32, ("aes50", "B"): 80}


def _block_source(token: str, offset: int) -> InputSource | None:
    match = _BLOCK_RE.match(token)
    if not match:
        return None
    prefix, start = match.group(1).upper(), int(match.group(2))
    port = start + offset
    if prefix == "AN":
        return InputSource("local", port=port, headamp_index=port - 1)
    if prefix in ("A", "B"):
        base = _HEADAMP_BASE[("aes50", prefix)]
        return InputSource("aes50", port=port, device=prefix, headamp_index=base + port - 1)
    if prefix == "CARD":
        return InputSource("card", port=port)
    return InputSource("aux", port=port)


def decode_input_routing(scene: Scene) -> None:
    """Decode routing blocks and resolve every channel's physical source."""
    payloads = scene.raw_directives.get("/config/routing/IN", [])
    tokens = payloads[-1].split() if payloads else []
    scene.routing.input_tokens = tokens

    for block, token in enumerate(tokens[:4]):
        for offset in range(8):
            source = _block_source(token, offset)
            if source is None:
                scene.warnings.append(f"Unrecognised input routing block {token!r}.")
                break
            scene.routing.decoded_inputs[block * 8 + offset + 1] = source
    if len(tokens) > 4:
        for offset in range(4):
            source = _block_source(tokens[4], offset)
            if source is None:
                scene.warnings.append(f"Unrecognised aux routing block {tokens[4]!r}.")
                break
            scene.routing.decoded_aux[offset + 1] = source
    # Aux 5-6 are not part of the routing block (fixed local aux sockets).
    for aux in range(1, 7):
        scene.routing.decoded_aux.setdefault(aux, InputSource("aux", port=aux))

    for channel in [*scene.channels, *scene.aux_inputs]:
        channel.source = _resolve(scene, channel.source_index)
        if channel.source and channel.source.headamp_index is not None:
            headamp = scene.headamps.get(channel.source.headamp_index)
            if headamp:
                channel.gain = headamp.gain
                channel.phantom = headamp.phantom

    scene.stageboxes = build_stageboxes(scene)


def _resolve(scene: Scene, index: int | None) -> InputSource | None:
    if index is None:
        return None
    if index == 0:
        return InputSource("off", display_name="Off")
    if 1 <= index <= 32:
        return scene.routing.decoded_inputs.get(
            index, InputSource("unresolved", display_name=f"In {index:02d} (unrouted)")
        )
    if 33 <= index <= 38:
        return scene.routing.decoded_aux.get(index - 32)
    if index in (39, 40):
        return InputSource("usb", display_name="USB L" if index == 39 else "USB R")
    if 41 <= index <= 48:
        n = index - 41
        return InputSource("fx", display_name=f"FX {n // 2 + 1}{'LR'[n % 2]}")
    if 49 <= index <= 64:
        return InputSource("bus", display_name=f"Bus {index - 48:02d}")
    return InputSource("unresolved", display_name=f"Source #{index}")


def build_stageboxes(scene: Scene) -> list[Stagebox]:
    """Group channels by the physical box/socket they're patched to.

    A box is listed if any routing block points at it. Its socket count is
    the highest routed socket, rounded up to a multiple of 8.
    """
    boxes: dict[str, Stagebox] = {}
    max_port: dict[str, int] = {}

    def key_of(source: InputSource) -> tuple[str, str] | None:
        if source.source_type == "aes50":
            return f"aes50:{source.device}", f"Stage box — AES50 {source.device}"
        if source.source_type == "local":
            return "local", "Console local inputs"
        return None

    for source in scene.routing.decoded_inputs.values():
        if (kv := key_of(source)) and kv[0] != "local":
            max_port[kv[0]] = max(max_port.get(kv[0], 0), source.port or 0)
            boxes.setdefault(kv[0], Stagebox(kv[0], kv[1]))

    sockets: dict[tuple[str, int], StageboxSocket] = {}
    for channel in [*scene.channels, *scene.aux_inputs]:
        source = channel.source
        if not source or not (kv := key_of(source)) or source.port is None:
            continue
        if not channel_is_used(channel) and kv[0] not in boxes:
            continue  # don't invent a box just for unused strips
        key = kv[0]
        boxes.setdefault(key, Stagebox(key, kv[1]))
        max_port[key] = max(max_port.get(key, 0), source.port)
        sockets.setdefault((key, source.port), StageboxSocket(source.port)).channels.append(channel)

    for key, box in boxes.items():
        count = -(-max_port[key] // 8) * 8
        base = _HEADAMP_BASE.get(
            "local" if key == "local" else ("aes50", key.split(":")[1]), 0
        )
        for port in range(1, count + 1):
            socket = sockets.get((key, port), StageboxSocket(port))
            headamp = scene.headamps.get(base + port - 1)
            if headamp:
                socket.gain, socket.phantom = headamp.gain, headamp.phantom
            box.sockets.append(socket)

    order = {"aes50:A": 0, "aes50:B": 1, "local": 2}
    return sorted(boxes.values(), key=lambda b: order.get(b.key, 9))


def channel_is_used(channel: Channel) -> bool:
    return bool(channel.label.strip()) or channel.color_code not in (None, "OFF")
