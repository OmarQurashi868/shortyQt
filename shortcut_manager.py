import os
import vdf
import zlib
import state
from PySide6.QtWidgets import QTableWidget

def get_appid(exe, name):
    """Generate Steam shortcut AppID (same algo Steam uses)."""
    data = f"{exe}{name}".encode("utf-8")
    crc = zlib.crc32(data) & 0xFFFFFFFF
    appid = crc | 0x80000000  # non-Steam flag
    return str(appid)

def get_existing_shortcuts(shortcuts_path: str) -> dict[str, dict[str, str | int]]:
    if os.path.exists(shortcuts_path):
        with open(shortcuts_path, "rb") as f:
            return vdf.binary_load(f)['shortcuts']
    return {}

def set_new_shortcuts(shortcuts: dict, shortcuts_path: str):
    if os.path.exists(shortcuts_path):
        with open(shortcuts_path, "wb") as f:
            vdf.binary_dump(shortcuts, f)
            
def add_new_shortcut(path: str):
    if os.path.exists(path):
        name = os.path.basename(path) #TODO: get name from file metadata

        appid = get_appid(path, name)
        start_dir = os.path.dirname(path)
        
        index = len(state.shortcuts) # Key of the new shortcut entry
        state.shortcuts[str(index)] = { # Modifying the current shortcuts dict
            "appid": appid,
            "AppName": name,
            "Exe": f"\"{path}\"",
            "StartDir": f"\"{start_dir}\"",
            "LaunchOptions": "",
            "Icon": "",
            "ShortcutPath": "",
            "AllowOverlay": 1,
            "OpenVR": 0,
            "LastPlayTime": 0,
            "tags": {0: "Shorty"}
        }

def get_shortcuts_dict(shortcuts_list: QTableWidget) -> dict[str, dict[str, str | int]]:
    headers = [shortcuts_list.horizontalHeaderItem(i).text() for i in range(shortcuts_list.columnCount())]  # type: ignore
    # NOTE: the original main branch returned inside the loop (likely a bug).
    # Here’s a safe version that reads all rows into a dict keyed by row index.
    data: dict[str, dict[str, str | int]] = {}
    for row in range(shortcuts_list.rowCount()):
        row_dict: dict[str, str | int | None] = {}
        row_dict: dict[str, str | int | None] = {}
        for col, header in enumerate(headers):
            item = shortcuts_list.item(row, col)
            row_dict[header] = item.text() if item else None
        data[str(row)] = row_dict  # type: ignore # key as string to match vdf-like dicts
    return data
