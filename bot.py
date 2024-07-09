import asyncio
from re import findall

from pyrogram import Client, filters, idle
from pyrogram.enums import ChatType as CT
from pyrogram.enums import ParseMode
from pyrogram.types import Message

from database import *
from vars import *

bot = Client(
    "My_bot",
    API_ID,
    API_HASH,
    bot_token=BOT_TOKEN
)

ub = Client(
    "MY_USERBOT",
    API_ID,
    API_HASH,
    session_string=SESSION
)

bot.start()

print("Starting userbot...")
ub.start()
print("Userbot started")

bot.alive = True


def load_sudo():
    sudo = SUDO
    if sudo:
        for i in sudo:
            insert_sudo(int(i))
    return


load_sudo()

pm = ParseMode.HTML


async def bot_owner_filt(_, __, m: Message):
    sudo = get_sudo()
    sudo.append(OWNER_ID)
    if m.from_user and m.from_user.id not in sudo:
        return False
    else:
        return True


async def replaceshits(tex):
    for i in findall(r"(@[A-Za-z0-9_]*[A-Za-z]+[A-Za-z0-9_]*( |$|\b))", tex):
        tex = tex.replace(i[0], "")
    for i in findall(
            r"((http(s)?://)?(t|telegram)\.(me|dog)/[A-Za-z0-9_]+( |$|\b))",
            tex):
        tex = tex.replace(i[0], "")

    words = get_words()
    if words:
        word_list = words.split()
        for x in word_list:
            tex = tex.replace(x, "")
    return tex


async def channel_filters(_, __, m: Message):
    if m.chat.type == CT.PRIVATE:
        return False
    all_chats = get_from_chat()
    if all_chats and m.chat.id in all_chats:
        return True
    else:
        return False

bot_owner = filters.create(bot_owner_filt)
channel_filt = filters.create(channel_filters)

print(f"Bot started on @{bot.me.username}")


@bot.on_message(filters.command("start"))
async def I_am_ALIVE(c: bot, m: Message):
    is_on = c.alive
    txt = "Hi there! I can forward message from one chat to another\nType /help to know the available commands"
    if is_on:
        txt += "\nForwarding is currently on"
    else:
        txt += "\nForwarding is currently off"
    await m.reply_text(txt)


@bot.on_message(filters.command("help"))
async def what_can_I_do(_, m: Message):
    txt = """
⤷ /add [from channel id] [to channel id] : Will start forwarding every new message from channel to destination
⤷ /disconnect [from channel id] : Will remove forwarding from the channel
⤷ /update [from channel id] [to channel id] **(One paramete either from channel or to channel should be same as previous one)**
⤷ /forwarding [on | off]: Will stop/start the forwarding of from channel
⤷ /addword [reply_to_message]: Will add replied text as text remove in the chat given
⤷ /rmword: Will remove word removal from the chat
⤷ /updateword [reply to message]: Will update word removal of the chat
⤷ /getforward : Will return the channel where forwarding is enabled
⤷ /forward [channel id] link1-link2: Will forward msg from link1 to link2 (channel id is of the channel where you want to forward the msg)

from channel: it is the channel from you want to start forwarding messages, you can say source.
to channel: it is the channel where the forwarded message will be sent, you can say destination

If you want to forward the content to a bot or an user just instead of id of to channel give me username of the bot with @
"""
    await m.reply_text(txt)

