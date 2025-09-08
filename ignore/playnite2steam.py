import os
import json
import zlib
import vdf
from pathlib import Path
import shutil

# --- CONFIG ---
PLAYNITE_EXPORT = "games.json"  # path to your exported JSON
PLAYNITE_IMAGES = Path(os.path.expandvars(r"%AppData%\Playnite\library"))
STEAM_USER_ID = "123595407"  # <-- replace with your Steam userdata folder
STEAM_PATH = Path(r"C:\Program Files (x86)\Steam")  # adjust if Steam elsewhere


SHORTCUTS_PATH = STEAM_PATH / "userdata" / STEAM_USER_ID / "config" / "shortcuts.vdf"
GRID_PATH = STEAM_PATH / "userdata" / STEAM_USER_ID / "config" / "grid"

CATEGORY = "No-steam"

# --- HELPERS ---

def steam_shortcut_id(exe, name):
    """Generate Steam shortcut AppID (same algo Steam uses)."""
    data = f"{exe}{name}".encode("utf-8")
    crc = zlib.crc32(data) & 0xFFFFFFFF
    appid = crc | 0x80000000  # non-Steam flag
    return str(appid)

def load_shortcuts(path):
    if path.exists() and path.stat().st_size > 0:
        with open(path, "rb") as f:
            return vdf.binary_load(f)
    # If file does not exist or is empty, return default structure
    return {"shortcuts": {}}

def save_shortcuts(data, path):
    with open(path, "wb") as f:
        vdf.binary_dump(data, f)

def copy_asset(src_rel, dest_name):
    """Copy an asset from Playnite library to Steam grid if exists."""
    if not src_rel:
        return None
    src = PLAYNITE_IMAGES / src_rel
    if src.exists():
        dest = GRID_PATH / dest_name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)
        return str(dest)
    return None

def main():
    # load JSON
    with open(PLAYNITE_EXPORT, "r", encoding="utf-8") as f:
        games = json.load(f)

    # load existing Steam shortcuts
    shortcuts = load_shortcuts(SHORTCUTS_PATH)

    for i, game in enumerate(games):
        if not game.get("IsInstalled"):
            continue

        name = game["Name"]
        actions = game.get("GameActions") or []
        play_action = next((a for a in actions if a.get("IsPlayAction")), None)
        if not play_action:
            continue

        exe = play_action["Path"].replace("{InstallDir}", game.get("InstallDirectory", ""))
        workdir = play_action["WorkingDir"].replace("{InstallDir}", game.get("InstallDirectory", ""))

        appid = steam_shortcut_id(exe, name)

        # Remove existing entry with the same name if exists
        to_delete = None
        for existing_id, existing_entry in shortcuts["shortcuts"].items():
            if existing_entry.get("AppName") == name:
                to_delete = existing_id
                break
        if to_delete:
            del shortcuts["shortcuts"][to_delete]
            

        entry = {
            "appid": appid,
            "AppName": name,
            "Exe": exe,
            "StartDir": workdir,
            "icon": "",
            "ShortcutPath": "",
            "LaunchOptions": "",
            "IsHidden": 0,
            "AllowDesktopConfig": 1,
            "AllowOverlay": 1,
            "OpenVR": 0,
            "Devkit": 0,
            "DevkitGameID": "",
            "LastPlayTime": 0,
            "tags": {"0": CATEGORY},
        }

        shortcuts["shortcuts"][str(i)] = entry

        # copy assets
        if game.get("Icon"):
            icon_path = copy_asset(game["Icon"], f"{appid}.ico")
            if icon_path:
                entry["icon"] = icon_path

        if game.get("CoverImage"):
            copy_asset(game["CoverImage"], f"{appid}p.jpg")  # portrait cover

        if game.get("BackgroundImage"):
            copy_asset(game["BackgroundImage"], f"{appid}_hero.jpg")  # hero image

    # save back to Steam
    save_shortcuts(shortcuts, SHORTCUTS_PATH)
    print("✅ Imported games with icons & artwork into Steam shortcuts.vdf")

if __name__ == "__main__":
    main()
