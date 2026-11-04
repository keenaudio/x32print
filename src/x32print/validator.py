"""Scene validation rules."""

from collections import Counter

from x32print.models import Scene


def validate_scene(scene: Scene) -> list[str]:
    warnings: list[str] = []
    labels = [channel.label.strip().casefold() for channel in scene.channels if channel.label.strip()]
    duplicates = sorted(label for label, count in Counter(labels).items() if count > 1)
    for label in duplicates:
        warnings.append(f"Duplicate channel label: {label}")

    for channel in scene.channels:
        if not channel.label.strip():
            warnings.append(f"Mixer channel {channel.number} has a blank label.")

    for bus in scene.buses:
        if not bus.name.strip():
            warnings.append(f"Bus {bus.number} has a blank name.")

    if scene.routing.decoded_inputs:
        source_keys = [
            (source.source_type, source.device, source.port)
            for source in scene.routing.decoded_inputs.values()
        ]
        duplicates = [key for key, count in Counter(source_keys).items() if count > 1]
        for source in duplicates:
            warnings.append(f"Duplicate input routing: {source}")

    return warnings