@bot.on_message(filters.command("forward"))
async def forward_old_msg(c: bot, m: Message):
    if len(m.command) < 2:
        await m.reply_text("**Usage**\n/forward [channel id] link1 - link2")
        return
    
    splited = m.text.split(None,2)
    try:
        to_chat_id = int(splited[1].strip())
    except:
        await m.reply_text("Channel id should be integer") 
        return
    
    links = splited[-1].strip().split("-")
    if len(links) !=2:
        await m.reply_text("Give me only two links")
        return
    msg_ids = [links[0].strip().split("/")[-1], links[1].strip().split("/")[-1]]
    from_msg = int(min(msg_ids))
    to_msg = int(max(msg_ids))
    from_chat = links[0].strip().split("/")[-2]
    from_chat = await ub.resolve_peer(int(from_chat))
    from_chat_id = from_chat.channel_id

    to_edit = await m.reply_text(f"Frowarding {to_msg - from_msg} from chat id `{from_chat_id}` to `{to_chat_id}`")
    success = 0
    failed = 0
    empty = 0

    for i in range(from_msg, to_msg+1):
        try:
            msg = await ub.get_messages(from_chat_id, i)
            if msg.empty:
                empty += 1
                continue
            
            elif msg.text:
                text = msg.text.html
                new_cap = await replaceshits(text)
                await ub.send_message(to_chat_id, new_cap, disable_web_page_preview=True)
                success += 1

            elif msg.caption:
                text = m.caption.html
                new_cap = await replaceshits(text)
                await ub.copy_message(to_chat_id, from_chat_id, msg.id, new_cap, pm)
                success += 1

            else:
                failed += 1
                continue
        except:
            failed += 1
            continue
    
    await to_edit.delete()
    await m.reply_text(f"Successfully forward {success} messages\nTotal empty messages skipped: {empty}\nFailed to forward: {failed} messages")
    return

@bot.on_message(filters.command("forwarding") & bot_owner)
async def forwarding_switch(c: bot, m: Message):
    is_started = c.alive
    if len(m.command) != 2:
        await m.reply_text(f"Usage\n`/forwarding {'off' if is_started else 'on'}` to {'stop' if is_started else 'start'} forwarding")
        return

    to_do = m.command[1].lower()
    if to_do not in ["on", "off"]:
        await m.reply_text(f"Usage\n`/forwarding {'off' if is_started else 'on'}` to {'stop' if is_started else 'start'} forwarding")
        return
    elif to_do == "on":
        if is_started:
            txt = "Forwarding from channel is already on"
        else:
            c.alive = True
            txt = "Forwarding from channel is now on"
    else:
        if not is_started:
            txt = "Forwarding from channel is already off"
        else:
            c.alive = False
            txt = "Forwarding from channel is now off"

    await m.reply_text(txt)
    return


@ub.on_message(filters.command("add") & bot_owner)
async def add_this_one(_, m: Message):
    if len(m.command) != 3:
        await m.reply_text("/add [from channel] [to channel]")
        return

    try:
        channel_from = int(m.command[1])
    except ValueError:
        await m.reply_text("**from channel id** should be integers")
        return

    try:
        channel_to = int(m.command[2])
    except ValueError:
        if m.command[2].startswith("@"):
            channel_to = m.command[2]
        else:
            await m.reply_text("**to channel should be id of the channel or if you want to forward it to an user or bot give me their username and it should be start with @.")
            return

    try:
        if type(channel_to) == int:
            await ub.get_chat_member(channel_to, ub.me.id)
        else:
            channel_to = (await ub.get_users(channel_to)).username
            channel_to = "@"+channel_to
    except Exception as e:
        await m.reply_text(f"Line 173:\n{e}")
        return

    try:
        await ub.join_chat(int(channel_from))
    except Exception as e:
        await m.reply_text(f"Error while joining:\n{e}")
        return

    insert_channel(channel_from, channel_to)

    await m.reply_text(f"Forwarding is now started from `{channel_from}` to `@{channel_to}`")
    return

@bot.on_message(filters.command("getforward") & bot_owner)
async def get_forwardd(_, m: Message):
    both = get_both()
    if both:
        txt = "From channel -> To channel\n"
        for i in both:
            txt += f"\n`{i['from_chat']}` -> `{i['to_chat']}`"
    else:
        txt = "No chat found"
    
    await m.reply_text(txt)
    return

@bot.on_message(filters.command("disconnect") & bot_owner)
async def remove_this_channel(_, m: Message):
    if len(m.command) != 2:
        await m.reply_text("/disconnect [from channel id]")
        return

    try:
        f_chat = int(m.command[1])
    except ValueError:
        await m.reply_text("From channel it should be integer")
        return

    remove_chat(f_chat)
    await m.reply_text(f"Removed forwarding from this (`{f_chat}`) channel")
    return


