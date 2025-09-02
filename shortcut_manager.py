import os
import vdf

def get_existing_shortcuts(shortcuts_path: str) -> dict[str, str]:
    if os.path.exists(shortcuts_path):
        with open(shortcuts_path, "rb") as f:
            return vdf.binary_load(f)['shortcuts']
    return {}


def set_new_shortcuts(shortcuts: dict, shortcuts_path: str):
    if os.path.exists(shortcuts_path):
        with open(shortcuts_path, "wb") as f:
            vdf.binary_dump(shortcuts, f)
            