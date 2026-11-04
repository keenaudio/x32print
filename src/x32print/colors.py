"""X32 scribble-strip color mapping."""

# The numeric mapping is kept isolated because it must be checked against
# console/firmware documentation and real scene fixtures before expansion.
X32_COLORS: dict[int, str] = {
    0: "#bdc3c7",  # default / grey
    1: "#f1c40f",  # yellow
    2: "#2ecc71",  # green
    3: "#3498db",  # cyan/blue
    4: "#9b59b6",  # purple
    5: "#1abc9c",  # turquoise
    6: "#e74c3c",  # red
    7: "#ecf0f1",  # white
}


def color_hex(value: int | None) -> str:
    """Return a safe display color for a console color code."""
    return X32_COLORS.get(value if value is not None else 0, "#bdc3c7")
