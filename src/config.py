import configparser
from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[1]

CONFIG = configparser.ConfigParser()
CONFIG.read(PROJECT_ROOT / "config" / "config.ini")

API_TOKEN = CONFIG.get("Telegram", "Secret", fallback=None)
