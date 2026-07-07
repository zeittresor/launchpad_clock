# Changelog

## v0.9.4

- Fixed GUI startup crash caused by a missing `QScrollArea` import.
- Installer prompt now explicitly says that the app will auto-start after 10 seconds.
- Version bumped in installer, scripts, and `VERSION` file.

## v0.9.3

- Reduced the default GUI height and preview minimum size.
- Added scrollable tab pages so vertically overflowing content remains usable.
- Added screen-aware initial window sizing based on available desktop geometry.
- Improved usability for 1920×1080 and 2560×1080 displays with a Windows taskbar.

## v0.9.2

- Installer language changed to English.
- App default language changed to English.
- README cleaned up for end users; changelog moved to `docs/CHANGELOG.md`.
- Added localized UI tooltips for the main controls.
- Version remains visible in the installer title, header, and status output.
- Hidden `REM` source comments remain in the installer.

## v0.9.1

- Installer shows the version number.
- Added hidden `REM` source comment in `install_windows.bat`.
- Added `VERSION` file.

## v0.9.0

- Renamed project to **Launchpad Clock**.
- Renamed Python package to `launchpad_clock`.
- Added MIT License.
- Added legal disclaimer and notice about Novation/trademark independence.

## v0.8.x

- Added selectable large digit styles.
- Improved large hour/minute switch display.
- Installer starts GUI automatically after setup.

## v0.7.x

- Added large hour/minute switch mode.

## v0.6.x

- Added normal digit rendering and optional Roman mode.

## Earlier versions

- Initial PyQt6 GUI, MIDI detection, preview mode, sounds, themes, languages, and macro row.
