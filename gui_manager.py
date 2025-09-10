import sys

import qdarktheme
import state
import path_manager
from metadata_manager import grab_metadata
from setup_manager import is_steam_exists
from typing import Tuple
from PySide6.QtWidgets import QWidget, QApplication, QTableWidget, QHeaderView, QAbstractItemView, QTableWidgetItem, QDialog, QPushButton
from PySide6.QtCore import QFile, Qt
from PySide6.QtUiTools import QUiLoader

def init_main_window() -> Tuple[QWidget, QApplication]:
    app = QApplication()
    # Dark theme
    qdarktheme.setup_theme(theme="auto",additional_qss="QToolTip { border: 0px; }")
    app.setPalette(qdarktheme.load_palette())

    state.app = app

    ui_file = QFile("ui/main_window.ui")
    ui_file.open(QFile.OpenModeFlag.ReadOnly)
    loader = QUiLoader()
    window = loader.load(ui_file)
    ui_file.close()

    if not window:
        print(loader.errorString())
        sys.exit(-1)

    # Set buttons
    #metadata_button = window.findChild(QPushButton, "metadataButton", Qt.FindChildOption.FindChildrenRecursively)
    window.metadataButton.clicked.connect(grab_metadata) # type: ignore
    window.actionSetup.triggered.connect(init_setup_window) # type: ignore

    window.show()

    return window, app

def init_setup_window() -> QWidget:
    ui_file = QFile("ui/setup_dialog.ui")
    ui_file.open(QFile.OpenModeFlag.ReadOnly)
    loader = QUiLoader()
    window = loader.load(ui_file)
    ui_file.close()

    if not window:
        print(loader.errorString())
        sys.exit(-1)

    # Load config into fields
    window.pathField.setText(state.steam_path) # type: ignore
    if is_steam_exists(state.steam_path):
        window.pathLabel.setText("Steam installation found") # type: ignore
        window.pathLabel.setStyleSheet(f"color: {"green"};") # type: ignore

    window.apiField.setText(state.api_key) # type: ignore
    
    users = path_manager.get_steam_users(state.steam_path)
    window.userSelect.addItems(users) # type: ignore
    window.userSelect.setCurrentIndex(users.index(state.user)) # type: ignore
    
    window.setWindowModality(Qt.WindowModality.ApplicationModal)
    window.show()
    window.setFocus() # So no child takes first focus

    state.setup_dialog = window
    return window

def update_shortcut_list(shortcuts: dict[str, dict[str, str | int]]) -> bool:
    shortcuts_list = state.window.findChild(QTableWidget, "shortcutsList")
    if not shortcuts_list:
        return False

    columns = ["AppId", "AppName", "Image", "Path"]
    entry_columns = ["appid", "AppName", "icon", "Exe"]

    # shortcuts_list.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    # shortcuts_list.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    # shortcuts_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
    shortcuts_list.setRowCount(len(shortcuts))
    shortcuts_list.setColumnCount(4)
    shortcuts_list.setHorizontalHeaderLabels(columns)

    for row_idx, entry in enumerate(shortcuts.values()):
        for col_idx, col in enumerate(columns):
            item = QTableWidgetItem(col)
            if col != "AppName":
                item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            if col == "Path":
                item.setToolTip(str(entry[entry_columns[col_idx]]))
            if col == "AppId":
                # signed int -> unsigned int
                entry[entry_columns[col_idx]] = str(int(entry[entry_columns[col_idx]]) + (1 << 32))
            item.setText(str(entry[entry_columns[col_idx]]))
            shortcuts_list.setItem(row_idx, col_idx, item)
    
    shortcuts_list.sortItems(1, Qt.SortOrder.AscendingOrder)
    return True

def get_selected_rows() -> set[int]:
    selected_shortcuts = set()

    shortcuts_list = state.window.findChild(QTableWidget, "shortcutsList")
    if not shortcuts_list:
        return selected_shortcuts
    
    for idx in shortcuts_list.selectionModel().selectedRows():
        row = idx.row()
        selected_shortcuts.add(row)
    return selected_shortcuts
