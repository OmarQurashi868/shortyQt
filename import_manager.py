import sys
import state
from PySide6.QtWidgets import QFileDialog
import logging

def import_exe():
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger()

    exe_path, _ = QFileDialog.getOpenFileName(
        state.window,
        "Select Executable",
        "",
        "Executable Files (*.exe)"
    )

    logger.info(exe_path)