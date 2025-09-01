import logging
import path_manager

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

path_manager.get_steam_path()
logger.info("Exiting")