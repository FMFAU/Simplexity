import sys
import subprocess
import importlib
import re
import math
import json
import os

required_modules = [
    "PyQt6",
    "pynput",
    "pystray",
    "PIL"
]

def install_missing_packages():
    missing = []
    for mod in required_modules:
        try:
            importlib.import_module(mod)
        except ImportError:
            missing.append(mod.lower())
    if missing:
        print(f"Installing missing packages: {', '.join(missing)}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])

install_missing_packages()

import urllib.parse
import webbrowser
from PyQt6.QtCore import Qt, QTimer, QEvent, QSize, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QColor, QFont, QPalette, QIcon, QPainter, QPen, QBrush
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLineEdit, QVBoxLayout, QHBoxLayout, QLabel,
    QGraphicsDropShadowEffect, QListWidget, QListWidgetItem, QDialog,
    QCheckBox, QSpinBox, QComboBox, QPushButton, QFormLayout, QTabWidget,
    QColorDialog, QSlider, QGroupBox, QTextEdit, QButtonGroup, QRadioButton
)

try:
    from PyQt6.QtWinExtras import QtWin
except ImportError:
    QtWin = None

try:
    import pythoncom
    import win32com.client
    import win32gui
except ImportError:
    pythoncom = None
    win32com = None
    win32gui = None

import threading
import pystray
from PIL import Image
from pynput import keyboard

class SettingsManager:
    def __init__(self):
        self.settings_file = "simplexity_settings.json"
        self.default_settings = {

            "auto_hide_delay": 3000,
            "max_results": 8,
            "show_math_calculator": True,
            "show_perplexity_search": True,
            "show_file_search": False,
            "auto_launch_on_startup": False,
            "close_after_launch": True,
            "remember_window_position": False,
            "enable_fuzzy_search": True,
            "search_case_sensitive": False,

            "launcher_opacity": 95,
            "theme_accent_color": "#00D4AA",
            "launcher_width": 600,
            "launcher_height": 320,
            "font_size": 16,
            "show_icons": True,
            "animation_speed": 300,
            "blur_background": True,
            "dark_theme": True,

            "hotkey_combination": "Ctrl+Space",
            "enable_double_ctrl": False,
            "hotkey_modifier": "Ctrl",
            "hotkey_key": "Space",

            "search_web_engine": "perplexity",
            "search_include_descriptions": False,
            "prioritize_recent_apps": True,
            "exclude_system_apps": False,
            "custom_search_engines": {},

            "enable_plugins": False,
            "auto_update_check": True,
            "performance_mode": False,
            "debug_mode": False,
            "custom_css": "",
        }
        self.settings = self.load_settings()

    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    loaded = json.load(f)

                    settings = self.default_settings.copy()
                    settings.update(loaded)
                    return settings
        except:
            pass
        return self.default_settings.copy()

    def save_settings(self):
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get(self, key):
        return self.settings.get(key, self.default_settings.get(key))

    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()

