from os import getenv

API_ID = int(getenv("API_ID", "20628383"))
API_HASH = getenv("API_HASH", "65a242463b8af9ba7b3c41d8de9738d1")
BOT_TOKEN = getenv("BOT_TOKEN", "7360043493:AAESptsDLQskNMaJfedW2pD-YPk83-tVKnU")
OWNER_ID = int(getenv("OWNER_ID", "1921693263"))
DB_URI = getenv("DB_URI", "mongodb+srv://utahakane008:utahakane008@cluster0.ugnnf20.mongodb.net/?retryWrites=true&w=majority")
SESSION = getenv("STRING_SESSION", "")
SUDO = [int(i.strip()) for i in getenv("SUDO", "").split(None)]
