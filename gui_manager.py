import sys

import qdarktheme
import state
import logging
import os
import platform
from typing import Tuple
import path_manager
from metadata_manager import grab_metadata
from shortcut_manager import add_new_shortcut, get_existing_shortcuts, get_shortcut_id_by_appid, set_new_shortcuts
from PySide6.QtWidgets import QWidget, QApplication, QTableWidget, QHeaderView, QAbstractItemView, QTableWidgetItem, QDialog, QPushButton, QFileDialog
from PySide6.QtCore import QFile, Qt
from PySide6.QtUiTools import QUiLoader
from setup_manager import is_steam_exists, on_path_change, confirm_config

try:
    import win32api
except ImportError:
    win32api = None

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

def init_main_window():
    app = QApplication()
    # Dark theme
    qdarktheme.setup_theme(theme="auto", corner_shape="sharp", additional_qss="QToolTip { border: 0px; }")
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

    state.window = window
    window.statusBar().showMessage("Welcome to SteamShorty!") # type: ignore

    # Set buttons
    metadata_button = window.findChild(QPushButton, "metadataButton", Qt.FindChildOption.FindChildrenRecursively)
    metadata_button.clicked.connect(grab_metadata) # type: ignore

    add_button = window.findChild(QPushButton, "addButton")
    add_button.clicked.connect(add_exe)


    delete_button = window.findChild(QPushButton, "deleteButton")
    delete_button.clicked.connect(delete_shortcut)


    window.metadataButton.clicked.connect(grab_metadata) # type: ignore
    window.configButton.clicked.connect(init_setup_window) # type: ignore


    window.show()

def init_setup_window():
    ui_file = QFile("ui/config_window.ui")
    ui_file.open(QFile.OpenModeFlag.ReadOnly)
    loader = QUiLoader()
    window = loader.load(ui_file)
    ui_file.close()

    if not window:
        print(loader.errorString())
        sys.exit(-1)

    state.config_window = window

    window.setWindowFlags(window.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint)

    # Load config into fields
    window.pathField.setText(state.steam_path) # type: ignore
    if is_steam_exists(state.steam_path):
        window.pathLabel.setText("Steam installation found") # type: ignore
        window.pathLabel.setStyleSheet(f"color: {"green"};") # type: ignore

    window.apiField.setText(state.api_key) # type: ignore

    users = path_manager.get_steam_users(state.steam_path)
    window.userSelect.addItems(users) # type: ignore
    if state.user in users:
        window.userSelect.setCurrentIndex(users.index(state.user)) # type: ignore

    if is_steam_exists(state.steam_path) and users:
        window.buttonBox.setEnabled(True) # type: ignore

    window.pathField.textChanged.connect(on_path_change) # type: ignore
    ok_button = window.buttonBox.button(QDialogButtonBox.StandardButton.Ok) # type: ignore
    ok_button.clicked.connect(confirm_config)

    window.browseButton.clicked.connect(set_browsed_path) # type: ignore
    
    # Window setup
    window.setWindowModality(Qt.WindowModality.ApplicationModal)
    window.show()
    window.setFocus() # So no child takes first focus

def set_browsed_path():
    path = QFileDialog.getExistingDirectory(state.window, "Select Steam folder", state.steam_path)
    if path:
        state.config_window.pathField.setText(path) # type: ignore

def update_shortcut_list(shortcuts: dict[str, dict[str, str | int]]) -> bool:
    shortcuts_list = state.window.findChild(QTableWidget, "shortcutsList")
    if not shortcuts_list:
        return False

    columns = ["AppId", "AppName", "Image", "Path"]
    entry_columns = ["appid", "AppName", "Icon", "Exe"]

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
            
            value = entry.get(entry_columns[col_idx], "")
            item.setText(str(value))
            shortcuts_list.setItem(row_idx, col_idx, item)
    
    shortcuts_list.sortItems(1, Qt.SortOrder.AscendingOrder)
    return True

def get_selected_appids() -> list[int]:
    appids = list()

    shortcuts_list = state.window.findChild(QTableWidget, "shortcutsList")
    if not shortcuts_list:
        return appids
    
    for i in range(shortcuts_list.columnCount()):
        if shortcuts_list.horizontalHeaderItem(i).text() == "AppId":
            appid_col = i
            break
        if appid_col is None:
            return appids
        
    
    for idx in shortcuts_list.selectionModel().selectedRows():
        row = idx.row()
        selected_shortcuts.add(row)
    return selected_shortcuts

def popup(window: QWidget, title: str, text: str):
    dlg = QDialog(window)
    dlg.setWindowTitle(title)
    dlg.exec()


def add_exe():
    exe_path, _ = QFileDialog.getOpenFileName(
        state.window,
        "Select Executable",
        "",
        "Executable Files (*.exe)"
    )

    exe_path = os.path.normpath(exe_path)
    if not exe_path or exe_path == ".":
        return

    logger.info("Selected exe path: %s", exe_path)

    app_name = extract_app_name(exe_path)
    add_new_shortcut(exe_path, app_name)

    shortcuts_path = path_manager.get_shortcuts_path(state.steam_path, state.user)
    new_shortcuts = get_existing_shortcuts(shortcuts_path)
    update_shortcut_list(new_shortcuts)



def delete_shortcut():
    appids = get_selected_appids()
    shortcuts_path = path_manager.get_shortcuts_path(state.steam_path, state.user)
    current_shortcuts = get_existing_shortcuts(shortcuts_path)

    indecies = []

    for appid in appids:
        indecies.append(get_shortcut_id_by_appid(appid))
    
    for indx in indecies:
        deleted = current_shortcuts.pop(indx, None)
        if deleted is None:
            logger.info(f"Failed to delete item #{indx}")
        
    set_new_shortcuts(current_shortcuts, shortcuts_path)
    update_shortcut_list(current_shortcuts)
    
    

            
def extract_app_name(exe_path: str) -> str:
    system = platform.system()

    if system == "Windows" and win32api:
        try:
            info = win32api.GetFileVersionInfo(exe_path, "\\")
            lang, codepage = list(info['StringFileInfo'].keys())[0] # type: ignore
            metadata = info['StringFileInfo'][(lang, codepage)] # type: ignore
            return metadata.get('FileDescription') or metadata.get('ProductName') or ""
        except Exception:
            pass

    return os.path.splitext(os.path.basename(exe_path))[0]
