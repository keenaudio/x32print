"""Report base class."""

from abc import ABC, abstractmethod

from x32print.models import Scene


class Report(ABC):
    @abstractmethod
    def render(self, scene: Scene) -> str:
        """Render the scene to a string."""
