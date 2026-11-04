from x32print.parser import parse_scene


def test_parse_channel_and_bus_directives(tmp_path):
    scene_file = tmp_path / "sample.scn"
    scene_file.write_text(
        '/ch/01/config/name "Lead Vocal"\n'
        '/ch/01/config/color 1\n'
        '/bus/01/config/name "Monitor 1"\n'
        '/config/routing/IN AES50A 1-8\n',
        encoding="utf-8",
    )
    scene = parse_scene(scene_file)
    assert scene.name == "sample"
    assert scene.channels[0].number == 1
    assert scene.channels[0].label == "Lead Vocal"
    assert scene.channels[0].scribble_color == "#f1c40f"
    assert scene.buses[0].name == "Monitor 1"
    assert scene.raw_directives["/config/routing/IN"] == ["AES50A 1-8"]
