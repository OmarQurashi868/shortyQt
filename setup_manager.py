import os
import platform
import gui_manager
import path_manager
import state
import json
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

def get_config_path() -> str:
    if platform.system() == "Windows":
        return os.path.join(os.getenv("APPDATA"), "SteamShorty", "config.json") # type: ignore
    elif platform.system() == "Linux":
        # TODO: linux support :)
        return ""
    else:
        return ""

def get_config() -> dict[str, str]:
    config_path = get_config_path()
    
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            logger.info("Loaded existing config")
            return config
    else:
        # Return defaults
        logger.info("No existing config found, using defaults...")
        steam_path = path_manager.get_steam_path()
        users = path_manager.get_steam_users(steam_path)
        user = ""
        if len(users) > 0:
            user = users[0]

        return {
            "steam_path": steam_path,
            "user":  user,
            "api_key": ""
        }

def save_config():
    config = {}
    
    config["steam_path"] = state.steam_path
    config["user"] = state.user
    config["api_key"] = state.api_key

    # Write file
    config_path = get_config_path()
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f)
        logger.info("Saved config")

def validate_config() -> bool:
    config = get_config()
    
    # Check steam and user(s) exist
    if not config["steam_path"]:
        logger.error("No Steam path provided")
        return False
    if not os.path.exists(os.path.join(config["steam_path"], "steam.exe")):
        logger.error("Invalid Steam path provided")
        return False
    logger.info("Steam found at: %s", config["steam_path"])


    if not config["user"]:
        logger.error("No users found")
        return False

    state.steam_path = config["steam_path"]
    state.user = config["user"]
    state.api_key = config["api_key"]

    logger.info("Config is valid")

    return True

def confirm_config():
    save_config()
    #gui_manager.update_shortcut_list()
    # TODO: kill setup window