"""PyQt6 GUI for Launchpad Clock."""

from __future__ import annotations

import sys
from datetime import datetime
from typing import Optional

import mido
from PyQt6.QtCore import QRectF, Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QDoubleSpinBox,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,)

from . import __version__
from .macro_runner import run_command
from .midi_device import LaunchpadMidi, is_launchpad_port
from .renderer import apply_orientation, build_clock_frame
from .settings import load_config, save_config
from .sound import SOUND_MODES, play_sound


BASE_DE = {
    "title": "Launchpad Clock",
    "subtitle": "Open-Source-Hobbyprojekt für Launchpad-artige MIDI-Controller",
    "tab_clock": "Uhr / Vorschau",
    "tab_macros": "Makros",
    "tab_options": "Optionen",
    "device": "Gerät",
    "midi_out": "MIDI-Out",
    "midi_in": "MIDI-In",
    "preview_only": "Nur Vorschau / kein MIDI-Out",
    "refresh_ports": "Ports aktualisieren",
    "connect": "Verbinden",
    "disconnect": "Trennen",
    "profile": "Profil",
    "orientation": "Ansicht drehen",
    "orientation_normal": "0° / normal",
    "orientation_rot90": "90° im Uhrzeigersinn",
    "orientation_rot180": "180°",
    "orientation_rot270": "270° im Uhrzeigersinn",
    "clock": "Uhr",
    "display_mode": "Anzeigemodus",
    "display_large": "Großwechsel Stunde/Minute",
    "display_compact": "Normalzahlen kompakt",
    "display_roman": "Römisch",
    "digit_style": "Ziffernstil",
    "digit_style_clear": "Klar 3x7 mit Abstand",
    "digit_style_slim": "Schmal 3x7",
    "digit_style_wide": "Breit 4x7",
    "switch_interval": "Wechselintervall",
    "start": "Start",
    "stop": "Stop",
    "test": "Testmuster",
    "save": "Einstellungen speichern",
    "colors": "Farben",
    "compact_hour": "Kompakt: Stunde",
    "compact_minute": "Kompakt: Minute",
    "large_hour": "Groß: Stunde",
    "large_minute": "Groß: Minute",
    "separator": "Trenner",
    "overlap": "Kompakt: Überlappung",
    "seconds_done": "Sekunden vergangen",
    "seconds_current": "Sekunden aktuell",
    "macro_marker": "Makro-Markierung",
    "blink": "Römischen Trenner blinken / Kompakt-Trenner animieren",
    "auto_connect": "Beim Start automatisch mit Launchpad verbinden",
    "allow_non_launchpad": "Nicht-Launchpad-MIDI-Out erlauben (kann Töne erzeugen)",
    "refresh": "Refresh",
    "language": "Sprache",
    "theme": "Theme",
    "sound": "Sounds",
    "second_sound": "Sekundenwechsel",
    "minute_sound": "Minutenwechsel",
    "hour_sound": "Stundenwechsel",
    "sound_test": "Sound testen",
    "status_preview": "Kein Launchpad verbunden; Live-Vorschau läuft.",
    "status_connected": "Verbunden. Out: {out_port} | In: {in_port}",
    "status_error": "MIDI-Verbindung fehlgeschlagen: {error}",
    "time_label": "Systemzeit",
    "display_label": "Anzeige",
    "active_hour": "Stunde",
    "active_minute": "Minute",
    "about": "MIT License • Hobbyprojekt • nicht mit Novation verbunden • Quelle/Updates: github.com/zeittresor",
    "saved": "Einstellungen gespeichert.",
    "none": "Keine Auswahl",
    "macro_enable": "Erste, sonst leere Matrixzeile als Makro-Reihe aktivieren",
    "macro_hint": "Pad 1–8 der ersten Matrixzeile kann ein frei definierbares Windows-Programm oder Script starten.",
    "macro_warning": "Makros werden lokal ausgeführt. Nur vertrauenswürdige Befehle/Scripte eintragen.",
    "pad": "Pad",
    "command": "Befehl / Programm / Script",
    "browse": "Auswählen",
    "run": "Test",
    "macro_disabled": "Makro-Reihe ist deaktiviert.",
    "macro_empty": "Für Pad {pad} ist kein Befehl hinterlegt.",
    "macro_executed": "Pad {pad}: gestartet.",
    "macro_error": "Pad {pad}: Fehler: {error}",
    "restart_language": "Sprache wird beim nächsten Start vollständig aktualisiert.",
    "layout_large": "Großwechsel: Zeile 2–8 zeigen abwechselnd Stunde in Grün und Minute in Gelb. Intervall: {interval}s.",
    "layout_compact": "Kompakt: Gelb = Ziffernpixel, Grün = horizontale Überlappung. Schwerer lesbar, aber gleichzeitige HH/MM-Anzeige.",
    "layout_roman": "Römisch: ursprüngliche römische Anzeige. Für echte Launchpad-LEDs nur bedingt lesbar.",
}

