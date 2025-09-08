import sys
import state
import path_manager
import shortcut_manager
import gui_manager
import setup_manager
import logging
import qdarktheme

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

def main():
    logger.info("Initializing...")

    state.window, app = gui_manager.init_main_window()
    # Dark theme
    qdarktheme.setup_theme(additional_qss="QToolTip { border: 0px; }")

    if not setup_manager.validate_config():
        logger.info("Config invalid or missing, opening setup window...")
        setup_window = gui_manager.init_setup_window()

    # Get path to Steam installation
    # steam_path = state.steam_path
    # if steam_path == "":
    #     logger.error("Steam not found")
    #     # TODO: prompt to select steam path
    #     sys.exit("no_steam")
    # else:
    #     logger.info("Steam found at: %s", steam_path)

    # Get logged in users
    # TODO: pick in setup
    # user = state.user
    # logger.info("Picked user: %s", user)

    # Get shortcuts
    shortcuts_path = path_manager.get_shortcuts_path(state.steam_path, state.user)
    shortcuts = shortcut_manager.get_existing_shortcuts(shortcuts_path)
    logger.info("Found %i shortcut entries", len(shortcuts))

    # Display the list
    success = gui_manager.update_shortcut_list(shortcuts)
    if not success:
        logger.error("Can't find shortcuts table in UI")
        sys.exit("ui_shortcut_table_not_found")

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
