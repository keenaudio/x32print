"""Base protocol for report plugins."""

from typing import Protocol

from x32print.models import Scene


class Report(Protocol):
    name: str

    def render(self, scene: Scene) -> str:
        """Render a Scene to a string."""
