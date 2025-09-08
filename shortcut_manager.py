import os
import vdf
import zlib
from PySide6.QtWidgets import QTableWidget

def steam_shortcut_id(exe, name):
    """Generate Steam shortcut AppID (same algo Steam uses)."""
    data = f"{exe}{name}".encode("utf-8")
    crc = zlib.crc32(data) & 0xFFFFFFFF
    appid = crc | 0x80000000  # non-Steam flag
    return str(appid)

from PySide6.QtWidgets import QTableWidget

def get_existing_shortcuts(shortcuts_path: str) -> dict[str, dict[str, str | int]]:
    if os.path.exists(shortcuts_path):
        with open(shortcuts_path, "rb") as f:
            return vdf.binary_load(f)['shortcuts']
    return {}


def set_new_shortcuts(shortcuts: dict, shortcuts_path: str):
    if os.path.exists(shortcuts_path):
        with open(shortcuts_path, "wb") as f:
            vdf.binary_dump(shortcuts, f)
            

def add_new_shortcut(shortcuts_path: str, exe_path: str, name: str, icon_path: str):
    if os.path.exists(shortcuts_path):
        current_shortcuts = get_existing_shortcuts(shortcuts_path)
        
        appid = steam_shortcut_id(exe_path, name)
        start_dir = os.path.dirname(exe_path)
        
        index = len(current_shortcuts) # Key of the new shortcut entry
        current_shortcuts[index] = { # Modifying the current shortcuts dict
            "appid": appid,
            "AppName": name,
            "Exe": f"\"{exe_path}\"",
            "StartDir": f"\"{start_dir}\"",
            "LaunchOptions": "",
            "Icon": icon_path,
            "ShortcutPath": "",
            "AllowOverlay": 1,
            "OpenVR": 0,
            "LastPlayTime": 0,
            "tags": {0: ""},
        }
        
        set_new_shortcuts(current_shortcuts, shortcuts_path)


def get_shortcuts_dict(shortcuts_list: QTableWidget) -> dict[str, dict[str, str | int]]:
    headers = [shortcuts_list.horizontalHeaderItem(i).text() for i in range(shortcuts_list.columnCount())]  # type: ignore
    # NOTE: the original main branch returned inside the loop (likely a bug).
    # Here’s a safe version that reads all rows into a dict keyed by row index.
    data: dict[str, dict[str, str | int]] = {}
    for row in range(shortcuts_list.rowCount()):
        row_dict: dict[str, str | int | None] = {}
        for col, header in enumerate(headers):
            item = shortcuts_list.item(row, col)
            row_dict[header] = item.text() if item else None
        data[str(row)] = row_dict  # key as string to match vdf-like dicts
    return data
    
    
    
    
            

def get_shortcuts_dict(shortcuts_list: QTableWidget) -> dict[str, dict[str, str | int]]:
    headers = [shortcuts_list.horizontalHeaderItem(i).text() for i in range(shortcuts_list.columnCount())] # type: ignore

    for row in range(shortcuts_list.rowCount()):
        row_dict = {}
        for col, header in enumerate(headers):
            item = shortcuts_list.item(row, col)
            row_dict[header] = item.text() if item else None
        return row_dict
    return {}