class SettingsDialog(QDialog):
    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.setWindowTitle("Simplexity Settings")
        self.setModal(True)
        self.setFixedSize(650, 700)

        self.setStyleSheet("""
            QDialog {
                background: 
                color: 
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QTabWidget::pane {
                border: 2px solid 
                border-radius: 8px;
                background: 
            }
            QTabWidget::tab-bar {
                alignment: center;
            }
            QTabBar::tab {
                background: 
                color: 
                padding: 8px 16px;
                margin: 2px;
                border-radius: 6px;
                min-width: 80px;
            }
            QTabBar::tab:selected {
                background: 
                color: 
                font-weight: bold;
            }
            QTabBar::tab:hover {
                background: 
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid 
                border-radius: 8px;
                margin-top: 1ex;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: 
            }
            QCheckBox, QRadioButton {
                color: 
                spacing: 8px;
            }
            QCheckBox::indicator, QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid 
                border-radius: 4px;
                background: 
            }
            QCheckBox::indicator:checked, QRadioButton::indicator:checked {
                background: 
                border-color: 
            }
            QRadioButton::indicator {
                border-radius: 9px;
            }
            QLabel {
                color: 
            }
            QSpinBox, QComboBox {
                background: 
                color: 
                border: 2px solid 
                border-radius: 6px;
                padding: 6px;
                min-height: 20px;
            }
            QSpinBox:focus, QComboBox:focus {
                border-color: 
            }

            QComboBox QAbstractItemView {
                background: 
                color: 
                border: 1px solid 
                border-radius: 4px;
                selection-background-color: 
                selection-color: 
            }
            QComboBox::drop-down {
                border: none;
                background: 
                width: 20px;
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid 
                margin: 2px;
            }
            QSlider::groove:horizontal {
                border: 1px solid 
                height: 8px;
                background: 
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: 
                border: 1px solid 
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QPushButton {
                background: 
                color: 
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: 
            }
            QPushButton:pressed {
                background: 
            }
            QTextEdit {
                background: 
                color: 
                border: 2px solid 
                border-radius: 6px;
                padding: 8px;
            }
            QTextEdit:focus {
                border-color: 
            }
        """)

        self.setup_ui()
        self.load_current_settings()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        tabs = QTabWidget()

        general_tab = self.create_general_tab()
        tabs.addTab(general_tab, "General")

        appearance_tab = self.create_appearance_tab()
        tabs.addTab(appearance_tab, "Appearance")

        hotkeys_tab = self.create_hotkeys_tab()
        tabs.addTab(hotkeys_tab, "Hotkeys")

        search_tab = self.create_search_tab()
        tabs.addTab(search_tab, "Search")

        advanced_tab = self.create_advanced_tab()
        tabs.addTab(advanced_tab, "Advanced")

        layout.addWidget(tabs)

        button_layout = QHBoxLayout()

        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self.reset_to_defaults)

        export_btn = QPushButton("Export Settings")
        export_btn.clicked.connect(self.export_settings)

        import_btn = QPushButton("Import Settings")
        import_btn.clicked.connect(self.import_settings)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_and_close)

        button_layout.addWidget(reset_btn)
        button_layout.addWidget(export_btn)
        button_layout.addWidget(import_btn)
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

    def create_general_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        behavior_group = QGroupBox("Behavior")
        behavior_layout = QFormLayout(behavior_group)

        self.auto_hide_spin = QSpinBox()
        self.auto_hide_spin.setRange(500, 10000)
        self.auto_hide_spin.setSuffix(" ms")
        behavior_layout.addRow("Auto-hide delay:", self.auto_hide_spin)

        self.max_results_spin = QSpinBox()
        self.max_results_spin.setRange(3, 20)
        behavior_layout.addRow("Max search results:", self.max_results_spin)

        self.close_after_launch_check = QCheckBox("Close launcher after opening app")
        behavior_layout.addRow(self.close_after_launch_check)

        self.remember_position_check = QCheckBox("Remember window position")
        behavior_layout.addRow(self.remember_position_check)

        self.auto_launch_check = QCheckBox("Launch on Windows startup")
        behavior_layout.addRow(self.auto_launch_check)

        layout.addWidget(behavior_group)

        features_group = QGroupBox("Features")
        features_layout = QVBoxLayout(features_group)

        self.math_calc_check = QCheckBox("Enable math calculator")
        self.perplexity_check = QCheckBox("Enable Perplexity search")
        self.file_search_check = QCheckBox("Enable file search (experimental)")
        self.show_icons_check = QCheckBox("Show app icons")

        features_layout.addWidget(self.math_calc_check)
        features_layout.addWidget(self.perplexity_check)
        features_layout.addWidget(self.file_search_check)
        features_layout.addWidget(self.show_icons_check)

        layout.addWidget(features_group)
        layout.addStretch()

        return tab

    def create_appearance_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        visual_group = QGroupBox("Visual")
        visual_layout = QFormLayout(visual_group)

        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(70, 100)
        self.opacity_label = QLabel("95%")
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(self.opacity_slider)
        opacity_layout.addWidget(self.opacity_label)
        visual_layout.addRow("Launcher opacity:", opacity_layout)

        self.width_spin = QSpinBox()
        self.width_spin.setRange(400, 1200)
        self.width_spin.setSuffix(" px")
        visual_layout.addRow("Launcher width:", self.width_spin)

        self.height_spin = QSpinBox()
        self.height_spin.setRange(200, 800)
        self.height_spin.setSuffix(" px")
        visual_layout.addRow("Launcher height:", self.height_spin)

        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(10, 24)
        self.font_size_spin.setSuffix(" pt")
        visual_layout.addRow("Font size:", self.font_size_spin)

        self.accent_color_btn = QPushButton("Choose Accent Color")
        self.accent_color_btn.clicked.connect(self.choose_accent_color)
        visual_layout.addRow("Accent color:", self.accent_color_btn)

        layout.addWidget(visual_group)

        animation_group = QGroupBox("Animation")
        animation_layout = QFormLayout(animation_group)

        self.animation_speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.animation_speed_slider.setRange(100, 1000)
        self.animation_speed_label = QLabel("300ms")
        anim_layout = QHBoxLayout()
        anim_layout.addWidget(self.animation_speed_slider)
        anim_layout.addWidget(self.animation_speed_label)
        animation_layout.addRow("Animation speed:", anim_layout)

        self.blur_background_check = QCheckBox("Blur background")
        animation_layout.addRow(self.blur_background_check)

        layout.addWidget(animation_group)
        layout.addStretch()

        self.opacity_slider.valueChanged.connect(
            lambda v: self.opacity_label.setText(f"{v}%")
        )
        self.animation_speed_slider.valueChanged.connect(
            lambda v: self.animation_speed_label.setText(f"{v}ms")
        )

        return tab

    def create_hotkeys_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        hotkey_group = QGroupBox("Hotkey Configuration")
        hotkey_layout = QFormLayout(hotkey_group)

        self.hotkey_combo = QComboBox()
        self.hotkey_combo.addItems([
            "Ctrl+Space",
            "Alt+Space", 
            "Win+Space",
            "Ctrl+Shift+Space",
            "Alt+Shift+Space",
            "Ctrl+Alt+Space",
            "F1", "F2", "F3", "F4"
        ])
        hotkey_layout.addRow("Launch hotkey:", self.hotkey_combo)

        self.double_ctrl_check = QCheckBox("Enable double-Ctrl activation")
        hotkey_layout.addRow(self.double_ctrl_check)

        layout.addWidget(hotkey_group)

        modifier_group = QGroupBox("Custom Hotkey Builder")
        modifier_layout = QVBoxLayout(modifier_group)

        mod_layout = QHBoxLayout()
        self.ctrl_radio = QRadioButton("Ctrl")
        self.alt_radio = QRadioButton("Alt")
        self.win_radio = QRadioButton("Win")
        self.shift_radio = QRadioButton("Shift")

        self.modifier_group = QButtonGroup()
        self.modifier_group.addButton(self.ctrl_radio)
        self.modifier_group.addButton(self.alt_radio)
        self.modifier_group.addButton(self.win_radio)
        self.modifier_group.addButton(self.shift_radio)

        mod_layout.addWidget(QLabel("Modifier:"))
        mod_layout.addWidget(self.ctrl_radio)
        mod_layout.addWidget(self.alt_radio)
        mod_layout.addWidget(self.win_radio)
        mod_layout.addWidget(self.shift_radio)
        mod_layout.addStretch()

        modifier_layout.addLayout(mod_layout)

        key_layout = QHBoxLayout()
        self.key_combo = QComboBox()
        self.key_combo.addItems([
            "Space", "Enter", "Tab", "Escape",
            "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
            "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
            "1", "2", "3", "4", "5", "6", "7", "8", "9", "0"
        ])
        key_layout.addWidget(QLabel("Key:"))
        key_layout.addWidget(self.key_combo)
        key_layout.addStretch()

        modifier_layout.addLayout(key_layout)

        layout.addWidget(modifier_group)
        layout.addStretch()

        return tab

    def create_search_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        search_group = QGroupBox("Search Behavior")
        search_layout = QVBoxLayout(search_group)

        self.fuzzy_search_check = QCheckBox("Enable fuzzy search")
        self.case_sensitive_check = QCheckBox("Case-sensitive search")
        self.prioritize_recent_check = QCheckBox("Prioritize recently used apps")
        self.exclude_system_check = QCheckBox("Exclude system applications")
        self.include_descriptions_check = QCheckBox("Include app descriptions in search")

        search_layout.addWidget(self.fuzzy_search_check)
        search_layout.addWidget(self.case_sensitive_check)
        search_layout.addWidget(self.prioritize_recent_check)
        search_layout.addWidget(self.exclude_system_check)
        search_layout.addWidget(self.include_descriptions_check)

        layout.addWidget(search_group)

        web_group = QGroupBox("Web Search")
        web_layout = QFormLayout(web_group)

        self.search_engine_combo = QComboBox()
        self.search_engine_combo.addItems([
            "perplexity", "google", "bing", "duckduckgo", "yahoo"
        ])
        web_layout.addRow("Default search engine:", self.search_engine_combo)

        layout.addWidget(web_group)
        layout.addStretch()

        return tab

    def create_advanced_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        performance_group = QGroupBox("Performance")
        performance_layout = QVBoxLayout(performance_group)

        self.performance_mode_check = QCheckBox("Performance mode (reduced animations)")
        self.debug_mode_check = QCheckBox("Enable debug mode")

        performance_layout.addWidget(self.performance_mode_check)
        performance_layout.addWidget(self.debug_mode_check)

        layout.addWidget(performance_group)

        css_group = QGroupBox("Custom Styling")
        css_layout = QVBoxLayout(css_group)

        css_layout.addWidget(QLabel("Custom CSS (Advanced users only):"))
        self.custom_css_edit = QTextEdit()
        self.custom_css_edit.setMaximumHeight(100)
        self.custom_css_edit.setPlaceholderText("Enter custom CSS rules here...")
        css_layout.addWidget(self.custom_css_edit)

        layout.addWidget(css_group)
        layout.addStretch()

        return tab

    def load_current_settings(self):

        self.auto_hide_spin.setValue(self.settings_manager.get("auto_hide_delay"))
        self.max_results_spin.setValue(self.settings_manager.get("max_results"))
        self.math_calc_check.setChecked(self.settings_manager.get("show_math_calculator"))
        self.perplexity_check.setChecked(self.settings_manager.get("show_perplexity_search"))
        self.file_search_check.setChecked(self.settings_manager.get("show_file_search"))
        self.show_icons_check.setChecked(self.settings_manager.get("show_icons"))
        self.auto_launch_check.setChecked(self.settings_manager.get("auto_launch_on_startup"))
        self.close_after_launch_check.setChecked(self.settings_manager.get("close_after_launch"))
        self.remember_position_check.setChecked(self.settings_manager.get("remember_window_position"))

        self.opacity_slider.setValue(self.settings_manager.get("launcher_opacity"))
        self.width_spin.setValue(self.settings_manager.get("launcher_width"))
        self.height_spin.setValue(self.settings_manager.get("launcher_height"))
        self.font_size_spin.setValue(self.settings_manager.get("font_size"))
        self.animation_speed_slider.setValue(self.settings_manager.get("animation_speed"))
        self.blur_background_check.setChecked(self.settings_manager.get("blur_background"))

        hotkey = self.settings_manager.get("hotkey_combination")
        index = self.hotkey_combo.findText(hotkey)
        if index >= 0:
            self.hotkey_combo.setCurrentIndex(index)

        self.double_ctrl_check.setChecked(self.settings_manager.get("enable_double_ctrl"))

        self.fuzzy_search_check.setChecked(self.settings_manager.get("enable_fuzzy_search"))
        self.case_sensitive_check.setChecked(self.settings_manager.get("search_case_sensitive"))
        self.prioritize_recent_check.setChecked(self.settings_manager.get("prioritize_recent_apps"))
        self.exclude_system_check.setChecked(self.settings_manager.get("exclude_system_apps"))
        self.include_descriptions_check.setChecked(self.settings_manager.get("search_include_descriptions"))

        engine = self.settings_manager.get("search_web_engine")
        engine_index = self.search_engine_combo.findText(engine)
        if engine_index >= 0:
            self.search_engine_combo.setCurrentIndex(engine_index)

        self.performance_mode_check.setChecked(self.settings_manager.get("performance_mode"))
        self.debug_mode_check.setChecked(self.settings_manager.get("debug_mode"))
        self.custom_css_edit.setPlainText(self.settings_manager.get("custom_css"))

    def choose_accent_color(self):
        current_color = QColor(self.settings_manager.get("theme_accent_color"))
        color = QColorDialog.getColor(current_color, self, "Choose Accent Color")
        if color.isValid():
            self.settings_manager.set("theme_accent_color", color.name())
            self.accent_color_btn.setStyleSheet(f"background-color: {color.name()};")

    def export_settings(self):
        try:
            from PyQt6.QtWidgets import QFileDialog
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export Settings", "simplexity_settings_backup.json", 
                "JSON files (*.json)"
            )
            if filename:
                with open(filename, 'w') as f:
                    json.dump(self.settings_manager.settings, f, indent=2)
                print(f"Settings exported to {filename}")
        except Exception as e:
            print(f"Export failed: {e}")

    def import_settings(self):
        try:
            from PyQt6.QtWidgets import QFileDialog
            filename, _ = QFileDialog.getOpenFileName(
                self, "Import Settings", "", "JSON files (*.json)"
            )
            if filename:
                with open(filename, 'r') as f:
                    imported_settings = json.load(f)
                self.settings_manager.save_settings()
                self.load_current_settings()
                print(f"Settings imported from {filename}")
        except Exception as e:
            print(f"Import failed: {e}")

    def reset_to_defaults(self):
        self.settings_manager.settings = self.settings_manager.default_settings.copy()
        self.load_current_settings()

    def save_and_close(self):

        self.settings_manager.set("auto_hide_delay", self.auto_hide_spin.value())
        self.settings_manager.set("max_results", self.max_results_spin.value())
        self.settings_manager.set("show_math_calculator", self.math_calc_check.isChecked())
        self.settings_manager.set("show_perplexity_search", self.perplexity_check.isChecked())
        self.settings_manager.set("show_file_search", self.file_search_check.isChecked())
        self.settings_manager.set("show_icons", self.show_icons_check.isChecked())
        self.settings_manager.set("auto_launch_on_startup", self.auto_launch_check.isChecked())
        self.settings_manager.set("close_after_launch", self.close_after_launch_check.isChecked())
        self.settings_manager.set("remember_window_position", self.remember_position_check.isChecked())

        self.settings_manager.set("launcher_opacity", self.opacity_slider.value())
        self.settings_manager.set("launcher_width", self.width_spin.value())
        self.settings_manager.set("launcher_height", self.height_spin.value())
        self.settings_manager.set("font_size", self.font_size_spin.value())
        self.settings_manager.set("animation_speed", self.animation_speed_slider.value())
        self.settings_manager.set("blur_background", self.blur_background_check.isChecked())

        self.settings_manager.set("hotkey_combination", self.hotkey_combo.currentText())
        self.settings_manager.set("enable_double_ctrl", self.double_ctrl_check.isChecked())

        self.settings_manager.set("enable_fuzzy_search", self.fuzzy_search_check.isChecked())
        self.settings_manager.set("search_case_sensitive", self.case_sensitive_check.isChecked())
        self.settings_manager.set("prioritize_recent_apps", self.prioritize_recent_check.isChecked())
        self.settings_manager.set("exclude_system_apps", self.exclude_system_check.isChecked())
        self.settings_manager.set("search_include_descriptions", self.include_descriptions_check.isChecked())
        self.settings_manager.set("search_web_engine", self.search_engine_combo.currentText())

        self.settings_manager.set("performance_mode", self.performance_mode_check.isChecked())
        self.settings_manager.set("debug_mode", self.debug_mode_check.isChecked())
        self.settings_manager.set("custom_css", self.custom_css_edit.toPlainText())

        self.accept()

