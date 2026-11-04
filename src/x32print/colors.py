"""X32 scribble-strip color mapping.

Scene files store colors as mnemonics: OFF, RD, GN, YE, BL, MG, CY, WH, with
an "i" suffix (e.g. "RDi") for the inverted display variant.
"""

X32_COLORS: dict[str, str] = {
    "OFF": "#bdc3c7",
    "RD": "#e74c3c",
    "GN": "#2ecc71",
    "YE": "#f1c40f",
    "BL": "#3498db",
    "MG": "#d147c8",
    "CY": "#1abcd4",
    "WH": "#ffffff",
}

# Legacy numeric codes (console color index order).
_NUMERIC = ["OFF", "RD", "GN", "YE", "BL", "MG", "CY", "WH"]


def normalize_color(value: str | int | None) -> str:
    """Return the base mnemonic (without inversion suffix)."""
    if value is None:
        return "OFF"
    if isinstance(value, int) or str(value).isdigit():
        index = int(value) % 8
        return _NUMERIC[index]
    code = str(value).strip().upper()
    if code.endswith("I") and code[:-1] in X32_COLORS:
        code = code[:-1]
    return code if code in X32_COLORS else "OFF"


def color_hex(value: str | int | None) -> str:
    """Return a safe display color for a console color code."""
    return X32_COLORS[normalize_color(value)]
