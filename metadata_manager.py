import state
from shortcut_manager import get_shortcuts_dict
from PySide6.QtWidgets import QTableWidget

def grab_metadata() -> bool:
    shortcuts_list = state.window.findChild(QTableWidget, "shortcutsList")
    if not shortcuts_list:
        return False
    
    shortcuts = get_shortcuts_dict(shortcuts_list)
    print(shortcuts)
    return True