"""HTML report renderer."""

from importlib.resources import files

from jinja2 import Environment, BaseLoader, select_autoescape

from x32print.models import Scene
from x32print.validator import validate_scene


class HtmlReport:
    name = "html"

    def render(self, scene: Scene) -> str:
        template_text = (
            files("x32print")
            .joinpath("templates/report.html.j2")
            .read_text(encoding="utf-8")
        )
        css = (
            files("x32print")
            .joinpath("templates/report.css")
            .read_text(encoding="utf-8")
        )
        env = Environment(
            loader=BaseLoader(),
            autoescape=select_autoescape(default=True),
        )
        template = env.from_string(template_text)
        warnings = [*scene.warnings, *validate_scene(scene)]
        return template.render(
            scene=scene,
            css=css,
            warnings=list(dict.fromkeys(warnings)),
            version="0.1.0",
        )
