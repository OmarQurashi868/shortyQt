import state
import requests
import gui_manager
import shortcut_manager
from PySide6.QtWidgets import QTableWidget
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


def grab_metadata():
    if not state.api_key:
        logger.error("No API key for SteamGridDB defined in config")
        return
    
    url = "https://www.steamgriddb.com/api/v2"

    headers = {"Authorization": f"Bearer {state.api_key}"}

    shortcuts = state.shortcuts
    for _, k in enumerate(shortcuts):
        # grab metadata
        shortcut = shortcuts[k]
        query = shortcut["AppName"]

        search_url = f"{url}/search/autocomplete/{query}"
        resp = requests.get(search_url, headers=headers)
        data = resp.json()

        if "data" not in data or not data["data"]:
            logger.error("No metadata match found for: %s", query)
            continue

        game = data["data"][0]  # best match
        game_id = game["id"]
        game_name = game["name"]

        state.shortcuts[k]["AppName"] = game_name
        shortcut_manager.set_new_shortcuts()
        gui_manager.update_shortcut_list(state.shortcuts)
