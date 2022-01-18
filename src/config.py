import configparser
from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[1]

CONFIG = configparser.ConfigParser(interpolation=None)
CONFIG.read(PROJECT_ROOT / "config" / "config.ini")

API_TOKEN = CONFIG.get("Telegram", "Secret", fallback=None)

EVENTS_URL = CONFIG.get("Events", "Url", fallback=None)
EVENTS_MAX_RESULTS = CONFIG.getint("Events", "MaxResults", fallback=6)
EVENTS_MAX_DAYS = CONFIG.getint("Events", "MaxDays", fallback=-1)
EVENTS_CACHE_SECONDS = CONFIG.getint("Events", "Cache", fallback=900)


def events_enabled() -> bool:
    return bool(EVENTS_URL)
