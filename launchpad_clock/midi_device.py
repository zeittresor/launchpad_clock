"""MIDI input/output helpers for Novation Launchpad devices."""

from __future__ import annotations

from typing import Dict, Optional, Tuple
import time

import mido

from .renderer import apply_orientation

DEFAULT_CLASSIC_COLORS = {"off": 0, "green": 48, "yellow": 62, "dim": 16}
DEFAULT_MK3_COLORS = {"off": 0, "green": 21, "yellow": 13, "dim": 17}

BLOCKED_SOFTWARE_SYNTH_KEYWORDS = [
    "microsoft gs wavetable",
    "midi mapper",
    "fluidsynth",
    "timidity",
    "wavetable synth",
]
LAUNCHPAD_KEYWORDS = ["launchpad", "novation"]


def is_launchpad_port(name: str) -> bool:
    low = name.lower()
    return any(k in low for k in LAUNCHPAD_KEYWORDS)


def is_blocked_software_synth(name: str) -> bool:
    low = name.lower()
    return any(k in low for k in BLOCKED_SOFTWARE_SYNTH_KEYWORDS)


class LaunchpadMidi:
    def __init__(
        self,
        port_name: Optional[str] = None,
        profile: str = "classic",
        orientation: str = "normal",
        color_values: Optional[Dict[str, int]] = None,
        allow_non_launchpad: bool = False,
    ) -> None:
        self.profile_name = profile
        self.orientation = orientation
        self.color_values = dict(DEFAULT_CLASSIC_COLORS if profile == "classic" else DEFAULT_MK3_COLORS)
        if color_values:
            self.color_values.update({k: int(v) for k, v in color_values.items()})

        self.port_name = self.choose_output_port(port_name, allow_non_launchpad)
        self.out = mido.open_output(self.port_name)

    @staticmethod
    def list_output_ports() -> list[str]:
        try:
            return mido.get_output_names()
        except Exception:
            return []

    @staticmethod
    def list_input_ports() -> list[str]:
        try:
            return mido.get_input_names()
        except Exception:
            return []

    @classmethod
    def choose_output_port(cls, requested: Optional[str], allow_non_launchpad: bool = False) -> str:
        ports = cls.list_output_ports()
        if not ports:
            raise RuntimeError("No MIDI output ports found.")

        if requested:
            for port in ports:
                if requested.lower() in port.lower():
                    if not allow_non_launchpad and (
                        not is_launchpad_port(port) or is_blocked_software_synth(port)
                    ):
                        raise RuntimeError(f"Refusing non-Launchpad/software-synth MIDI output: {port}")
                    return port
            raise RuntimeError(f"Requested MIDI output port not found: {requested}")

        for port in ports:
            if is_launchpad_port(port):
                return port

        if allow_non_launchpad:
            for port in ports:
                if not is_blocked_software_synth(port):
                    return port

        raise RuntimeError("No Launchpad/Novation MIDI output port found.")

    @classmethod
    def choose_input_port(cls, requested: Optional[str]) -> str:
        ports = cls.list_input_ports()
        if not ports:
            raise RuntimeError("No MIDI input ports found.")

        if requested:
            for port in ports:
                if requested.lower() in port.lower():
                    return port
            raise RuntimeError(f"Requested MIDI input port not found: {requested}")

        for port in ports:
            if is_launchpad_port(port):
                return port

        return ports[0]

    def close(self) -> None:
        try:
            self.all_off()
        finally:
            try:
                self.out.close()
            except Exception:
                pass

    def _color(self, name: str) -> int:
        return int(self.color_values.get(name, 0))

    def grid_note(self, x: int, y: int) -> int:
        x2, y2 = apply_orientation(x, y, self.orientation)

        if self.profile_name == "classic":
            return (7 - y2) * 16 + x2

        return (8 - y2) * 10 + (x2 + 1)

    def note_to_logical_xy(self, note: int) -> Optional[Tuple[int, int]]:
        for y in range(8):
            for x in range(8):
                if self.grid_note(x, y) == note:
                    return x, y
        return None

    def _top_button_cc(self, index: int) -> int:
        return 104 + index if self.profile_name == "classic" else 91 + index

    def _oriented_top_button_index(self, index: int) -> int:
        return 7 - index if self.orientation in ("rot180", "rot270") else index

    def set_pad(self, x: int, y: int, color: str) -> None:
        self.out.send(
            mido.Message("note_on", note=self.grid_note(x, y), velocity=self._color(color), channel=0)
        )

    def set_top_button(self, index: int, color: str) -> None:
        cc = self._top_button_cc(self._oriented_top_button_index(index))
        self.out.send(mido.Message("control_change", control=cc, value=self._color(color), channel=0))

    def all_off(self) -> None:
        for y in range(8):
            for x in range(8):
                self.set_pad(x, y, "off")
        for i in range(8):
            self.set_top_button(i, "off")

    def _token_color(
        self,
        token: str,
        y: int,
        hour_color: str,
        minute_color: str,
        large_hour_color: str,
        large_minute_color: str,
        separator_color: str,
        overlap_color: str,
    ) -> str:
        if token == ".":
            return "off"
        if token == "h":
            return large_hour_color
        if token == "m":
            return large_minute_color
        if token == "O":
            return overlap_color
        if token == "-":
            return separator_color
        if y in (1, 2, 3):
            return hour_color
        if y == 4:
            return separator_color
        return minute_color

    def draw_matrix(
        self,
        matrix,
        hour_color: str = "yellow",
        minute_color: str = "yellow",
        large_hour_color: str = "green",
        large_minute_color: str = "yellow",
        separator_color: str = "green",
        overlap_color: str = "green",
        macro_row_enabled: bool = False,
        macro_commands: Optional[list[str]] = None,
        macro_marker_color: str = "dim",
    ) -> None:
        macro_commands = macro_commands or [""] * 8
        for y, row in enumerate(matrix):
            for x, token in enumerate(row):
                if y == 0 and macro_row_enabled and x < len(macro_commands) and macro_commands[x].strip():
                    color = macro_marker_color
                else:
                    color = self._token_color(
                        token, y, hour_color, minute_color, large_hour_color, large_minute_color,
                        separator_color, overlap_color
                    )
                self.set_pad(x, y, color)

    def draw_seconds_progress(self, second: int, done_color: str = "green", current_color: str = "yellow") -> None:
        # 8 fields, field 1 and 8 stay free. Fields 2..7 are six 10-second blocks.
        second = max(0, min(59, int(second)))
        current = second // 10

        for i in range(8):
            if i in (0, 7):
                color = "off"
            else:
                segment = i - 1
                if segment < current:
                    color = done_color
                elif segment == current:
                    color = current_color
                else:
                    color = "off"
            self.set_top_button(i, color)

    def test_pattern(self) -> None:
        self.all_off()
        for y in range(8):
            for x in range(8):
                self.set_pad(x, y, "yellow" if (x + y) % 2 == 0 else "green")
                time.sleep(0.01)
        for i in range(8):
            self.set_top_button(i, "off" if i in (0, 7) else "green")
