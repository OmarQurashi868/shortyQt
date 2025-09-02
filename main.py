import sys
import state
import path_manager
import shortcut_manager
import gui_manager
import logging

def main():
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger()

    state.window, app = gui_manager.init_window()

    # Get path to Steam installation
    steam_path = path_manager.get_steam_path()
    if steam_path == "":
        logger.error("Steam not found")
        # TODO: prompt to select steam path
        sys.exit("no_steam")
    else:
        logger.info("Steam found at: %s", steam_path)

    # Get logged in users
    users = path_manager.get_steam_users(steam_path)
    if len(users) < 1:
        # No logged in users found
        # TODO: show error dialog
        logger.error("No steam users found")
        sys.exit("no_users")
    elif len(users) > 1:
        # Multiple logged in users found
        # TODO: prompt to select users
        logger.info("User selected: %s", users[0])
        shortcuts_path = path_manager.get_shortcuts_path(steam_path, users[0])
    else:
        # Exactly one logged in user found
        logger.info("One user found: %s", users[0])
        shortcuts_path = path_manager.get_shortcuts_path(steam_path, users[0])

    # Get shortcuts
    shortcuts = shortcut_manager.get_existing_shortcuts(shortcuts_path)
    if not shortcuts:
        logger.error("Error reading shortcuts.vdf")
        # TODO: show error dialog
        #gui_manager.popup(window, "Error", "Error reading shortcuts.vdf")
        sys.exit("shortcut_read_error")
    logger.info("Found shortcuts containing %i entries", len(shortcuts))

    # Display the list
    success = gui_manager.update_shortcut_list(shortcuts)
    if not success:
        logger.error("Can't find shortcuts table in UI")
        sys.exit("ui_shortcut_table_not_found")

    sys.exit(app.exec())

if __name__ == "__main__":
    main()

existing_shortcuts = shortcut_manager.get_existing_shortcuts(shortcuts_path)
print('existing shortcuts: ', existing_shortcuts)

# Exit
logger.info("Exiting")
sys.exit(0)