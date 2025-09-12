import state
from shortcut_manager import get_shortcuts_dict
from PySide6.QtWidgets import QTableWidget

def grab_metadata() -> bool:
    shortcuts = state.shortcuts
    for shortcut in shortcuts:
        # TODO: grab metadata
        pass
    
    return True