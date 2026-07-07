"""Optional sound feedback."""

from __future__ import annotations

import sys
import threading
import time

SOUND_MODES = {
    "none": "Keine / None",
    "soft_tick": "Soft Tick",
    "click": "Click",
    "beep": "Beep",
    "digital": "Digital",
    "chime": "Chime",
    "bell": "Bell",
}


def _win(mode: str) -> None:
    import winsound

    patterns = {
        "soft_tick": [(880, 18)],
        "click": [(1200, 12), (800, 12)],
        "beep": [(880, 80)],
        "digital": [(1000, 35), (1400, 35)],
        "chime": [(660, 80), (880, 120)],
        "bell": [(784, 130), (1046, 180)],
    }

    for freq, duration in patterns.get(mode, []):
        winsound.Beep(int(freq), int(duration))
        time.sleep(0.025)


def play_sound(mode: str) -> None:
    if not mode or mode == "none":
        return

    def worker() -> None:
        try:
            if sys.platform.startswith("win"):
                _win(mode)
            else:
                print("\a", end="", flush=True)
        except Exception:
            pass

    threading.Thread(target=worker, daemon=True).start()
