from x32print.models import Bus, Channel, InputSource, Scene
from x32print.validator import validate_scene


def test_validation_reports_duplicates_and_coloured_blank_labels():
    scene = Scene(
        name="test",
        channels=[Channel(1, "Vocal"), Channel(2, "Vocal"), Channel(3, "", color_code="RD")],
        buses=[Bus(1, "")],
    )
    warnings = validate_scene(scene)
    assert any("Duplicate channel label" in warning for warning in warnings)
    assert any("channel 3" in warning for warning in warnings)


def test_validation_flags_shared_socket():
    src = InputSource("aes50", port=3, device="A")
    scene = Scene(name="t", channels=[Channel(1, "A", source=src), Channel(2, "B", source=src)])
    assert any("AES50 A 03 feeds more than one channel" in w for w in validate_scene(scene))
