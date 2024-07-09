from os import getenv

API_ID = int(getenv("API_ID", ""))
API_HASH = getenv("API_HASH", None)
BOT_TOKEN = getenv("BOT_TOKEN", None)
OWNER_ID = int(getenv("OWNER_ID", ""))
DB_URI = getenv("DB_URI", None)
SESSION = getenv("STRING_SESSION", None)
SUDO = [int(i.strip()) for i in getenv("SUDO", "").split(None)]
