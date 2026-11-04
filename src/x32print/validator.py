"""Scene validation rules."""

from collections import Counter

from x32print.models import Scene
from x32print.routing import channel_is_used


def validate_scene(scene: Scene) -> list[str]:
    warnings: list[str] = []
    labels = [channel.label.strip().casefold() for channel in scene.channels if channel.label.strip()]
    duplicates = sorted(label for label, count in Counter(labels).items() if count > 1)
    for label in duplicates:
        warnings.append(f"Duplicate channel label: {label}")

    for channel in scene.channels:
        # Only flag strips someone has clearly set up (colored) but not named.
        if channel_is_used(channel) and not channel.label.strip():
            warnings.append(f"Mixer channel {channel.number} has a colour but a blank label.")

    # Two named strips fed by the same physical socket is usually a patch error.
    by_socket: dict[str, list[str]] = {}
    for channel in [*scene.channels, *scene.aux_inputs]:
        src = channel.source
        if channel_is_used(channel) and src and src.port is not None and src.source_type in ("local", "aes50", "card"):
            kind = "Aux" if channel.kind == "auxin" else "Ch"
            by_socket.setdefault(src.display(), []).append(
                f"{kind} {channel.number} ({channel.label or 'unnamed'})"
            )
    for socket, names in by_socket.items():
        if len(names) > 1:
            warnings.append(f"{socket} feeds more than one channel: {', '.join(names)}")

    return warnings
