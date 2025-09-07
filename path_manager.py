import os
import platform
import winreg
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

def get_steam_path() -> str:
    if platform.system() == "Windows":
        try:
            # Open registry key for Steam
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Valve\Steam")
            steam_path, _ = winreg.QueryValueEx(key, "SteamPath")
            winreg.CloseKey(key)
            return os.path.normpath(steam_path)
        except FileNotFoundError:
            return "C:\\Program Files (x86)\\Steam"
    elif platform.system() == "Linux":
        # TODO: linux support :)
        return ""
    else:
        return ""

def get_steam_users(steam_path: str) -> list[str]:
    userdata_path = os.path.join(steam_path, "userdata")
    try:
        _, users, _ = next(os.walk(userdata_path))
        logger.info("Found %s users", len(users))
        return users
    except StopIteration:
        return []

def get_shortcuts_path(steam_path: str, user: str) -> str:
    return os.path.join(steam_path, "userdata", user, "config", "shortcuts.vdf")
