import sys
import path_manager
import shortcut_manager
import logging
from PySide6 import QtWidgets
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

app = QtWidgets.QApplication([])

ui_file = QFile("main_window.ui")
ui_file.open(QFile.OpenModeFlag.ReadOnly)
loader = QUiLoader()
window = loader.load(ui_file)
ui_file.close()
if not window:
    print(loader.errorString())
    sys.exit(-1)
window.show()

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

shortcuts = shortcut_manager.get_existing_shortcuts(shortcuts_path)
if not shortcuts:
    logger.error("Error reading shortcuts.vdf")
    sys.exit("shortcut_read_error")

shortcuts_list = window.findChild(QtWidgets.QTableWidget, "shortcutsList")
if not shortcuts_list:
    logger.error("Can't find shortcuts table in UI")
    sys.exit("ui_shortcut_table_not_found")

columns = ["AppId", "AppName", "Path", "Image"]
entry_columns = ["appid", "AppName", "Exe", "icon"]

shortcuts_list.setRowCount(len(shortcuts))
shortcuts_list.setColumnCount(4)
shortcuts_list.setHorizontalHeaderLabels(columns)

for row_idx, entry in enumerate(shortcuts.values()):
    for col_idx, col in enumerate(columns):
        item = QtWidgets.QTableWidgetItem(col)
        item.setText(str(entry[entry_columns[col_idx]]))
        shortcuts_list.setItem(row_idx, col_idx, item)

# Exit
sys.exit(app.exec())