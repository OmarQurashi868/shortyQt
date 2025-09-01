import os
import platform
import winreg
from main import logger

def get_steam_path() -> str:
    if platform.system() == "Windows":
        try:
            # Open registry key for Steam
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Valve\Steam")
            steam_path, _ = winreg.QueryValueEx(key, "SteamPath")
            winreg.CloseKey(key)
            logger.info("Steam found at -> %s", steam_path)
            return os.path.normpath(steam_path)
        except FileNotFoundError:
            logger.error("Steam not found")
            return ""
    elif platform.system() == "Linux":
        logger.error("Linux isn't supported yet")
        return "linux"
    else:
        logger.error("Could not determine operating system")
        return ""

def get_steam_users(steam_path: str) -> list[str]:
    return []

def get_shortcuts_path(steam_path: str, user: str) -> str:
    return ""
