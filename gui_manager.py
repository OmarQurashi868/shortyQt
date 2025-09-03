import sys
from typing import Tuple
from PySide6.QtWidgets import QWidget, QApplication, QTableWidget, QHeaderView, QAbstractItemView, QTableWidgetItem, QDialog
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader

def init_window() -> Tuple[QWidget, QApplication]:
    app = QApplication([])

    ui_file = QFile("main_window.ui")
    ui_file.open(QFile.OpenModeFlag.ReadOnly)
    loader = QUiLoader()
    window = loader.load(ui_file)
    ui_file.close()
    if not window:
        print(loader.errorString())
        sys.exit(-1)
    window.show()

    return window, app

def update_shortcut_list(window, shortcuts: dict[str, dict[str, str | int]]) -> bool:
    shortcuts_list = window.findChild(QTableWidget, "shortcutsList")
    if not shortcuts_list:
        return False

    columns = ["AppId", "AppName", "Path", "Image"]
    entry_columns = ["appid", "AppName", "Exe", "icon"]

    shortcuts_list.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    shortcuts_list.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    shortcuts_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
    shortcuts_list.setRowCount(len(shortcuts))
    shortcuts_list.setColumnCount(4)
    shortcuts_list.setHorizontalHeaderLabels(columns)

    for row_idx, entry in enumerate(shortcuts.values()):
        for col_idx, col in enumerate(columns):
            item = QTableWidgetItem(col)
            item.setText(str(entry[entry_columns[col_idx]]))
            shortcuts_list.setItem(row_idx, col_idx, item)
    return True

def popup(window: QWidget, title: str, text: str):
    dlg = QDialog(window)
    dlg.setWindowTitle(title)
    dlg.exec()