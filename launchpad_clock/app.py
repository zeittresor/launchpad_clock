"""Command-line application for Launchpad Clock."""

from __future__ import annotations

import argparse
import signal
import sys
import time
from datetime import datetime

from .midi_device import LaunchpadMidi
from .renderer import build_clock_frame, frame_to_console
from .settings import load_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="LED clock for Launchpad-style MIDI controllers.")
    parser.add_argument("--list-ports", action="store_true")
    parser.add_argument("--port", default=None)
    parser.add_argument("--profile", choices=["classic", "mk3"], default=None)
    parser.add_argument("--orientation", choices=["normal", "rot90", "rot180", "rot270"], default=None)
    parser.add_argument("--display-mode", choices=["digits_large_switch", "digits_compact", "roman"], default=None)
    parser.add_argument("--switch-interval", type=int, choices=[5, 10], default=None)
    parser.add_argument("--large-digit-style", choices=["clear_3x7", "slim_3x7", "wide_4x7"], default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--test", action="store_true")
    parser.add_argument("--allow-non-launchpad", action="store_true")
    return parser


def print_ports() -> None:
    print("MIDI-Ausgabeports:")
    for port in LaunchpadMidi.list_output_ports():
        print(f"  - {port}")
    print()
    print("MIDI-Eingabeports:")
    for port in LaunchpadMidi.list_input_ports():
        print(f"  - {port}")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    cfg = load_config()

    if args.list_ports:
        print_ports()
        return 0

    profile = args.profile or cfg.get("profile", "classic")
    orientation = args.orientation or cfg.get("orientation", "normal")
    display_mode = args.display_mode or cfg.get("display_mode", "digits_large_switch")
    switch_interval = args.switch_interval or int(cfg.get("switch_interval_seconds", 5))
    large_digit_style = args.large_digit_style or cfg.get("large_digit_style", "clear_3x7")
    color_values = cfg.get("classic_color_values" if profile == "classic" else "mk3_color_values", {})
    device = None

    def shutdown(*_: object) -> None:
        if device is not None:
            device.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    if not args.dry_run:
        try:
            device = LaunchpadMidi(
                args.port or cfg.get("output_port") or None,
                profile,
                orientation,
                color_values,
                args.allow_non_launchpad or bool(cfg.get("allow_non_launchpad_output", False)),
            )
            print(f"[OK] MIDI-Out: {device.port_name}")
        except Exception as exc:
            print(f"[FEHLER] {exc}")
            print("Tipp: --dry-run oder --list-ports verwenden.")
            return 1

    if args.test and device is not None:
        device.test_pattern()
        time.sleep(3)
        device.close()
        return 0

    try:
        while True:
            now = datetime.now()
            sep_enabled = (now.second % 2 == 0) if display_mode == "roman" else True
            frame = build_clock_frame(
                now.hour, now.minute, now.second, display_mode, sep_enabled, switch_interval, large_digit_style
            )

            if args.dry_run:
                print()
                print(now.strftime("%H:%M:%S"), f"= {frame.hour_text} / {frame.minute_text} ({display_mode}, {frame.active_part})")
                print(frame_to_console(frame, orientation))
            else:
                device.draw_matrix(
                    frame.matrix,
                    cfg.get("hour_color", "yellow"),
                    cfg.get("minute_color", "yellow"),
                    cfg.get("large_hour_color", "green"),
                    cfg.get("large_minute_color", "yellow"),
                    cfg.get("separator_color", "green"),
                    cfg.get("overlap_color", "green"),
                )
                device.draw_seconds_progress(
                    now.second,
                    cfg.get("seconds_color_done", "green"),
                    cfg.get("seconds_color_current", "yellow"),
                )

            time.sleep(float(cfg.get("refresh_seconds", 1.0)))
    finally:
        if device is not None:
            device.close()

    return 0
