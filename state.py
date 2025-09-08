from PySide6.QtWidgets import QWidget, QApplication

app: QApplication
window: QWidget
setup_dialog: QWidget

steam_path: str
user: str
api_key: str

shortcuts: dict[str, dict[str, str | int]]