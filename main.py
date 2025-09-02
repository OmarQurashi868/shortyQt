import sys
import path_manager
import shortcut_manager
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

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

existing_shortcuts = shortcut_manager.get_existing_shortcuts(shortcuts_path)
print('existing shortcuts: ', existing_shortcuts)

# Exit
logger.info("Exiting")
sys.exit(0)