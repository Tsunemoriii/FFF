from os import getenv

API_ID = int(getenv("API_ID", "20628383"))
API_HASH = getenv("API_HASH", "65a242463b8af9ba7b3c41d8de9738d1")
BOT_TOKEN = getenv("BOT_TOKEN", "7360043493:AAGSteBwOG1b1J1qOQ5MvepmVJ_y43R8LVc")
OWNER_ID = int(getenv("OWNER_ID", "1921693263"))
DB_URI = getenv("DB_URI", "mongodb+srv://utahakane008:utahakane008@cluster0.ugnnf20.mongodb.net/?retryWrites=true&w=majority")
SESSION = getenv("STRING_SESSION", "")
SUDO = [int(i.strip()) for i in getenv("SUDO", "").split(None)]
RSSUSERS = getenv("RSSUSERS", "Ember_Encodes Judas varyg1001").split(None)
UPDATE_CHANNEL = int(getenv("UPDATE_CHANNEL", "-1001252296278"))
