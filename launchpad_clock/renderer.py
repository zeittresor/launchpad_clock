"""8x8 renderer for the Launchpad clock."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from .roman import to_roman

Matrix = List[List[str]]
WIDTH = 8
HEIGHT = 8

# Matrix tokens:
# "." = off
# "*" = compact digit pixel
# "O" = compact overlap pixel
# "-" = compact separator pixel
# "h" = large hour pixel
# "m" = large minute pixel
# Roman letters are kept only for the optional Roman preview mode.

COMPACT_DIGIT_5X3 = {
    "0": ("11111", "10001", "11111"),
    "1": ("00100", "00100", "00100"),
    "2": ("11111", "00111", "11100"),
    "3": ("11111", "00111", "11111"),
    "4": ("10001", "11111", "00001"),
    "5": ("11111", "11100", "00111"),
    "6": ("11111", "11100", "11111"),
    "7": ("11111", "00010", "00100"),
    "8": ("11111", "11111", "11111"),
    "9": ("11111", "11111", "00001"),
}

# Default: clear, high-contrast 3x7 digits with two dark columns between both digits.
# Placement: tens x=0..2, ones x=5..7, gap x=3..4.
LARGE_DIGIT_CLEAR_3X7 = {
    "0": ("111", "101", "101", "101", "101", "101", "111"),
    "1": ("010", "110", "010", "010", "010", "010", "111"),
    "2": ("111", "001", "001", "111", "100", "100", "111"),
    "3": ("111", "001", "001", "111", "001", "001", "111"),
    "4": ("101", "101", "101", "111", "001", "001", "001"),
    "5": ("111", "100", "100", "111", "001", "001", "111"),
    "6": ("111", "100", "100", "111", "101", "101", "111"),
    "7": ("111", "001", "001", "010", "010", "010", "010"),
    "8": ("111", "101", "101", "111", "101", "101", "111"),
    "9": ("111", "101", "101", "111", "001", "001", "111"),
}

# Slim style: more open and less filled, good if the LEDs bleed into each other.
LARGE_DIGIT_SLIM_3X7 = {
    "0": ("111", "101", "101", "101", "101", "101", "111"),
    "1": ("010", "010", "010", "010", "010", "010", "010"),
    "2": ("111", "001", "001", "111", "100", "100", "111"),
    "3": ("111", "001", "001", "011", "001", "001", "111"),
    "4": ("101", "101", "101", "111", "001", "001", "001"),
    "5": ("111", "100", "100", "111", "001", "001", "111"),
    "6": ("111", "100", "100", "111", "101", "101", "111"),
    "7": ("111", "001", "001", "010", "010", "010", "010"),
    "8": ("111", "101", "101", "111", "101", "101", "111"),
    "9": ("111", "101", "101", "111", "001", "001", "111"),
}

# Wide style: each digit is 4 columns wide. It uses all 8 columns, no hard center gap.
# This gives more lit pads, but adjacent horizontal segments can visually merge.
LARGE_DIGIT_WIDE_4X7 = {
    "0": ("1111", "1001", "1001", "1001", "1001", "1001", "1111"),
    "1": ("0110", "0010", "0010", "0010", "0010", "0010", "1111"),
    "2": ("1111", "0001", "0001", "1111", "1000", "1000", "1111"),
    "3": ("1111", "0001", "0001", "1111", "0001", "0001", "1111"),
    "4": ("1001", "1001", "1001", "1111", "0001", "0001", "0001"),
    "5": ("1111", "1000", "1000", "1111", "0001", "0001", "1111"),
    "6": ("1111", "1000", "1000", "1111", "1001", "1001", "1111"),
    "7": ("1111", "0001", "0001", "0010", "0010", "0100", "0100"),
    "8": ("1111", "1001", "1001", "1111", "1001", "1001", "1111"),
    "9": ("1111", "1001", "1001", "1111", "0001", "0001", "1111"),
}

LARGE_DIGIT_STYLES = {
    "clear_3x7": (LARGE_DIGIT_CLEAR_3X7, [0, 5]),
    "slim_3x7": (LARGE_DIGIT_SLIM_3X7, [0, 5]),
    "wide_4x7": (LARGE_DIGIT_WIDE_4X7, [0, 4]),
}


@dataclass(frozen=True)
class Frame:
    matrix: Matrix
    hour_text: str
    minute_text: str
    display_mode: str
    active_part: str = ""


def _centered_text(text: str, width: int = WIDTH) -> str:
    text = text[:width]
    left = (width - len(text)) // 2
    return "." * left + text + "." * (width - left - len(text))


def _compact_digit_pair_rows(value: int) -> list[str]:
    """Render a two-digit value as three 8-cell rows.

    Each digit is 5 cells wide. The second digit starts at x=3, therefore both
    digits overlap in columns 3 and 4. Single pixels become "*"; overlap pixels
    become "O".
    """
    text = f"{value:02d}"[-2:]
    starts = [0, 3]
    count_grid = [[0 for _ in range(WIDTH)] for _ in range(3)]

    for digit, start_x in zip(text, starts):
        pattern = COMPACT_DIGIT_5X3.get(digit, COMPACT_DIGIT_5X3["0"])
        for y, row in enumerate(pattern):
            for dx, bit in enumerate(row):
                x = start_x + dx
                if bit == "1" and 0 <= x < WIDTH:
                    count_grid[y][x] += 1

    rows = []
    for y in range(3):
        chars = []
        for x in range(WIDTH):
            if count_grid[y][x] >= 2:
                chars.append("O")
            elif count_grid[y][x] == 1:
                chars.append("*")
            else:
                chars.append(".")
        rows.append("".join(chars))
    return rows


def _large_digit_pair_rows(value: int, token: str, digit_style: str = "clear_3x7") -> list[str]:
    """Render two large digits into seven 8-cell rows.

    clear_3x7/slim_3x7:
      tens x=0..2, ones x=5..7, gap x=3..4.
    wide_4x7:
      tens x=0..3, ones x=4..7.
    """
    style = LARGE_DIGIT_STYLES.get(digit_style, LARGE_DIGIT_STYLES["clear_3x7"])
    patterns, starts = style

    text = f"{value:02d}"[-2:]
    rows = [["." for _ in range(WIDTH)] for _ in range(7)]

    for digit, start_x in zip(text, starts):
        pattern = patterns.get(digit, patterns["0"])
        for y, row in enumerate(pattern):
            for dx, bit in enumerate(row):
                x = start_x + dx
                if bit == "1" and 0 <= x < WIDTH:
                    rows[y][x] = token

    return ["".join(row) for row in rows]


def _moving_separator(second: int, enabled: bool = True) -> str:
    """Two separator pixels move outside -> inside -> outside."""
    if not enabled:
        return "........"

    path = [0, 1, 2, 3, 3, 2, 1, 0]
    left = path[int(second) % len(path)]
    right = WIDTH - 1 - left
    row = ["."] * WIDTH
    row[left] = "-"
    row[right] = "-"
    return "".join(row)


def build_compact_digit_clock_frame(hour: int, minute: int, second: int, separator_enabled: bool = True) -> Frame:
    hour_rows = _compact_digit_pair_rows(hour)
    minute_rows = _compact_digit_pair_rows(minute)
    rows = [
        "........",
        hour_rows[0],
        hour_rows[1],
        hour_rows[2],
        _moving_separator(second, separator_enabled),
        minute_rows[0],
        minute_rows[1],
        minute_rows[2],
    ]
    return Frame([list(r) for r in rows], f"{hour:02d}", f"{minute:02d}", "digits_compact", "both")


def build_large_switch_digit_frame(
    hour: int,
    minute: int,
    second: int,
    switch_interval_seconds: int = 5,
    large_digit_style: str = "clear_3x7",
) -> Frame:
    """Alternate large hour and large minute over rows 2-8.

    The first matrix row remains free for macros.
    """
    interval = max(1, int(switch_interval_seconds or 5))
    show_hour = ((int(second) // interval) % 2) == 0
    value = hour if show_hour else minute
    token = "h" if show_hour else "m"
    active = "hour" if show_hour else "minute"

    large_rows = _large_digit_pair_rows(value, token, large_digit_style)
    rows = ["........", *large_rows]
    return Frame([list(r) for r in rows], f"{hour:02d}", f"{minute:02d}", "digits_large_switch", active)


def build_roman_clock_frame(hour: int, minute: int, separator_on: bool = True) -> Frame:
    h = to_roman(hour)
    m = to_roman(minute)
    sep = ".--..--." if separator_on else "........"
    rows = [
        "........",
        _centered_text(h),
        _centered_text(h),
        _centered_text(h),
        sep,
        _centered_text(m),
        _centered_text(m),
        _centered_text(m),
    ]
    return Frame([list(r) for r in rows], h, m, "roman", "both")


def build_clock_frame(
    hour: int,
    minute: int,
    second: int = 0,
    display_mode: str = "digits_large_switch",
    separator_enabled: bool = True,
    switch_interval_seconds: int = 5,
    large_digit_style: str = "clear_3x7",
) -> Frame:
    if display_mode == "roman":
        return build_roman_clock_frame(hour, minute, separator_on=separator_enabled)
    if display_mode == "digits_compact":
        return build_compact_digit_clock_frame(hour, minute, second, separator_enabled)
    return build_large_switch_digit_frame(hour, minute, second, switch_interval_seconds, large_digit_style)


def apply_orientation(x: int, y: int, orientation: str) -> Tuple[int, int]:
    if orientation == "normal":
        return x, y
    if orientation == "rot90":
        return HEIGHT - 1 - y, x
    if orientation == "rot180":
        return WIDTH - 1 - x, HEIGHT - 1 - y
    if orientation == "rot270":
        return y, WIDTH - 1 - x
    return x, y


def oriented_matrix(matrix: Matrix, orientation: str) -> Matrix:
    out = [["." for _ in range(WIDTH)] for _ in range(HEIGHT)]
    for y in range(HEIGHT):
        for x in range(WIDTH):
            ox, oy = apply_orientation(x, y, orientation)
            out[oy][ox] = matrix[y][x]
    return out


def frame_to_console(frame: Frame, orientation: str = "normal") -> str:
    return "\n".join("".join(r) for r in oriented_matrix(frame.matrix, orientation))
