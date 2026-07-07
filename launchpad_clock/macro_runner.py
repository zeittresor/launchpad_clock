"""Macro execution helpers."""

from __future__ import annotations

import subprocess
from pathlib import Path


def run_command(command: str) -> subprocess.Popen:
    """Run a user-defined command without blocking the GUI."""
    command = command.strip()
    if not command:
        raise ValueError("Empty command.")

    return subprocess.Popen(
        command,
        shell=True,
        cwd=str(Path.home()),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0),
    )
