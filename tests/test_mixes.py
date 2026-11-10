from x32print.mixes import build_mix_matrix, fmt_pan
from x32print.parser import parse_scene_text

SCN = """\
/config/buslink OFF OFF OFF OFF ON OFF OFF OFF
/ch/01/config "Vox" 50 YE 1
/ch/01/mix/01 ON  +4.0 -100 PRE 0
/ch/01/mix/02 ON  -1.5
/ch/01/mix/03 OFF  -3.0 +0 PRE 0
/ch/01/mix/09 ON  -5.0 -40 POST 0
/ch/01/mix/10 ON  -5.0
/ch/02/config "Gtr" 17 GN 2
/ch/02/mix/01 ON   -oo +0 PRE 0
/ch/02/mix/02 ON  -7.0
/ch/03/config "Spare" 1 OFF 3
/ch/03/mix/01 OFF   -oo +0 PRE 0
/bus/01/config "Mon 1" 63 YE
/bus/02/config "Mon 2" 63 GN
/bus/03/config "" 1 OFF
/bus/04/config "" 1 OFF
/bus/09/config "Keys L" 33 RD
/bus/10/config "Keys R" 33 RD
"""


def test_sends_parsed_with_inherited_tap():
    scene = parse_scene_text(SCN)
    ch1 = scene.channels[0]
    assert ch1.sends[1].on and ch1.sends[1].level == 4.0 and ch1.sends[1].tap == "PRE"
    assert ch1.sends[2].tap == "PRE"  # even bus inherits tap from odd partner
    assert ch1.sends[1].pan == -100
    assert not ch1.sends[3].active  # switched off
    assert not scene.channels[1].sends[1].active  # on but -oo
    assert [b.linked for b in scene.buses] == [False, False, False, False, True, True]


def test_matrix_columns_rows_and_linked_buses():
    matrix = build_mix_matrix(parse_scene_text(SCN))
    assert [c.label for c in matrix.columns] == ["Bus 01", "Bus 02", "Bus 09–10"]
    keys = matrix.columns[2]
    assert keys.stereo and keys.name == "Keys L / Keys R" and keys.tap == "POST"
    assert [r.strip.label for r in matrix.rows] == ["Vox", "Gtr"]
    vox, gtr = matrix.rows
    assert [c.level if c else None for c in vox.cells] == [4.0, -1.5, -5.0]
    assert gtr.cells[0] is None and gtr.cells[1].level == -7.0


def test_fmt_pan():
    assert [fmt_pan(v) for v in (-100, 0, 40, None)] == ["L100", "C", "R40", ""]