BASE_EN = {
    "subtitle": "Open-source hobby project for Launchpad-style MIDI controllers",
    "tab_clock": "Clock / Preview",
    "tab_options": "Options",
    "device": "Device",
    "preview_only": "Preview only / no MIDI out",
    "refresh_ports": "Refresh ports",
    "connect": "Connect",
    "disconnect": "Disconnect",
    "orientation": "Rotate view",
    "orientation_rot90": "90° clockwise",
    "orientation_rot270": "270° clockwise",
    "clock": "Clock",
    "display_mode": "Display mode",
    "display_large": "Large hour/minute switch",
    "display_compact": "Compact normal digits",
    "display_roman": "Roman",
    "digit_style": "Digit style",
    "digit_style_clear": "Clear 3x7 with gap",
    "digit_style_slim": "Slim 3x7",
    "digit_style_wide": "Wide 4x7",
    "switch_interval": "Switch interval",
    "start": "Start",
    "test": "Test pattern",
    "save": "Save settings",
    "colors": "Colors",
    "compact_hour": "Compact: hour",
    "compact_minute": "Compact: minute",
    "large_hour": "Large: hour",
    "large_minute": "Large: minute",
    "separator": "Separator",
    "overlap": "Compact: overlap",
    "seconds_done": "Seconds done",
    "seconds_current": "Current second",
    "macro_marker": "Macro marker",
    "blink": "Blink Roman separator / animate compact separator",
    "auto_connect": "Auto-connect to Launchpad on startup",
    "allow_non_launchpad": "Allow non-Launchpad MIDI out (may create sounds)",
    "language": "Language",
    "sound": "Sounds",
    "second_sound": "Second change",
    "minute_sound": "Minute change",
    "hour_sound": "Hour change",
    "sound_test": "Test sound",
    "status_preview": "No Launchpad connected; live preview is running.",
    "status_connected": "Connected. Out: {out_port} | In: {in_port}",
    "status_error": "MIDI connection failed: {error}",
    "time_label": "System time",
    "display_label": "Display",
    "active_hour": "hour",
    "active_minute": "minute",
    "about": "MIT License • hobby project • not affiliated with Novation • source/updates: github.com/zeittresor",
    "saved": "Settings saved.",
    "none": "None",
    "macro_enable": "Use the first otherwise empty matrix row as macro row",
    "macro_hint": "Pad 1–8 of the first matrix row can launch a freely defined Windows program or script.",
    "macro_warning": "Macros execute locally. Only enter trusted commands/scripts.",
    "command": "Command / program / script",
    "browse": "Browse",
    "macro_disabled": "Macro row is disabled.",
    "macro_empty": "No command configured for pad {pad}.",
    "macro_executed": "Pad {pad}: launched.",
    "macro_error": "Pad {pad}: error: {error}",
    "restart_language": "Language is fully updated after restart.",
    "layout_large": "Large switch: rows 2–8 alternate hour in green and minute in yellow. Interval: {interval}s.",
    "layout_compact": "Compact: yellow = digit pixel, green = horizontal overlap. Less readable, but HH/MM are shown together.",
    "layout_roman": "Roman: original Roman display. Limited readability on real Launchpad LEDs.",
}
BASE_FR = {
    "subtitle": "Projet open source amateur pour contrôleurs MIDI de type Launchpad",
    "tab_clock": "Horloge / Aperçu",
    "tab_options": "Options",
    "device": "Appareil",
    "connect": "Connecter",
    "disconnect": "Déconnecter",
    "orientation": "Rotation",
    "clock": "Horloge",
    "display_mode": "Mode d’affichage",
    "display_large": "Alternance heure/minute",
    "display_compact": "Chiffres compacts",
    "display_roman": "Romain",
    "digit_style": "Style des chiffres",
    "digit_style_clear": "Clair 3x7 avec espace",
    "digit_style_slim": "Fin 3x7",
    "digit_style_wide": "Large 4x7",
    "switch_interval": "Intervalle",
    "save": "Enregistrer",
    "colors": "Couleurs",
    "language": "Langue",
    "theme": "Thème",
    "sound": "Sons",
    "status_preview": "Aucun Launchpad connecté; aperçu actif.",
    "time_label": "Heure système",
    "display_label": "Affichage",
    "none": "Aucun",
    "browse": "Choisir",
}
BASE_RU = {
    "subtitle": "Открытый любительский проект для MIDI-контроллеров типа Launchpad",
    "tab_clock": "Часы / предпросмотр",
    "tab_options": "Настройки",
    "device": "Устройство",
    "connect": "Подключить",
    "disconnect": "Отключить",
    "orientation": "Поворот",
    "clock": "Часы",
    "display_mode": "Режим отображения",
    "display_large": "Час/минута крупно",
    "display_compact": "Компактные цифры",
    "display_roman": "Римские",
    "digit_style": "Стиль цифр",
    "digit_style_clear": "Чёткий 3x7 с промежутком",
    "digit_style_slim": "Тонкий 3x7",
    "digit_style_wide": "Широкий 4x7",
    "switch_interval": "Интервал",
    "save": "Сохранить",
    "colors": "Цвета",
    "language": "Язык",
    "theme": "Тема",
    "sound": "Звуки",
    "status_preview": "Launchpad не подключён; работает предпросмотр.",
    "time_label": "Системное время",
    "display_label": "Вид",
    "none": "Нет",
    "browse": "Выбрать",
}
I18N = {
    "de": BASE_DE,
    "en": {**BASE_DE, **BASE_EN},
    "fr": {**BASE_DE, **BASE_FR},
    "ru": {**BASE_DE, **BASE_RU},
}
BASE_EN_FULL = I18N["en"]

