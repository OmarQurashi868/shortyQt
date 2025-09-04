import os
import vdf
from PySide6.QtWidgets import QTableWidget

def get_existing_shortcuts(shortcuts_path: str) -> dict[str, dict[str, str | int]]:
    if os.path.exists(shortcuts_path):
        with open(shortcuts_path, "rb") as f:
            return vdf.binary_load(f)['shortcuts']
    return {}

def get_shortcuts_dict(shortcuts_list: QTableWidget) -> dict[str, dict[str, str | int]]:
    headers = [shortcuts_list.horizontalHeaderItem(i).text() for i in range(shortcuts_list.columnCount())] # type: ignore

    for row in range(shortcuts_list.rowCount()):
        row_dict = {}
        for col, header in enumerate(headers):
            item = shortcuts_list.item(row, col)
            row_dict[header] = item.text() if item else None
        return row_dict
    return {}