@bot.on_message(filters.command("update") & bot_owner)
async def update_chat_pls(c: bot, m: Message):
    if len(m.command) != 3:
        await m.reply_text("/update [from channel] [to channel]")
        return

    try:
        channel_from = int(m.command[1])
    except ValueError:
        await m.reply_text("**from channel id** should be integers")
        return

    try:
        channel_to = int(m.command[2])
    except ValueError:
        if m.command[2].startswith("@"):
            channel_to = m.command[2]
        else:
            await m.reply_text("**to channel should be id of the channel or if you want to forward it to an user or bot give me their username and it should be start with @.")
            return

    try:
        if type(channel_to) == int:
            await ub.get_chat_member(channel_to, ub.me.id)
        else:
            channel_to = (await ub.get_users(channel_to)).username
            channel_to = "@"+channel_to
    except Exception as e:
        await m.reply_text(f"Line 247:\n{e}")
        return

    update_chat(channel_from, channel_to)

    await m.reply_text(f"Forwarding is now started from `{channel_from}` to `{channel_to}`")
    return


@bot.on_message(filters.command("addword") & bot_owner)
async def add_removal_words(_, m: Message):
    repl = m.reply_to_message
    if not repl:
        await m.reply_text("Reply to a message to add the word")
        return
    elif repl and not repl.text:
        await m.reply_text("Replied message should be text")
        return

    txt = repl.text

    insert_word(txt)

    await m.reply_text("Added this word")
    return


@bot.on_message(filters.command("updateword") & bot_owner)
async def update_the_words(_, m: Message):
    repl = m.reply_to_message
    if not repl:
        await m.reply_text("Reply to a message to add the word")
        return
    elif repl and not repl.text:
        await m.reply_text("Replied message should be text")
        return

    txt = repl.text

    update_word(txt)
    await m.reply_text("Update the text")
    return


@bot.on_message(filters.command("rmword") & bot_owner)
async def remove_this_word(c: bot, m: Message):
    rm_word()

    await m.reply_text("Removed word from the chat")


@bot.on_message(filters.command("addsudo") & filters.user(OWNER_ID))
async def add_more_sudo(_, m: Message):
    repl = m.reply_to_message
    if len(m.command) != 2 or not repl:
        await m.reply_text("/addsudo [user id | reply to user]")
        return
    if len(m.command) == 2:
        try:
            user = int(m.command[1])
        except ValueError:
            await m.reply_text("User id should be integer")
            return
    elif repl:
        if not repl.from_user:
            await m.reply_text("Reply to an user")
            return
        user = repl.from_user.id

    insert_sudo(user)
    await m.reply_text(f"Add `{user}` to sudoers")
    return


@bot.on_message(filters.command("rmsudo") & filters.user(OWNER_ID))
async def add_more_sudo(_, m: Message):
    repl = m.reply_to_message
    if len(m.command) != 2 or not repl:
        await m.reply_text("/rmsudo [user id | reply to user]")
        return
    if len(m.command) == 2:
        try:
            user = int(m.command[1])
        except ValueError:
            await m.reply_text("User id should be integer")
            return
    elif repl:
        if not repl.from_user:
            await m.reply_text("Reply to an user")
            return
        user = repl.from_user.id

    rm_sudo(user)
    await m.reply_text(f"Removed `{user}` to sudoers")
    return


@ub.on_message(channel_filt)
async def watcher(_, m: Message):
    if not bot.alive:
        return
    to_chat = get_to_chat(m.chat.id)

    if m.text:
        text = m.text.html
        new_cap = await replaceshits(text)
        await ub.send_message(to_chat, new_cap, disable_web_page_preview=True)
        return

    if m.caption:
        text = m.caption.html
        new_cap = await replaceshits(text)

    await ub.copy_message(to_chat, m.chat.id, m.id, caption=new_cap, parse_mode=pm)

idle()
