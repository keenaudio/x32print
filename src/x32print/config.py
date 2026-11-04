"""Small configuration defaults; external config-file support is planned."""

from dataclasses import dataclass


@dataclass(slots=True)
class ReportConfig:
    include_inputs: bool = True
    include_stageboxes: bool = True
    include_buses: bool = True
    include_validation: bool = True
    page_size: str = "letter"
    orientation: str = "landscape"
