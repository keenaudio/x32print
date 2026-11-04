from x32print.parser import parse_scene, tokenize


def test_tokenize_handles_quotes():
    assert tokenize('"Mic Vince" 50 YE 1') == ["Mic Vince", "50", "YE", "1"]
    assert tokenize('"" 1 OFF 8') == ["", "1", "OFF", "8"]


def test_parse_real_format_directives(tmp_path):
    scene_file = tmp_path / "sample.scn"
    scene_file.write_text(
        '#4.0# "My Show" "" %000000000 1\n'
        "/config/chlink ON OFF OFF OFF OFF OFF OFF OFF OFF OFF OFF OFF OFF OFF OFF OFF\n"
        '/ch/01/config "Lead Vocal" 50 YE 1\n'
        "/ch/01/preamp -10.5 OFF ON 24 132\n"
        '/ch/02/config "" 1 OFF 2\n'
        '/bus/01/config "Monitor 1" 63 GN\n'
        "/headamp/032 +23.5 ON\n"
        "/config/routing/IN A1-8 A9-16 B1-8 B9-16 AN1-4\n",
        encoding="utf-8",
    )
    scene = parse_scene(scene_file)
    assert scene.name == "My Show"
    ch1 = scene.channels[0]
    assert (ch1.number, ch1.label, ch1.color_code, ch1.source_index) == (1, "Lead Vocal", "YE", 1)
    assert ch1.scribble_color == "#f1c40f"
    assert ch1.linked and scene.channels[1].linked
    assert ch1.trim == -10.5 and ch1.hpf_on and ch1.hpf_freq == 132
    assert scene.buses[0].name == "Monitor 1"
    assert scene.headamps[32].gain == 23.5 and scene.headamps[32].phantom
    assert scene.raw_directives["/config/routing/IN"] == ["A1-8 A9-16 B1-8 B9-16 AN1-4"]
