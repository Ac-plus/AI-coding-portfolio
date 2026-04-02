from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
ROOMS_FILE = DATA_DIR / "rooms.json"
BOOKINGS_FILE = DATA_DIR / "bookings.json"
AUTO_RELEASE_INTERVAL_SECONDS = 60
