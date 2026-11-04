"""Routing interpretation layer.

Keep routing decoding here, not in parser.py. The exact X32 routing token
encoding must be established with real scene fixtures before mapping sources.
"""

from x32print.models import Scene


def decode_input_routing(scene: Scene) -> None:
    """Populate scene.routing.decoded_inputs when the format is verified.

    This starter intentionally does not guess the meaning of routing tokens.
    """
    scene.routing.input_tokens = [
        token
        for payloads in scene.raw_directives.get("/config/routing/IN", [])
        for token in payloads.split()
    ]
