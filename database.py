from pymongo import MongoClient

from vars import DB_URI

MY_CLIENT = MongoClient(DB_URI)
MY_DB = MY_CLIENT["FILE_FORWARDER"]
MY_TABLE = MY_DB["channel_info"]
MY_TABLE_2 = MY_DB["word_replacee"]
SUDOER = MY_DB["SUDO"]
APPROVE = MY_DB["APPROVE"]
RSSANIME = MY_DB["RSS"]
RSS_UPDATE_CHANNEL = MY_DB["RSS_UPDATE_CHANNEL"]
RSS_USERS = MY_DB["RSS_USERS"]
CLEAN_MENTIONS = MY_DB["CLEAN_MENTIONS"]

def insert_clean_mentions(chat_id: int):
    if not CLEAN_MENTIONS.find_one({"chat_id": chat_id}):
        CLEAN_MENTIONS.insert_one({"chat_id": chat_id})
        return True

def remove_clean_mentions(chat_id: int):
    return bool(CLEAN_MENTIONS.find_one_and_delete({"chat_id": chat_id}))

def get_clean_mentions(chat_id: int | None = None):
    if chat_id:
        if curr := CLEAN_MENTIONS.find_one({"chat_id": chat_id}):
            return curr["chat_id"]
        else:
            return False
    curr = list(CLEAN_MENTIONS.find({}))
    if curr:
        return [int(i["chat_id"]) for i in curr]
    return []

def rss_update_channel(id: int):
    RSS_UPDATE_CHANNEL.update_one({"u": "u"}, {"$set": {"id": id}}, True)

def get_rss_update_channel():
    if curr:=RSS_UPDATE_CHANNEL.find_one({"u": "u"}):
        return curr["id"]

def insert_rss_user(user: str):
    if not get_rss_user(user):
        RSS_USERS.insert_one({"user": user})
        return True
    return False

def get_rss_user(user: str | None = None):
    if not user:
        return list(RSS_USERS.find({}))
    elif curr := RSS_USERS.find_one({"user": user}):
        return curr
    else:
        return False

def remove_rss_user(user: str):
    return bool(RSS_USERS.find_one_and_delete({"user": user})

def insert_approve_channel(id_: int):
    curr = APPROVE.find_one({"chat": id_})
    if not curr:
        APPROVE.insert_one({"chat": id_})
    return

def remove_approve_channel(id_: int):
    APPROVE.find_one_and_delete({"chat": id_})
    return

def aut_approve_channels():
    curr = APPROVE.find()
    if curr:
        return [int(i["chat"]) for i in curr]
    return []

def is_approve_channel(id_: int):
    return bool(APPROVE.find_one({"chat": id_}))

def insert_sudo(user):
    curr = SUDOER.find_one({"sudo": user})
    if curr:
        return
    else:
        SUDOER.insert_one({"sudo": user})
        return


def rm_sudo(user):
    SUDOER.find_one_and_delete({"sudo": user})
    return


def get_sudo():
    curr = list(SUDOER.find({}))
    if curr:
        user = [int(i["sudo"]) for i in curr]
    else:
        user = []

    return user


def insert_word(word):
    curr = MY_TABLE_2.find_one({"word": word})
    if curr:
        return
    else:
        curr = list(MY_TABLE_2.find({}))
        for i in curr:
            MY_TABLE_2.delete_one({"word":i["word"]})
        MY_TABLE_2.insert_one({"word": word})
        return


def rm_word():
    curr = list(MY_TABLE_2.find({}))
    if curr:
        word = curr[0]["word"]
        MY_TABLE_2.delete_one({"word": word})
    return


def update_word(word):
    curr = list(MY_TABLE_2.find({}))
    if curr:
        word_ = curr[0]["word"]
        MY_TABLE_2.update_one({"word": word_}, {"$set": {word}})
    return


def get_words():
    curr = list(MY_TABLE_2.find({}))
    if curr:
        word = curr[0]["word"]
        return word
    return False


def insert_channel(from_chat, to_chat):
    curr = MY_TABLE.find_one({"from_chat": from_chat, "to_chat": to_chat})
    if curr:
        return
    else:
        MY_TABLE.insert_one({"from_chat": from_chat, "to_chat": to_chat})
        return True


def get_from_chat():
    curr = list(MY_TABLE.find({}))
    if curr:
        to_return = [int(i["from_chat"]) for i in curr]
    else:
        to_return = []

    return to_return

def get_both():
    curr = list(MY_TABLE.find({}))
    if curr:
        return curr
    return []

def get_to_chat(from_chat):
    curr = MY_TABLE.find_one({"from_chat": from_chat})
    if curr:
        try:
            chat = int(curr["to_chat"])
        except:
            chat = curr["to_chat"]
        return chat 
    else:
        return None


def remove_chat(from_chat):
    curr = MY_TABLE.find_one_and_delete({"from_chat": from_chat})
    return


def update_chat(from_chat, to_chat):
    curr = MY_TABLE.find_one({"from_chat": from_chat, "to_chat": to_chat})
    if curr:
        return
    if not curr:
        curr = MY_TABLE.find_one({"to_chat": to_chat})
        new = {"from_chat": from_chat}
        filt = {"to_chat": to_chat}
    if not curr:
        curr = MY_TABLE.find_one({"from_chat": from_chat})
        new = {"to_chat": to_chat}
        filt = {"from_chat": from_chat}
    if curr:
        MY_TABLE.update_one(filt, {"$set": new})
    return

def insert_rss(link: str, title: str):
    if not find_rss(link):
        RSSANIME.insert_one({"title": title, "link": link})
        return True
    return False

def update_rss(link: str, new_title: str):
    RSSANIME.update_one({"link": link}, {"$set": {"title": new_title}}, True)
    return

def find_rss(link: str):
    if curr := RSSANIME.find_one({"link": link}):
        return curr
    return False
