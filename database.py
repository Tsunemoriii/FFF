from pymongo import MongoClient

from vars import DB_URI

MY_CLIENT = MongoClient(DB_URI)
MY_DB = MY_CLIENT["FILE_FORWARDER"]
MY_TABLE = MY_DB["channel_info"]
MY_TABLE_2 = MY_DB["word_replacee"]
SUDOER = MY_DB["SUDO"]


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
