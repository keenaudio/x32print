from x32print.models import Scene
from x32print.routing import decode_input_routing


def test_routing_decoder_preserves_tokens_without_guessing():
    scene = Scene(
        name="test",
        raw_directives={"/config/routing/IN": ["AES50A 1-8 LOCAL 1-8"]},
    )
    decode_input_routing(scene)
    assert scene.routing.input_tokens == ["AES50A", "1-8", "LOCAL", "1-8"]
    assert scene.routing.decoded_inputs == {}