def find_start_menu_apps():
    apps = []
    start_dirs = [
        os.path.join(os.environ.get('APPDATA', ''), r'Microsoft\Windows\Start Menu\Programs'),
        os.path.join(os.environ.get('PROGRAMDATA', ''), r'Microsoft\Windows\Start Menu\Programs')
    ]
    for start_dir in start_dirs:
        if not os.path.exists(start_dir):
            continue
        for root, dirs, files in os.walk(start_dir):
            for file in files:
                if file.lower().endswith('.lnk'):
                    path = os.path.join(root, file)
                    name = file[:-4]
                    apps.append((name, path))
    return apps

def evaluate_math_expression(expr):
    """Safely evaluate mathematical expressions"""

    expr = expr.replace(' ', '').lower()

    replacements = {
        'pi': str(math.pi),
        'e': str(math.e),
        'sin': 'math.sin',
        'cos': 'math.cos',
        'tan': 'math.tan',
        'sqrt': 'math.sqrt',
        'log': 'math.log10',
        'ln': 'math.log',
        'abs': 'abs',
        '^': '**',
    }

    for old, new in replacements.items():
        expr = expr.replace(old, new)

    if not re.match(r'^[0-9+\-*/().mathsincoqrtlgabspie\s]+$', expr):
        return None

    try:

        result = eval(expr, {"__builtins__": {}, "math": math, "abs": abs})
        return result
    except:
        return None

