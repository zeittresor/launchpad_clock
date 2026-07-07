"""Config loading/saving."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config.json"

DEFAULT_CONFIG: Dict[str, Any] = {
    "profile": "classic",
    "output_port": "",
    "input_port": "",
    "orientation": "normal",
    "display_mode": "digits_large_switch",
    "switch_interval_seconds": 5,
    "large_digit_style": "clear_3x7",
    "hour_color": "yellow",
    "minute_color": "yellow",
    "large_hour_color": "green",
    "large_minute_color": "yellow",
    "separator_color": "green",
    "overlap_color": "green",
    "seconds_color_done": "green",
    "seconds_color_current": "yellow",
    "macro_marker_color": "dim",
    "blink": True,
    "refresh_seconds": 1.0,
    "auto_connect": True,
    "allow_non_launchpad_output": False,
    "macro_row_enabled": False,
    "second_sound": "none",
    "minute_sound": "none",
    "hour_sound": "none",
    "language": "en",
    "theme": "dark",
    "macro_commands": [""] * 8,
    "classic_color_values": {"off": 0, "green": 48, "yellow": 62, "dim": 16},
    "mk3_color_values": {"off": 0, "green": 21, "yellow": 13, "dim": 17},
}


def load_config() -> Dict[str, Any]:
    cfg = dict(DEFAULT_CONFIG)
    if CONFIG_PATH.exists():
        try:
            loaded = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            cfg.update(loaded)
        except Exception:
            pass

    commands = list(cfg.get("macro_commands", []))[:8]
    commands += [""] * (8 - len(commands))
    cfg["macro_commands"] = commands

    if cfg.get("display_mode") not in ("digits_large_switch", "digits_compact", "roman"):
        cfg["display_mode"] = "digits_large_switch"

    if cfg.get("large_digit_style") not in ("clear_3x7", "slim_3x7", "wide_4x7"):
        cfg["large_digit_style"] = "clear_3x7"

    try:
        interval = int(cfg.get("switch_interval_seconds", 5))
    except Exception:
        interval = 5
    cfg["switch_interval_seconds"] = 10 if interval >= 10 else 5

    return cfg


def save_config(cfg: Dict[str, Any]) -> None:
    merged = dict(DEFAULT_CONFIG)
    merged.update(cfg)

    commands = list(merged.get("macro_commands", []))[:8]
    commands += [""] * (8 - len(commands))
    merged["macro_commands"] = commands

    CONFIG_PATH.write_text(json.dumps(merged, indent=2, ensure_ascii=False), encoding="utf-8")
