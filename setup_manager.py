import os
import platform
import gui_manager
import path_manager
import shortcut_manager
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

        return {
            "steam_path": steam_path,
            "user":  "",
            "api_key": ""
        }
    
def load_config():
    config = get_config()

    state.steam_path = config["steam_path"]
    state.user = config["user"]
    state.api_key = config["api_key"]

def save_config():
    config = {}
    
    config["steam_path"] = state.steam_path
    config["user"] = state.user
    config["api_key"] = state.api_key

    # Write file
    config_path = get_config_path()
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f)
        logger.info("Saved config")

def validate_config(steam_path: str) -> bool:
    # Check steam install
    if not is_steam_exists(steam_path):
        logger.error("Invalid Steam path provided")
        return False
    logger.info("Steam found at: %s", steam_path)

    # Check user existence
    if not path_manager.get_steam_users(steam_path):
        logger.error("No users found")
        return False

    logger.info("Config is valid")

    return True

def is_steam_exists(path: str) -> bool:
    if not path or not os.path.exists(os.path.join(path, "steam.exe")):
        return False
    else:
        return True

def on_path_change(path: str):
    if not is_steam_exists(path):
        state.config_window.pathLabel.setText("Steam installation NOT found") # type: ignore
        state.config_window.pathLabel.setStyleSheet(f"color: {"red"};") # type: ignore
        state.config_window.userSelect.clear() # type: ignore
        state.config_window.buttonBox.setEnabled(False) # type: ignore
        return
    
    state.config_window.pathLabel.setText("Steam installation found") # type: ignore
    state.config_window.pathLabel.setStyleSheet(f"color: {"green"};") # type: ignore
    users = path_manager.get_steam_users(path)
    state.config_window.userSelect.addItems(users) # type: ignore
    state.config_window.userSelect.setCurrentIndex(0) # type: ignore
    state.config_window.buttonBox.setEnabled(True) # type: ignore

def confirm_config():
    steam_path = state.config_window.pathField.text() # type: ignore
    if not validate_config(steam_path):
        logger.error("Config is invalid")
        return
    
    state.steam_path = steam_path
    state.user = state.config_window.userSelect.currentText() # type: ignore
    state.api_key = state.config_window.apiField.text() # type: ignore

    save_config()
    shortcuts_path = path_manager.get_shortcuts_path(state.steam_path, state.user)
    state.shortcuts = shortcut_manager.get_existing_shortcuts(shortcuts_path)
    gui_manager.update_shortcut_list(state.shortcuts)