TOOLTIPS = {
    "en": {
        "output_combo": "MIDI output device. Use preview-only if no controller is connected.",
        "input_combo": "MIDI input device used for reading button presses, especially macro row buttons.",
        "refresh_ports_btn": "Reload available MIDI input and output ports.",
        "connect_btn": "Connect to the selected MIDI ports.",
        "disconnect_btn": "Disconnect MIDI ports and turn off the device LEDs.",
        "profile_combo": "Select the MIDI mapping profile. Classic is usually correct for older Launchpad Mini devices.",
        "orientation_combo": "Rotate the LED layout if the device is standing in a different orientation.",
        "start_btn": "Start or resume the live clock display.",
        "stop_btn": "Stop the clock and clear the preview/device LEDs.",
        "test_btn": "Send a simple LED test pattern to the connected device.",
        "display_mode_combo": "Choose how the time is represented on the 8×8 matrix.",
        "large_digit_style_combo": "Choose the shape of the large digit font.",
        "switch_interval_combo": "How often the large display alternates between hour and minute.",
        "blink_check": "Enable animated separators in compact/Roman modes.",
        "refresh_spin": "How often the display is refreshed.",
        "macro_enable_check": "Enable the first matrix row as programmable macro buttons.",
        "auto_connect_check": "Try to connect to a Launchpad-style MIDI device when the app starts.",
        "allow_non_launchpad_check": "Allow output to non-Launchpad MIDI devices. Keep off to avoid software synth sounds.",
        "theme_combo": "Change the app color theme.",
        "lang_combo": "Change the UI language. A restart applies it fully.",
        "save_btn": "Save the current settings to config.json.",
    },
    "de": {
        "output_combo": "MIDI-Ausgabegerät. Nutze Nur Vorschau, wenn kein Controller angeschlossen ist.",
        "input_combo": "MIDI-Eingabegerät zum Lesen von Tastendrücken, besonders für Makro-Tasten.",
        "refresh_ports_btn": "Verfügbare MIDI-Ein- und Ausgänge neu laden.",
        "connect_btn": "Mit den ausgewählten MIDI-Ports verbinden.",
        "disconnect_btn": "MIDI-Verbindung trennen und LEDs am Gerät ausschalten.",
        "profile_combo": "MIDI-Mapping-Profil wählen. Classic passt meist für ältere Launchpad Mini Geräte.",
        "orientation_combo": "LED-Layout drehen, falls das Gerät anders herum aufgestellt ist.",
        "start_btn": "Live-Uhr starten oder fortsetzen.",
        "stop_btn": "Uhr stoppen und Vorschau/Geräte-LEDs löschen.",
        "test_btn": "Ein einfaches LED-Testmuster an das verbundene Gerät senden.",
        "display_mode_combo": "Auswählen, wie die Uhrzeit auf der 8×8-Matrix dargestellt wird.",
        "large_digit_style_combo": "Form der großen Ziffern auswählen.",
        "switch_interval_combo": "Wie oft die große Anzeige zwischen Stunde und Minute wechselt.",
        "blink_check": "Animierte Trenner in Kompakt-/Römisch-Modus aktivieren.",
        "refresh_spin": "Wie oft die Anzeige aktualisiert wird.",
        "macro_enable_check": "Die erste Matrixzeile als programmierbare Makro-Tasten aktivieren.",
        "auto_connect_check": "Beim Start versuchen, ein Launchpad-artiges MIDI-Gerät zu verbinden.",
        "allow_non_launchpad_check": "Ausgabe an Nicht-Launchpad-MIDI-Geräte erlauben. Aus lassen, um Software-Synth-Töne zu vermeiden.",
        "theme_combo": "Farbschema der App ändern.",
        "lang_combo": "UI-Sprache ändern. Ein Neustart übernimmt sie vollständig.",
        "save_btn": "Aktuelle Einstellungen in config.json speichern.",
    },
    "fr": {
        "output_combo": "Périphérique de sortie MIDI. Utilisez l’aperçu seul si aucun contrôleur n’est connecté.",
        "input_combo": "Entrée MIDI utilisée pour lire les boutons, surtout la rangée de macros.",
        "refresh_ports_btn": "Recharger les ports MIDI disponibles.",
        "connect_btn": "Se connecter aux ports MIDI sélectionnés.",
        "disconnect_btn": "Déconnecter les ports MIDI et éteindre les LED.",
        "profile_combo": "Choisir le profil de mappage MIDI.",
        "orientation_combo": "Faire pivoter l’affichage LED selon l’orientation du contrôleur.",
        "start_btn": "Démarrer ou reprendre l’horloge.",
        "stop_btn": "Arrêter l’horloge et effacer l’aperçu/les LED.",
        "test_btn": "Envoyer un motif de test LED au périphérique connecté.",
        "display_mode_combo": "Choisir le mode d’affichage de l’heure.",
        "large_digit_style_combo": "Choisir la forme des grands chiffres.",
        "switch_interval_combo": "Intervalle d’alternance entre heure et minute.",
        "blink_check": "Activer les séparateurs animés.",
        "refresh_spin": "Fréquence de rafraîchissement de l’affichage.",
        "macro_enable_check": "Utiliser la première rangée comme boutons macro.",
        "auto_connect_check": "Essayer de se connecter automatiquement au démarrage.",
        "allow_non_launchpad_check": "Autoriser les sorties MIDI non Launchpad. À laisser désactivé pour éviter les sons de synthé logiciel.",
        "theme_combo": "Changer le thème visuel.",
        "lang_combo": "Changer la langue de l’interface. Redémarrage recommandé.",
        "save_btn": "Enregistrer les paramètres dans config.json.",
    },
    "ru": {
        "output_combo": "MIDI-выход. Используйте только предпросмотр, если контроллер не подключён.",
        "input_combo": "MIDI-вход для считывания нажатий, особенно кнопок макро-ряда.",
        "refresh_ports_btn": "Обновить список MIDI-портов.",
        "connect_btn": "Подключиться к выбранным MIDI-портам.",
        "disconnect_btn": "Отключить MIDI-порты и выключить LED.",
        "profile_combo": "Выбрать профиль MIDI-разметки.",
        "orientation_combo": "Повернуть LED-раскладку под ориентацию устройства.",
        "start_btn": "Запустить или продолжить часы.",
        "stop_btn": "Остановить часы и очистить предпросмотр/LED.",
        "test_btn": "Отправить тестовый LED-рисунок на устройство.",
        "display_mode_combo": "Выбрать способ отображения времени.",
        "large_digit_style_combo": "Выбрать форму крупных цифр.",
        "switch_interval_combo": "Интервал переключения между часом и минутой.",
        "blink_check": "Включить анимированные разделители.",
        "refresh_spin": "Частота обновления дисплея.",
        "macro_enable_check": "Использовать первый ряд матрицы как макро-кнопки.",
        "auto_connect_check": "Автоматически подключаться при запуске.",
        "allow_non_launchpad_check": "Разрешить не-Launchpad MIDI-выход. Оставьте выключенным, чтобы избежать звуков софт-синтезатора.",
        "theme_combo": "Изменить тему приложения.",
        "lang_combo": "Изменить язык интерфейса. Полностью применяется после перезапуска.",
        "save_btn": "Сохранить настройки в config.json.",
    },
}

THEMES = {
    "dark": {"bg": "#20242b", "panel": "#2b3038", "fg": "#e8eaed", "muted": "#aab0ba", "button": "#3b424d", "border": "#596170", "off": "#33373f"},
    "light": {"bg": "#f2f2f2", "panel": "#ffffff", "fg": "#1f2328", "muted": "#5b6470", "button": "#e5e7eb", "border": "#b8bec8", "off": "#d5d7dc"},
    "sepia": {"bg": "#2b241a", "panel": "#3b3022", "fg": "#f4e3c1", "muted": "#c7ad82", "button": "#57462f", "border": "#8b724c", "off": "#443827"},
    "ocean": {"bg": "#071923", "panel": "#0e2835", "fg": "#d7f4ff", "muted": "#7fb8cc", "button": "#17394a", "border": "#2b7791", "off": "#15303b"},
    "matrix": {"bg": "#07110a", "panel": "#0d1c12", "fg": "#c8ffd2", "muted": "#75b980", "button": "#17331f", "border": "#2f7a3c", "off": "#112016"},
    "hellfire": {"bg": "#1d0b08", "panel": "#30120c", "fg": "#ffe1cf", "muted": "#d99a75", "button": "#512014", "border": "#a94b27", "off": "#3a1710"},
    "purple": {"bg": "#170d25", "panel": "#25163b", "fg": "#f1e7ff", "muted": "#bfa4e8", "button": "#3a2359", "border": "#7f5bb7", "off": "#2c1b42"},
    "aurora": {"bg": "#06141f", "panel": "#0b2331", "fg": "#d8fff7", "muted": "#81d7c8", "button": "#12384a", "border": "#33a58d", "off": "#102633"},
}

PREVIEW_COLORS = {
    "off": "#2b2e33",
    "green": "#48ff35",
    "yellow": "#ffd84a",
    "dim": "#7d828c",
}