def is_math_expression(text):
    """Check if text looks like a mathematical expression"""

    math_pattern = r'[0-9+\-*/().^]'
    math_functions = ['sin', 'cos', 'tan', 'sqrt', 'log', 'ln', 'pi', 'e']

    has_math_chars = bool(re.search(math_pattern, text))
    has_math_functions = any(func in text.lower() for func in math_functions)

    return has_math_chars or has_math_functions

class AnimatedLineEdit(QLineEdit):
    def __init__(self):
        super().__init__()
        self._glow_radius = 0
        self.animation = QPropertyAnimation(self, b"glowRadius")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    @pyqtProperty(int)
    def glowRadius(self):
        return self._glow_radius

    @glowRadius.setter
    def glowRadius(self, value):
        self._glow_radius = value
        self.update()

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.animation.setStartValue(0)
        self.animation.setEndValue(15)  
        self.animation.start()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.animation.setStartValue(15)
        self.animation.setEndValue(0)
        self.animation.start()

class ModernListWidget(QListWidget):
    def __init__(self):
        super().__init__()
        self.setAlternatingRowColors(False)

class SimplexityLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.settings_manager = SettingsManager()

        self.setWindowTitle("Simplexity")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(600, 320)  

        screen = QApplication.primaryScreen().availableGeometry()
        x = (screen.width() - self.width()) // 2
        y = 100
        self.move(x, y)

        accent_color = self.settings_manager.get("theme_accent_color")

        self.setStyleSheet(f"""
            QWidget {{
                font-family: 'Segoe UI', Arial, sans-serif;
                background: rgba(15, 15, 15, 240);
                border: 2px solid {accent_color};
                border-radius: 16px;
            }}
            QLineEdit {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 
                color: 
                font-size: 16px;
                font-weight: 400;
                border: 2px solid {accent_color};
                border-radius: 12px;
                padding: 8px 16px;
                min-height: 24px;
                max-height: 24px;
                selection-background-color: {accent_color};
                selection-color: 
            }}
            QLineEdit:focus {{
                border: 2px solid 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 
                box-shadow: 0 0 10px rgba(0, 255, 204, 0.3);
            }}
            QListWidget {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(25, 25, 25, 255), stop:1 rgba(15, 15, 15, 255));
                border: 1px solid 
                border-radius: 12px;
                color: 
                font-size: 14px;
                font-weight: 400;
                padding: 6px;
                outline: none;
            }}
            QListWidget::item {{
                background: transparent;
                border: 1px solid transparent;
                border-radius: 8px;
                padding: 8px 12px;
                margin: 1px 0px;
                color: 
            }}
            QListWidget::item:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 212, 170, 0.15), stop:1 rgba(0, 212, 170, 0.08));
                border: 1px solid rgba(0, 212, 170, 0.3);
                color: 
            }}
            QListWidget::item:selected {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {accent_color}, stop:1 
                border: 1px solid 
                color: 
                font-weight: 500;
            }}
            QListWidget QScrollBar:vertical {{
                background: rgba(30, 30, 30, 255);
                width: 8px;
                margin: 0px;
                border-radius: 4px;
            }}
            QListWidget QScrollBar::handle:vertical {{
                background: {accent_color};
                min-height: 20px;
                border-radius: 4px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        self.entry = AnimatedLineEdit()
        self.entry.setPlaceholderText("Search apps, calculate, or search web...")
        self.entry.returnPressed.connect(self.on_enter_pressed)
        self.entry.textChanged.connect(self.on_text_changed)
        self.entry.installEventFilter(self)
        layout.addWidget(self.entry, 0, Qt.AlignmentFlag.AlignTop)

        self.list_widget = ModernListWidget()
        self.list_widget.setFixedHeight(220)
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        self.list_widget.installEventFilter(self)
        layout.addWidget(self.list_widget, 0, Qt.AlignmentFlag.AlignTop)
        self.list_widget.setVisible(False)

        self.is_visible = False
        self.ctrl_pressed = False

        self.all_apps = find_start_menu_apps()
        self.apps_lower = [(name.lower(), path) for name, path in self.all_apps]

        self.builtin_items = [
            ("settings", "⚙️ Settings", "settings_menu"),
            ("preferences", "⚙️ Settings", "settings_menu"),
            ("config", "⚙️ Settings", "settings_menu"),
            ("options", "⚙️ Settings", "settings_menu"),
        ]

        self.setup_hotkey()
        self.create_tray_icon()

    def setup_hotkey(self):
        def on_press(key):
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.ctrl_pressed = True
            elif key == keyboard.Key.space and self.ctrl_pressed:
                QTimer.singleShot(100, self.toggle_visibility)

        def on_release(key):
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.ctrl_pressed = False

        self.listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        self.listener.start()

    def create_tray_icon(self):
        try:

            icon_image = Image.open("Assets/Icon.ico")
        except:

            icon_image = Image.new('RGBA', (64, 64), (0, 212, 170, 255))

        menu = pystray.Menu(
            pystray.MenuItem('Show Launcher', self.show_launcher_pystray),
            pystray.MenuItem('Settings', self.show_settings_pystray),
            pystray.MenuItem('Exit', self.exit_app_pystray)
        )

        self.tray_icon = pystray.Icon("Simplexity", icon_image, "Simplexity", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def show_launcher_pystray(self, icon, item):
        self.show()
        self.raise_()
        self.activateWindow()
        self.is_visible = True

    def show_settings_pystray(self, icon, item):
        self.show_settings()

    def exit_app_pystray(self, icon, item):
        self.tray_icon.stop()
        QApplication.quit()

    def show_settings(self):
        settings_dialog = SettingsDialog(self.settings_manager, self)
        if settings_dialog.exec() == QDialog.DialogCode.Accepted:

            self.update_ui_from_settings()

    def update_ui_from_settings(self):

        accent_color = self.settings_manager.get("theme_accent_color")

        self.__init__()

    def toggle_visibility(self):
        if not self.isVisible():
            self.show_launcher()
        else:
            self.hide_launcher()

    def show_launcher(self):
        self.show()
        self.raise_()
        self.activateWindow()
        self.entry.clear()
        self.list_widget.clear()
        self.list_widget.setVisible(False)
        QTimer.singleShot(50, self.focus_and_prepare_entry)
        self.is_visible = True

    def focus_and_prepare_entry(self):
        self.entry.setFocus(Qt.FocusReason.OtherFocusReason)
        self.entry.setCursorPosition(len(self.entry.text()))

    def hide_launcher(self):
        self.hide()
        self.is_visible = False

    def on_enter_pressed(self):
        current_item = self.list_widget.currentItem()
        text = self.entry.text().strip()

        if current_item:
            data = current_item.data(Qt.ItemDataRole.UserRole)
            if data == "settings_menu":
                self.show_settings()
            elif data == "perplexity_search":
                self.launch_perplexity_search(text)
            elif data and data.startswith("math_result:"):

                result = data.replace("math_result:", "")
                QApplication.clipboard().setText(result)
                print(f"Copied to clipboard: {result}")
            else:
                self.launch_app(data)
        else:
            if text:

                if is_math_expression(text) and self.settings_manager.get("show_math_calculator"):
                    result = evaluate_math_expression(text)
                    if result is not None:
                        QApplication.clipboard().setText(str(result))
                        print(f"Math result copied to clipboard: {result}")
                    else:
                        self.launch_perplexity_search(text)
                else:
                    self.launch_perplexity_search(text)

        self.hide_launcher()

    def on_item_clicked(self, item: QListWidgetItem):
        data = item.data(Qt.ItemDataRole.UserRole)
        text = self.entry.text().strip()

        if data == "settings_menu":
            self.show_settings()
        elif data == "perplexity_search":
            self.launch_perplexity_search(text)
        elif data and data.startswith("math_result:"):
            result = data.replace("math_result:", "")
            QApplication.clipboard().setText(result)
            print(f"Copied to clipboard: {result}")
        else:
            self.launch_app(data)
        self.hide_launcher()

    def launch_app(self, path):
        try:
            os.startfile(path)
        except Exception as e:
            print(f"Couldn't open {path}: {e}")

    def launch_perplexity_search(self, query):
        if query and self.settings_manager.get("show_perplexity_search"):
            encoded = urllib.parse.quote_plus(query)
            url = f"https://www.perplexity.ai/search/new?q={encoded}"
            webbrowser.open(url)

    def on_text_changed(self, text):
        text_stripped = text.strip()
        text_lower = text_stripped.lower()

        if not text_stripped:
            self.list_widget.clear()
            self.list_widget.setVisible(False)
            return

        matched_apps = []
        matched_builtin = []
        math_result = None

        for keyword, display_name, action in self.builtin_items:
            if text_lower in keyword:
                matched_builtin.append((display_name, action))

        if (is_math_expression(text_stripped) and 
            self.settings_manager.get("show_math_calculator")):
            math_result = evaluate_math_expression(text_stripped)

        max_results = self.settings_manager.get("max_results")
        for name_lower, path in self.apps_lower:
            if text_lower in name_lower:
                matched_apps.append((name_lower, path))
                if len(matched_apps) >= max_results:
                    break

        self.list_widget.clear()

        for display_name, action in matched_builtin:
            item = QListWidgetItem(display_name)
            item.setData(Qt.ItemDataRole.UserRole, action)
            item.setSizeHint(QSize(0, 35))
            self.list_widget.addItem(item)

        if math_result is not None:
            result_text = str(math_result)
            if len(result_text) > 50:  
                try:
                    if '.' in result_text:
                        result_text = f"{float(result_text):.10g}"
                    else:
                        result_text = f"{int(float(result_text)):,}"
                except:
                    pass

            item = QListWidgetItem(f"📊 {text_stripped} = {result_text}")
            item.setData(Qt.ItemDataRole.UserRole, f"math_result:{result_text}")
            item.setSizeHint(QSize(0, 35))
            self.list_widget.addItem(item)

        if matched_apps:
            for name_lower, path in matched_apps:
                display_name = ' '.join(word.capitalize() for word in name_lower.split())
                item = QListWidgetItem(f"🚀 {display_name}")
                item.setData(Qt.ItemDataRole.UserRole, path)
                item.setSizeHint(QSize(0, 35))
                self.list_widget.addItem(item)

        if (text_stripped and self.settings_manager.get("show_perplexity_search") and
            (not math_result or matched_apps or matched_builtin)):
            item = QListWidgetItem(f'🔍 Ask Perplexity AI: "{text_stripped}"')
            item.setData(Qt.ItemDataRole.UserRole, "perplexity_search")
            item.setSizeHint(QSize(0, 35))
            self.list_widget.addItem(item)

        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)
            self.list_widget.setVisible(True)
        else:
            self.list_widget.setVisible(False)

    def eventFilter(self, obj, event):
        if obj is self.entry:
            if event.type() == QEvent.Type.FocusOut:
                QTimer.singleShot(100, self.check_focus)
            elif event.type() == QEvent.Type.KeyPress:
                if event.key() == Qt.Key.Key_Escape:
                    self.hide_launcher()
                elif event.key() in (Qt.Key.Key_Down, Qt.Key.Key_Up):
                    if self.list_widget.isVisible():
                        self.list_widget.setFocus()
                        if event.key() == Qt.Key.Key_Down:
                            self.list_widget.setCurrentRow(0)
                        else:
                            self.list_widget.setCurrentRow(self.list_widget.count() - 1)
                        return True
        elif obj is self.list_widget:
            if event.type() == QEvent.Type.KeyPress:
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                    self.on_enter_pressed()
                    return True
                elif event.key() == Qt.Key.Key_Escape:
                    self.hide_launcher()
                    return True
                elif event.key() in (Qt.Key.Key_Backspace, Qt.Key.Key_Delete):
                    self.entry.setFocus()
                    return True
        return super().eventFilter(obj, event)

    def check_focus(self):
        if not self.entry.hasFocus() and not self.list_widget.hasFocus():
            self.hide_launcher()

    def closeEvent(self, event):
        event.ignore()
        self.hide_launcher()

def main():
    app = QApplication(sys.argv)

    app.setApplicationName("Simplexity")
    app.setApplicationVersion("2.1")

    launcher = SimplexityLauncher()
    print("Enhanced Simplexity running. Press Ctrl+Space to open.")
    print("Features: App search, Math calculator, Web search, Settings")
    print("Type 'settings' to open configuration menu")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()