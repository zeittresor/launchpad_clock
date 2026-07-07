# Launchpad Clock

Launchpad Clock is a small open-source hobby project for Windows/Python/PyQt6.  
It can use a Launchpad-style MIDI controller as a LED clock, live preview display, and optional macro board.

The app also works without a connected device. In that case it starts in live preview mode.

<img width="1081" height="777" alt="time_h" src="https://github.com/user-attachments/assets/f1150cfb-6399-4bbb-adfc-99f2e56c2b8b" />

<img width="1083" height="773" alt="time_m" src="https://github.com/user-attachments/assets/b85f6d49-17ce-4756-a3fe-2d29ce387d60" />

Background:

In the past, I used my Launchpad for its intended purpose, but now it serves as a clock and a function keypad :-)

https://www.youtube.com/watch?v=XmOkz26WWoY

## Quick Start on Windows

```bat
install_windows.bat
run_gui.bat
```

The installer shows the version it is installing and starts the GUI automatically after 10 seconds unless you cancel the prompt.

## Window Size and Scrolling

The app uses a responsive window size and scrollable tabs so it remains usable on Full HD displays with a Windows taskbar and on ultrawide 2560×1080 setups.

## Main Features

- PyQt6 desktop GUI
- Live preview without connected MIDI hardware
- MIDI-Out/MIDI-In selection
- Protection against accidental output to Windows software synthesizers
- Rotatable display: 0°, 90°, 180°, 270°
- Clock based on the Windows system time
- Display modes:
  - Large hour/minute switch
  - Compact normal digits
  - Roman numerals
- Large digit styles:
  - Clear 3×7 with gap
  - Slim 3×7
  - Wide 4×7
- Hour/minute switch interval: 5 s or 10 s
- Optional sounds for second, minute, and hour changes
- Optional macro row
- Themes:
  - Light
  - Dark
  - Sepia
  - Ocean
  - Matrix
  - Hellfire
  - Purple
  - Aurora
- UI languages:
  - English
  - German
  - French
  - Russian

## Display Modes

### Large Hour/Minute Switch

Default mode.  
The app alternates between:

```text
large hour in green
large minute in yellow
```

Rows 2–8 of the 8×8 matrix are used for the large display.  
The first matrix row stays free or can optionally be used as a macro row.

### Compact Normal Digits

Shows hour and minute at the same time. This is more compact, but less readable on an 8×8 matrix.

### Roman Numerals

Experimental mode kept for completeness. On real LED hardware it is usually less readable than the large digit mode.

## Macros

In the **Macros** tab, the first matrix row can optionally be used as an 8-button macro row.

Examples:

```bat
notepad.exe
calc.exe
C:\Tools\my_script.bat
powershell.exe -ExecutionPolicy Bypass -File "C:\Tools\diagnostics.ps1"
python "C:\Tools\my_script.py"
```

Macros are executed locally on your Windows PC. Only configure commands and scripts you trust.

## MIDI Output Safety

By default, the app refuses software synthesizers such as `Microsoft GS Wavetable Synth`.  
Non-Launchpad MIDI output can be allowed explicitly in the Options tab, but is disabled by default.

## Legal Notice

This project is unofficial, non-commercial, not developed by Novation, not supported by Novation, and not affiliated with Novation.

`Launchpad`, `Novation`, and other product or brand names belong to their respective owners. They are used only descriptively so users can understand what type of MIDI hardware this project is intended for.

Users are responsible for respecting all relevant copyrights, trademarks, software licenses, device documentation, firmware/driver terms, and other third-party rights.

## License

This project is released under the **MIT License**.  
See `LICENSE`.

## Project Status

Hobby/experimental project.  
No warranty is provided for function, compatibility, or suitability for any specific purpose.

## Source / Updates

Original source / updates: `github.com/zeittresor`