class PreviewCanvas(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.matrix = [["." for _ in range(8)] for _ in range(8)]
        self.second = 0
        self.orientation = "normal"
        self.colors = {
            "hour": "yellow",
            "minute": "yellow",
            "large_hour": "green",
            "large_minute": "yellow",
            "separator": "green",
            "overlap": "green",
            "done": "green",
            "current": "yellow",
            "macro": "dim",
        }
        self.macro_enabled = False
        self.macro_commands = [""] * 8
        self.theme_off = "#33373f"
        self.setMinimumSize(390, 390)

    def set_theme_off(self, color: str) -> None:
        self.theme_off = color
        self.update()

    def set_frame(
        self,
        matrix,
        second: int,
        orientation: str,
        colors: dict,
        macro_enabled: bool,
        macro_commands: list[str],
    ) -> None:
        self.matrix = matrix
        self.second = int(second)
        self.orientation = orientation
        self.colors.update(colors)
        self.macro_enabled = macro_enabled
        self.macro_commands = macro_commands
        self.update()

    def clear(self) -> None:
        self.matrix = [["." for _ in range(8)] for _ in range(8)]
        self.update()

    def _token_color(self, token: str, y: int) -> str:
        if token == ".":
            return "off"
        if token == "h":
            return self.colors["large_hour"]
        if token == "m":
            return self.colors["large_minute"]
        if token == "O":
            return self.colors["overlap"]
        if token == "-":
            return self.colors["separator"]
        if y in (1, 2, 3):
            return self.colors["hour"]
        if y == 4:
            return self.colors["separator"]
        return self.colors["minute"]

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()
        margin = 12
        gap = 6
        top_height = 38
        available_width = width - 2 * margin
        available_height = height - 2 * margin - top_height - 18
        cell = min((available_width - 7 * gap) / 8, (available_height - 7 * gap) / 8)
        cell = max(16, cell)

        grid_width = cell * 8 + gap * 7
        x0 = (width - grid_width) / 2
        y0 = margin + top_height + 18

        radius = min(18, cell * 0.34)
        sec_y = margin + top_height / 2
        current_segment = max(0, min(5, self.second // 10))

        for i in range(8):
            cx = x0 + i * (cell + gap) + cell / 2
            if i in (0, 7):
                name = "off"
                text = ""
            else:
                segment = i - 1
                if segment < current_segment:
                    name = self.colors["done"]
                elif segment == current_segment:
                    name = self.colors["current"]
                else:
                    name = "off"
                text = str(segment * 10)

            painter.setBrush(QColor(PREVIEW_COLORS.get(name, self.theme_off)))
            painter.setPen(QPen(QColor("#111111"), 1))
            painter.drawEllipse(QRectF(cx - radius, sec_y - radius, 2 * radius, 2 * radius))
            if text:
                painter.setPen(QColor("#101010" if name != "off" else "#777777"))
                painter.setFont(QFont("Segoe UI", max(7, int(radius * 0.55)), QFont.Weight.Bold))
                painter.drawText(QRectF(cx - radius, sec_y - radius, 2 * radius, 2 * radius), Qt.AlignmentFlag.AlignCenter, text)

        oriented_chars = [["." for _ in range(8)] for _ in range(8)]
        oriented_colors = [["off" for _ in range(8)] for _ in range(8)]

        for y in range(8):
            for x in range(8):
                token = self.matrix[y][x]
                if y == 0 and self.macro_enabled and x < len(self.macro_commands) and self.macro_commands[x].strip():
                    color = self.colors["macro"]
                    draw_token = str(x + 1)
                else:
                    color = self._token_color(token, y)
                    draw_token = token

                ox, oy = apply_orientation(x, y, self.orientation)
                oriented_chars[oy][ox] = draw_token
                oriented_colors[oy][ox] = color

        for y in range(8):
            for x in range(8):
                token = oriented_chars[y][x]
                name = oriented_colors[y][x]
                rect = QRectF(x0 + x * (cell + gap), y0 + y * (cell + gap), cell, cell)
                painter.setBrush(QColor(PREVIEW_COLORS.get(name, self.theme_off)))
                painter.setPen(QPen(QColor("#111111"), 1))
                painter.drawRoundedRect(rect, max(4, cell * 0.10), max(4, cell * 0.10))

                # Only optional Roman/macro labels are drawn. All normal digit modes use LED blocks only.
                if token not in (".", "*", "O", "-", "h", "m"):
                    painter.setPen(QColor("#111111" if name != "off" else "#777777"))
                    painter.setFont(QFont("Segoe UI", max(10, int(cell * 0.45)), QFont.Weight.Black))
                    painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, token)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.cfg = load_config()
        self.lang = self.cfg.get("language", "en") if self.cfg.get("language", "en") in I18N else "en"
        self.t = I18N[self.lang]
        self.device: Optional[LaunchpadMidi] = None
        self.input_port = None
        self.running = True
        self.macro_lines: list[QLineEdit] = []
        self.last_second = None
        self.last_minute = None
        self.last_hour = None

        self.setWindowTitle(f"{self.tr('title')} v{__version__}")
        self.setMinimumSize(760, 560)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_clock)
        self.input_timer = QTimer(self)
        self.input_timer.timeout.connect(self.poll_midi_input)

        self.build_ui()
        self.apply_theme(self.cfg.get("theme", "dark"))
        self.apply_initial_window_size()
        self.populate_ports()

        if self.cfg.get("auto_connect", True):
            self.connect_device(silent=True)

        self.update_clock()
        self.timer.start(int(float(self.cfg.get("refresh_seconds", 1.0)) * 1000))
        self.input_timer.start(40)

    def tr(self, key: str) -> str:
        return self.t.get(key, BASE_EN_FULL.get(key, BASE_DE.get(key, key)))

    def tip(self, key: str) -> str:
        lang_tips = TOOLTIPS.get(self.lang, TOOLTIPS["en"])
        return lang_tips.get(key, TOOLTIPS["en"].get(key, ""))

    def apply_tooltips(self) -> None:
        widget_names = [
            "output_combo", "input_combo", "refresh_ports_btn", "connect_btn", "disconnect_btn",
            "profile_combo", "orientation_combo", "start_btn", "stop_btn", "test_btn",
            "display_mode_combo", "large_digit_style_combo", "switch_interval_combo",
            "blink_check", "refresh_spin", "macro_enable_check", "auto_connect_check",
            "allow_non_launchpad_check", "theme_combo", "lang_combo", "save_btn",
        ]
        for name in widget_names:
            widget = getattr(self, name, None)
            if widget is not None:
                widget.setToolTip(self.tip(name))

        for i, line in enumerate(getattr(self, "macro_lines", []), start=1):
            line.setToolTip(f"{self.tip('macro_enable_check')} #{i}")

    def make_scroll_tab(self, widget: QWidget) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        return scroll

    def apply_initial_window_size(self) -> None:
        screen = QApplication.primaryScreen()
        if screen is None:
            self.resize(1040, 720)
            return

        available = screen.availableGeometry()
        target_w = min(1080, max(860, int(available.width() * 0.82)))
        target_h = min(740, max(600, int(available.height() * 0.82)))
        self.resize(target_w, target_h)

        # Keep the window inside the available desktop area, especially when a taskbar is present.
        x = available.x() + max(0, (available.width() - target_w) // 2)
        y = available.y() + max(0, (available.height() - target_h) // 2)
        self.move(x, y)

    def build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(10, 10, 10, 10)
        outer.setSpacing(7)

        title = QLabel(self.tr("title"))
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        outer.addWidget(title)

        subtitle = QLabel(self.tr("subtitle"))
        outer.addWidget(subtitle)

        self.tabs = QTabWidget()
        outer.addWidget(self.tabs, 1)

        self.clock_tab = QWidget()
        self.macro_tab = QWidget()
        self.options_tab = QWidget()
        self.tabs.addTab(self.make_scroll_tab(self.clock_tab), self.tr("tab_clock"))
        self.tabs.addTab(self.make_scroll_tab(self.macro_tab), self.tr("tab_macros"))
        self.tabs.addTab(self.make_scroll_tab(self.options_tab), self.tr("tab_options"))

        self.build_clock_tab()
        self.build_macro_tab()
        self.build_options_tab()

        self.status_label = QLabel(self.tr("status_preview"))
        self.status_label.setWordWrap(True)
        outer.addWidget(self.status_label)
        outer.addWidget(QLabel(self.tr("about")))

        self.apply_tooltips()

    def build_clock_tab(self) -> None:
        main = QHBoxLayout(self.clock_tab)
        main.setContentsMargins(6, 6, 6, 6)
        main.setSpacing(10)

        left = QVBoxLayout()
        main.addLayout(left, 2)

        self.preview = PreviewCanvas()
        left.addWidget(self.preview, 1)

        bottom_row = QHBoxLayout()
        self.time_label = QLabel()
        self.time_label.setFont(QFont("Consolas", 16, QFont.Weight.Bold))
        self.display_label = QLabel()
        self.display_label.setFont(QFont("Consolas", 16, QFont.Weight.Bold))
        bottom_row.addWidget(self.time_label)
        bottom_row.addStretch(1)
        bottom_row.addWidget(self.display_label)
        left.addLayout(bottom_row)

        self.layout_label = QLabel("")
        self.layout_label.setWordWrap(True)
        left.addWidget(self.layout_label)

        right = QVBoxLayout()
        main.addLayout(right, 1)

        device_group = QGroupBox(self.tr("device"))
        device_layout = QGridLayout(device_group)
        right.addWidget(device_group)

        device_layout.addWidget(QLabel(self.tr("midi_out")), 0, 0)
        self.output_combo = QComboBox()
        device_layout.addWidget(self.output_combo, 0, 1, 1, 2)

        device_layout.addWidget(QLabel(self.tr("midi_in")), 1, 0)
        self.input_combo = QComboBox()
        device_layout.addWidget(self.input_combo, 1, 1, 1, 2)

        self.refresh_ports_btn = QPushButton(self.tr("refresh_ports"))
        self.refresh_ports_btn.clicked.connect(self.populate_ports)
        device_layout.addWidget(self.refresh_ports_btn, 2, 0)

        self.connect_btn = QPushButton(self.tr("connect"))
        self.connect_btn.clicked.connect(lambda: self.connect_device(False))
        device_layout.addWidget(self.connect_btn, 2, 1)

        self.disconnect_btn = QPushButton(self.tr("disconnect"))
        self.disconnect_btn.clicked.connect(self.disconnect_device)
        device_layout.addWidget(self.disconnect_btn, 2, 2)

        device_layout.addWidget(QLabel(self.tr("profile")), 3, 0)
        self.profile_combo = QComboBox()
        self.profile_combo.addItems(["classic", "mk3"])
        self.profile_combo.setCurrentText(self.cfg.get("profile", "classic"))
        self.profile_combo.currentTextChanged.connect(self.on_device_param_changed)
        device_layout.addWidget(self.profile_combo, 3, 1, 1, 2)

        device_layout.addWidget(QLabel(self.tr("orientation")), 4, 0)
        self.orientation_combo = QComboBox()
        for key in ["normal", "rot90", "rot180", "rot270"]:
            self.orientation_combo.addItem(self.tr("orientation_" + key), key)
        idx = self.orientation_combo.findData(self.cfg.get("orientation", "normal"))
        self.orientation_combo.setCurrentIndex(idx if idx >= 0 else 0)
        self.orientation_combo.currentIndexChanged.connect(self.on_device_param_changed)
        device_layout.addWidget(self.orientation_combo, 4, 1, 1, 2)

        clock_group = QGroupBox(self.tr("clock"))
        clock_layout = QGridLayout(clock_group)
        right.addWidget(clock_group)

        self.start_btn = QPushButton(self.tr("start"))
        self.start_btn.clicked.connect(self.start_clock)
        clock_layout.addWidget(self.start_btn, 0, 0)

        self.stop_btn = QPushButton(self.tr("stop"))
        self.stop_btn.clicked.connect(self.stop_clock)
        clock_layout.addWidget(self.stop_btn, 0, 1)

        self.test_btn = QPushButton(self.tr("test"))
        self.test_btn.clicked.connect(self.test_pattern)
        clock_layout.addWidget(self.test_btn, 0, 2)

        clock_layout.addWidget(QLabel(self.tr("display_mode")), 1, 0)
        self.display_mode_combo = QComboBox()
        self.display_mode_combo.addItem(self.tr("display_large"), "digits_large_switch")
        self.display_mode_combo.addItem(self.tr("display_compact"), "digits_compact")
        self.display_mode_combo.addItem(self.tr("display_roman"), "roman")
        idx = self.display_mode_combo.findData(self.cfg.get("display_mode", "digits_large_switch"))
        self.display_mode_combo.setCurrentIndex(idx if idx >= 0 else 0)
        self.display_mode_combo.currentIndexChanged.connect(self.update_clock)
        clock_layout.addWidget(self.display_mode_combo, 1, 1, 1, 2)

        clock_layout.addWidget(QLabel(self.tr("digit_style")), 2, 0)
        self.large_digit_style_combo = QComboBox()
        self.large_digit_style_combo.addItem(self.tr("digit_style_clear"), "clear_3x7")
        self.large_digit_style_combo.addItem(self.tr("digit_style_slim"), "slim_3x7")
        self.large_digit_style_combo.addItem(self.tr("digit_style_wide"), "wide_4x7")
        idx = self.large_digit_style_combo.findData(self.cfg.get("large_digit_style", "clear_3x7"))
        self.large_digit_style_combo.setCurrentIndex(idx if idx >= 0 else 0)
        self.large_digit_style_combo.currentIndexChanged.connect(self.update_clock)
        clock_layout.addWidget(self.large_digit_style_combo, 2, 1, 1, 2)

        clock_layout.addWidget(QLabel(self.tr("switch_interval")), 3, 0)
        self.switch_interval_combo = QComboBox()
        self.switch_interval_combo.addItem("5 s", 5)
        self.switch_interval_combo.addItem("10 s", 10)
        idx = self.switch_interval_combo.findData(int(self.cfg.get("switch_interval_seconds", 5)))
        self.switch_interval_combo.setCurrentIndex(idx if idx >= 0 else 0)
        self.switch_interval_combo.currentIndexChanged.connect(self.update_clock)
        clock_layout.addWidget(self.switch_interval_combo, 3, 1, 1, 2)

        self.blink_check = QCheckBox(self.tr("blink"))
        self.blink_check.setChecked(bool(self.cfg.get("blink", True)))
        self.blink_check.stateChanged.connect(self.update_clock)
        clock_layout.addWidget(self.blink_check, 4, 0, 1, 3)

        clock_layout.addWidget(QLabel(self.tr("refresh")), 5, 0)
        self.refresh_spin = QDoubleSpinBox()
        self.refresh_spin.setRange(0.2, 10.0)
        self.refresh_spin.setDecimals(1)
        self.refresh_spin.setSingleStep(0.1)
        self.refresh_spin.setSuffix(" s")
        self.refresh_spin.setValue(float(self.cfg.get("refresh_seconds", 1.0)))
        self.refresh_spin.valueChanged.connect(lambda: self.timer.setInterval(int(self.refresh_spin.value() * 1000)))
        clock_layout.addWidget(self.refresh_spin, 5, 1, 1, 2)

        right.addStretch(1)

    def build_macro_tab(self) -> None:
        layout = QVBoxLayout(self.macro_tab)
        layout.setContentsMargins(8, 8, 8, 8)
        self.macro_enable_check = QCheckBox(self.tr("macro_enable"))
        self.macro_enable_check.setChecked(bool(self.cfg.get("macro_row_enabled", False)))
        self.macro_enable_check.stateChanged.connect(self.update_clock)
        layout.addWidget(self.macro_enable_check)

        hint = QLabel(self.tr("macro_hint"))
        hint.setWordWrap(True)
        layout.addWidget(hint)

        warning = QLabel(self.tr("macro_warning"))
        warning.setWordWrap(True)
        layout.addWidget(warning)

        grid = QGridLayout()
        layout.addLayout(grid)
        grid.addWidget(QLabel(self.tr("pad")), 0, 0)
        grid.addWidget(QLabel(self.tr("command")), 0, 1)

        commands = list(self.cfg.get("macro_commands", []))[:8] + [""] * 8

        for i in range(8):
            grid.addWidget(QLabel(str(i + 1)), i + 1, 0)

            line = QLineEdit()
            line.setText(commands[i])
            line.setPlaceholderText("notepad.exe / C:\\Tools\\script.bat / powershell.exe ...")
            line.textChanged.connect(self.update_clock)
            self.macro_lines.append(line)
            grid.addWidget(line, i + 1, 1)

            browse_btn = QPushButton(self.tr("browse"))
            browse_btn.clicked.connect(lambda _, idx=i: self.browse_macro(idx))
            grid.addWidget(browse_btn, i + 1, 2)

            run_btn = QPushButton(self.tr("run"))
            run_btn.clicked.connect(lambda _, idx=i: self.execute_macro(idx, True))
            grid.addWidget(run_btn, i + 1, 3)

        layout.addStretch(1)

    def build_options_tab(self) -> None:
        layout = QVBoxLayout(self.options_tab)
        layout.setContentsMargins(8, 8, 8, 8)

        behavior_group = QGroupBox(self.tr("device"))
        behavior_layout = QGridLayout(behavior_group)
        layout.addWidget(behavior_group)

        self.auto_connect_check = QCheckBox(self.tr("auto_connect"))
        self.auto_connect_check.setChecked(bool(self.cfg.get("auto_connect", True)))
        behavior_layout.addWidget(self.auto_connect_check, 0, 0, 1, 2)

        self.allow_non_launchpad_check = QCheckBox(self.tr("allow_non_launchpad"))
        self.allow_non_launchpad_check.setChecked(bool(self.cfg.get("allow_non_launchpad_output", False)))
        behavior_layout.addWidget(self.allow_non_launchpad_check, 1, 0, 1, 2)

        color_group = QGroupBox(self.tr("colors"))
        color_layout = QGridLayout(color_group)
        layout.addWidget(color_group)
        self.color_combos = {}

        color_rows = [
            ("large_hour_color", "large_hour"),
            ("large_minute_color", "large_minute"),
            ("hour_color", "compact_hour"),
            ("minute_color", "compact_minute"),
            ("separator_color", "separator"),
            ("overlap_color", "overlap"),
            ("seconds_color_done", "seconds_done"),
            ("seconds_color_current", "seconds_current"),
            ("macro_marker_color", "macro_marker"),
        ]

        for row, (key, label_key) in enumerate(color_rows):
            color_layout.addWidget(QLabel(self.tr(label_key)), row, 0)
            combo = QComboBox()
            combo.addItems(["green", "yellow", "dim", "off"])
            combo.setCurrentText(self.cfg.get(key, "green"))
            combo.currentTextChanged.connect(self.update_clock)
            color_layout.addWidget(combo, row, 1)
            self.color_combos[key] = combo

        sound_group = QGroupBox(self.tr("sound"))
        sound_layout = QGridLayout(sound_group)
        layout.addWidget(sound_group)
        self.sound_combos = {}

        for row, (key, label_key) in enumerate([
            ("second_sound", "second_sound"),
            ("minute_sound", "minute_sound"),
            ("hour_sound", "hour_sound"),
        ]):
            sound_layout.addWidget(QLabel(self.tr(label_key)), row, 0)
            combo = QComboBox()
            for mode_key, mode_name in SOUND_MODES.items():
                combo.addItem(mode_name, mode_key)
            idx = combo.findData(self.cfg.get(key, "none"))
            combo.setCurrentIndex(idx if idx >= 0 else 0)
            sound_layout.addWidget(combo, row, 1)
            self.sound_combos[key] = combo

            test_btn = QPushButton(self.tr("sound_test"))
            test_btn.clicked.connect(lambda _, c=combo: play_sound(c.currentData()))
            sound_layout.addWidget(test_btn, row, 2)

        ui_group = QGroupBox("UI")
        ui_layout = QGridLayout(ui_group)
        layout.addWidget(ui_group)

        ui_layout.addWidget(QLabel(self.tr("language")), 0, 0)
        self.lang_combo = QComboBox()
        for name, key in [("Deutsch", "de"), ("English", "en"), ("Français", "fr"), ("Русский", "ru")]:
            self.lang_combo.addItem(name, key)
        idx = self.lang_combo.findData(self.lang)
        self.lang_combo.setCurrentIndex(idx if idx >= 0 else 0)
        self.lang_combo.currentIndexChanged.connect(self.on_language_changed)
        ui_layout.addWidget(self.lang_combo, 0, 1)

        ui_layout.addWidget(QLabel(self.tr("theme")), 1, 0)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(list(THEMES.keys()))
        self.theme_combo.setCurrentText(self.cfg.get("theme", "dark"))
        self.theme_combo.currentTextChanged.connect(self.apply_theme)
        ui_layout.addWidget(self.theme_combo, 1, 1)

        self.save_btn = QPushButton(self.tr("save"))
        self.save_btn.clicked.connect(self.save_settings)
        layout.addWidget(self.save_btn)
        layout.addStretch(1)

    def current_orientation(self) -> str:
        return self.orientation_combo.currentData() or "normal"

    def current_display_mode(self) -> str:
        return self.display_mode_combo.currentData() or "digits_large_switch"

    def current_switch_interval(self) -> int:
        return int(self.switch_interval_combo.currentData() or 5)

    def current_large_digit_style(self) -> str:
        return self.large_digit_style_combo.currentData() or "clear_3x7"

    def macro_commands(self) -> list[str]:
        return [line.text() for line in self.macro_lines]

    def current_color_values(self) -> dict:
        return self.cfg.get(
            "classic_color_values" if self.profile_combo.currentText() == "classic" else "mk3_color_values",
            {},
        )

    def preview_colors(self) -> dict:
        return {
            "hour": self.color_combos["hour_color"].currentText(),
            "minute": self.color_combos["minute_color"].currentText(),
            "large_hour": self.color_combos["large_hour_color"].currentText(),
            "large_minute": self.color_combos["large_minute_color"].currentText(),
            "separator": self.color_combos["separator_color"].currentText(),
            "overlap": self.color_combos["overlap_color"].currentText(),
            "done": self.color_combos["seconds_color_done"].currentText(),
            "current": self.color_combos["seconds_color_current"].currentText(),
            "macro": self.color_combos["macro_marker_color"].currentText(),
        }

    def apply_theme(self, name: str) -> None:
        theme = THEMES.get(name, THEMES["dark"])
        if hasattr(self, "preview"):
            self.preview.set_theme_off(theme["off"])

        self.setStyleSheet(f"""
            QWidget {{
                background: {theme['bg']};
                color: {theme['fg']};
                font-family: Segoe UI, Arial;
                font-size: 10pt;
            }}
            QTabWidget::pane {{
                border: 1px solid {theme['border']};
                background: {theme['panel']};
                border-radius: 8px;
            }}
            QTabBar::tab {{
                background: {theme['button']};
                color: {theme['fg']};
                border: 1px solid {theme['border']};
                padding: 7px 12px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }}
            QTabBar::tab:selected {{
                background: {theme['panel']};
                border-bottom: 1px solid {theme['panel']};
            }}
            QScrollArea {{
                background: {theme['bg']};
                border: none;
            }}
            QGroupBox {{
                background: {theme['panel']};
                border: 1px solid {theme['border']};
                border-radius: 8px;
                margin-top: 12px;
                padding: 10px;
                font-weight: bold;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px;
            }}
            QPushButton, QComboBox, QDoubleSpinBox, QSpinBox, QLineEdit {{
                background: {theme['button']};
                color: {theme['fg']};
                border: 1px solid {theme['border']};
                border-radius: 5px;
                padding: 6px;
            }}
            QPushButton:hover {{
                border: 1px solid {theme['fg']};
            }}
            QLineEdit:focus, QComboBox:focus {{
                border: 1px solid {theme['fg']};
            }}
        """)
        self.update_clock()

    def populate_ports(self) -> None:
        current_out = self.cfg.get("output_port", "")
        self.output_combo.clear()
        self.output_combo.addItem(self.tr("preview_only"), "")

        ports = LaunchpadMidi.list_output_ports()
        launchpads = [p for p in ports if is_launchpad_port(p)]
        others = [p for p in ports if p not in launchpads]
        for port in launchpads + others:
            self.output_combo.addItem(port, port)

        idx = self.output_combo.findData(current_out)
        self.output_combo.setCurrentIndex(idx if idx >= 0 else (1 if launchpads else 0))

        current_in = self.cfg.get("input_port", "")
        self.input_combo.clear()
        self.input_combo.addItem(self.tr("none"), "")
        for port in LaunchpadMidi.list_input_ports():
            self.input_combo.addItem(port, port)

        idx = self.input_combo.findData(current_in)
        self.input_combo.setCurrentIndex(idx if idx >= 0 else 0)

    def connect_device(self, silent: bool = False) -> None:
        self.disconnect_device(update_status=False)

        out_port = self.output_combo.currentData() or None
        in_port = self.input_combo.currentData() or None

        if not out_port:
            self.status_label.setText(self.tr("status_preview"))
            return

        try:
            self.device = LaunchpadMidi(
                out_port,
                self.profile_combo.currentText(),
                self.current_orientation(),
                self.current_color_values(),
                self.allow_non_launchpad_check.isChecked(),
            )
            if in_port:
                self.input_port = mido.open_input(LaunchpadMidi.choose_input_port(in_port))

            self.status_label.setText(
                self.tr("status_connected").format(
                    out_port=self.device.port_name,
                    in_port=getattr(self.input_port, "name", self.tr("none")) if self.input_port else self.tr("none"),
                )
            )
            self.update_clock()
        except Exception as exc:
            self.device = None
            self.input_port = None
            self.status_label.setText(self.tr("status_error").format(error=str(exc)))
            if not silent:
                QMessageBox.warning(self, self.tr("device"), self.tr("status_error").format(error=str(exc)))

    def disconnect_device(self, update_status: bool = True) -> None:
        if self.input_port:
            try:
                self.input_port.close()
            except Exception:
                pass
            self.input_port = None

        if self.device:
            try:
                self.device.close()
            except Exception:
                pass
            self.device = None

        if update_status:
            self.status_label.setText(self.tr("status_preview"))

    def on_device_param_changed(self) -> None:
        if self.device:
            self.connect_device(True)
        self.update_clock()

    def start_clock(self) -> None:
        self.running = True
        self.update_clock()

    def stop_clock(self) -> None:
        self.running = False
        self.preview.clear()
        if self.device:
            self.device.all_off()

    def test_pattern(self) -> None:
        if self.device:
            try:
                self.device.test_pattern()
            except Exception as exc:
                QMessageBox.warning(self, self.tr("device"), str(exc))

    def browse_macro(self, index: int) -> None:
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("browse"),
            "",
            "Programs/Scripts (*.exe *.bat *.cmd *.ps1 *.py);;All files (*.*)",
        )
        if file_name:
            self.macro_lines[index].setText(f'"{file_name}"')

    def execute_macro(self, index: int, ignore_enabled: bool = False) -> None:
        if not ignore_enabled and not self.macro_enable_check.isChecked():
            self.status_label.setText(self.tr("macro_disabled"))
            return

        command = self.macro_commands()[index].strip()
        if not command:
            self.status_label.setText(self.tr("macro_empty").format(pad=index + 1))
            return

        try:
            run_command(command)
            self.status_label.setText(self.tr("macro_executed").format(pad=index + 1))
        except Exception as exc:
            self.status_label.setText(self.tr("macro_error").format(pad=index + 1, error=exc))

    def poll_midi_input(self) -> None:
        if not self.input_port or not self.device:
            return

        try:
            for msg in self.input_port.iter_pending():
                if msg.type == "note_on" and getattr(msg, "velocity", 0) > 0:
                    xy = self.device.note_to_logical_xy(int(msg.note))
                    if xy and xy[1] == 0:
                        self.execute_macro(xy[0])
        except Exception as exc:
            self.status_label.setText(self.tr("status_error").format(error=exc))
            try:
                self.input_port.close()
            except Exception:
                pass
            self.input_port = None

    def update_clock(self) -> None:
        if not getattr(self, "running", True) or not hasattr(self, "preview"):
            return

        now = datetime.now()
        display_mode = self.current_display_mode()

        if display_mode == "roman":
            separator_enabled = (now.second % 2 == 0) if self.blink_check.isChecked() else True
        elif display_mode == "digits_compact":
            separator_enabled = self.blink_check.isChecked()
        else:
            separator_enabled = True

        frame = build_clock_frame(
            now.hour,
            now.minute,
            now.second,
            display_mode=display_mode,
            separator_enabled=separator_enabled,
            switch_interval_seconds=self.current_switch_interval(),
            large_digit_style=self.current_large_digit_style(),
        )

        colors = self.preview_colors()
        commands = self.macro_commands()
        macro_enabled = self.macro_enable_check.isChecked()

        self.preview.set_frame(
            frame.matrix,
            now.second,
            self.current_orientation(),
            colors,
            macro_enabled,
            commands,
        )

        if display_mode == "digits_large_switch":
            mode_name = self.tr("display_large")
            active = self.tr("active_hour") if frame.active_part == "hour" else self.tr("active_minute")
            label_suffix = f"{active} {frame.hour_text if frame.active_part == 'hour' else frame.minute_text}"
            self.layout_label.setText(self.tr("layout_large").format(interval=self.current_switch_interval()))
        elif display_mode == "digits_compact":
            mode_name = self.tr("display_compact")
            label_suffix = f"{frame.hour_text}/{frame.minute_text}"
            self.layout_label.setText(self.tr("layout_compact"))
        else:
            mode_name = self.tr("display_roman")
            label_suffix = f"{frame.hour_text}/{frame.minute_text}"
            self.layout_label.setText(self.tr("layout_roman"))

        self.time_label.setText(f"{self.tr('time_label')}: {now.strftime('%H:%M:%S')}")
        self.display_label.setText(f"{self.tr('display_label')}: {mode_name} {label_suffix}")

        if self.last_second is not None and now.second != self.last_second:
            play_sound(self.sound_combos["second_sound"].currentData())
        if self.last_minute is not None and now.minute != self.last_minute:
            play_sound(self.sound_combos["minute_sound"].currentData())
        if self.last_hour is not None and now.hour != self.last_hour:
            play_sound(self.sound_combos["hour_sound"].currentData())

        self.last_second = now.second
        self.last_minute = now.minute
        self.last_hour = now.hour

        if self.device:
            try:
                self.device.draw_matrix(
                    frame.matrix,
                    self.color_combos["hour_color"].currentText(),
                    self.color_combos["minute_color"].currentText(),
                    self.color_combos["large_hour_color"].currentText(),
                    self.color_combos["large_minute_color"].currentText(),
                    self.color_combos["separator_color"].currentText(),
                    self.color_combos["overlap_color"].currentText(),
                    macro_enabled,
                    commands,
                    self.color_combos["macro_marker_color"].currentText(),
                )
                self.device.draw_seconds_progress(
                    now.second,
                    self.color_combos["seconds_color_done"].currentText(),
                    self.color_combos["seconds_color_current"].currentText(),
                )
            except Exception as exc:
                self.status_label.setText(self.tr("status_error").format(error=exc))
                self.disconnect_device(False)

    def on_language_changed(self) -> None:
        self.save_settings(False)
        QMessageBox.information(self, "Info", self.tr("restart_language"))

    def current_snapshot(self) -> dict:
        cfg = dict(self.cfg)
        cfg.update({
            "profile": self.profile_combo.currentText(),
            "output_port": self.output_combo.currentData() or "",
            "input_port": self.input_combo.currentData() or "",
            "orientation": self.current_orientation(),
            "display_mode": self.current_display_mode(),
            "switch_interval_seconds": self.current_switch_interval(),
            "large_digit_style": self.current_large_digit_style(),
            "blink": self.blink_check.isChecked(),
            "refresh_seconds": float(self.refresh_spin.value()),
            "auto_connect": self.auto_connect_check.isChecked(),
            "allow_non_launchpad_output": self.allow_non_launchpad_check.isChecked(),
            "macro_row_enabled": self.macro_enable_check.isChecked(),
            "language": self.lang_combo.currentData() or "de",
            "theme": self.theme_combo.currentText(),
            "macro_commands": self.macro_commands(),
        })

        for key, combo in self.color_combos.items():
            cfg[key] = combo.currentText()
        for key, combo in self.sound_combos.items():
            cfg[key] = combo.currentData()

        return cfg

    def save_settings(self, show_message: bool = True) -> None:
        self.cfg = self.current_snapshot()
        save_config(self.cfg)
        if show_message:
            self.status_label.setText(self.tr("saved"))

    def closeEvent(self, event) -> None:
        self.save_settings(False)
        self.disconnect_device(False)
        event.accept()


def main() -> int:
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
