from x32print.models import Bus, Channel, Scene
from x32print.validator import validate_scene


def test_validation_reports_blank_and_duplicate_labels_and_bus():
    scene = Scene(
        name="test",
        channels=[Channel(1, "Vocal"), Channel(2, "Vocal"), Channel(3, "")],
        buses=[Bus(1, "")],
    )
    warnings = validate_scene(scene)
    assert any("Duplicate channel label" in warning for warning in warnings)
    assert any("channel 3" in warning for warning in warnings)
    assert any("Bus 1" in warning for warning in warnings)
