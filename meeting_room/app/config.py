from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"
ROOMS_FILE = DATA_DIR / "rooms.json"
BOOKINGS_FILE = DATA_DIR / "bookings.json"
USERS_FILE = DATA_DIR / "users.json"
AUTO_RELEASE_INTERVAL_SECONDS = 60
