from x32print.parser import parse_scene_text
from x32print.routing import decode_input_routing

SCN = """\
/config/routing/IN A1-8 A9-16 B1-8 AN1-8 AN1-4
/ch/01/config "Kick" 2 WH 1
/ch/10/config "Bass" 17 MG 10
/ch/17/config "Gtr" 17 YE 17
/ch/25/config "Talkback" 1 GN 25
/ch/32/config "USB" 1 CY 39
/auxin/05/config "BT" 55 BL 37
/headamp/032 +30.0 ON
/headamp/041 +12.0 OFF
/headamp/080 +20.0 OFF
"""


def _scene():
    scene = parse_scene_text(SCN)
    decode_input_routing(scene)
    return scene


def test_channels_resolve_to_physical_sockets():
    chans = {c.number: c for c in _scene().channels}
    assert chans[1].source.display() == "AES50 A 01"
    assert chans[1].gain == 30.0 and chans[1].phantom
    assert chans[10].source.display() == "AES50 A 10"
    assert chans[10].gain == 12.0
    assert chans[17].source.display() == "AES50 B 01"
    assert chans[17].gain == 20.0
    assert chans[25].source.display() == "Local 01"
    assert chans[32].source.display() == "USB L"


def test_stageboxes_group_by_device():
    boxes = {b.key: b for b in _scene().stageboxes}
    assert set(boxes) == {"aes50:A", "aes50:B", "local"}
    assert len(boxes["aes50:A"].sockets) == 16
    assert len(boxes["aes50:B"].sockets) == 8
    a1 = boxes["aes50:A"].sockets[0]
    assert [c.label for c in a1.channels] == ["Kick"] and a1.phantom


def test_unused_strip_does_not_create_local_box():
    scene = parse_scene_text(
        "/config/routing/IN A1-8 A9-16 B1-8 B9-16 AN1-4\n"
        '/ch/01/config "Kick" 2 WH 1\n'
        '/auxin/03/config "" 1 OFF 35\n'
    )
    decode_input_routing(scene)
    assert [b.key for b in scene.stageboxes] == ["aes50:A", "aes50:B"]


def test_unknown_block_warns_without_guessing():
    scene = parse_scene_text("/config/routing/IN XYZ A9-16 B1-8 B9-16 AN1-4\n/ch/01/config \"x\" 1 RD 1\n")
    decode_input_routing(scene)
    assert any("XYZ" in w for w in scene.warnings)
    assert scene.channels[0].source.source_type == "unresolved"
