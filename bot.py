import asyncio
import httpx
import re

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bs4 import BeautifulSoup as soup
from pyrogram import Client, filters, idle
from pyrogram.enums import ChatMemberStatus as CMS
from pyrogram.enums import ChatType as CT
from pyrogram.enums import MessageEntityType as MET
from pyrogram.enums import ParseMode
from pyrogram.types import ChatJoinRequest, Message

from database import *
from vars import *

bot: Client = Client(
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


scheduler = AsyncIOScheduler()

RSS_CACHE = dict()

rss_users = RSSUSERS

update_channel = get_rss_update_channel() or UPDATE_CHANNEL

async def anime_updates():
    if not rss_users:
        return
    updates = []
    for rssuser in rss_users:
        rsslink = f"https://nyaa.si/?page=rss&c=0_0&f=0&u={rssuser}"
        if "nyaa.si" in rssuser:
            rsslink = rssuser
        parsed = soup(httpx.get(rsslink).text, features="html.parser")
        title = str(parsed.find("item").find("title"))
        if not find_rss(rsslink):
            insert_rss(rsslink, title)
            return

        for element in parsed.findAll("item"):
            already = RSS_CACHE.get(rsslink, False) or find_rss(rsslink).get("title", False)
            if already == str(element.find("title")):
                break
            updates.append([str(element.find("title")), (re.sub(r"<.*?>(.*)<.*?>", r"\1", str(element.find("guide")))).replace("view", "download")+".torrent"])
        update_rss(rsslink, title)
        RSS_CACHE[rsslink] = title
    
    for update in updates:
        try:
            await bot.send_message(update_channel, f"Found 👀New Anime👀\n\n{update[0]}\n{update[1]}")
        except Exception as e:
            print(e)
            continue


def load_vars():
    if not get_rss_update_channel():
        rss_update_channel(UPDATE_CHANNEL)

    for user in RSSUSERS:
        insert_rss_user(user)

    global rss_users
    
    rss_users = [i["user"] for i in get_rss_user()]

    sudo = SUDO
    if sudo:
        for i in sudo:
            insert_sudo(int(i))
    return


pm = ParseMode.HTML


async def bot_owner_filt(_, __, m: Message):
    sudo = get_sudo()
    sudo.append(OWNER_ID)
    if m.from_user and m.from_user.id not in sudo:
        return False
    else:
        return True

async def approve_chan(_, __, r: ChatJoinRequest):
    return is_approve_channel(r.chat.id)

async def replaceshits(tex):
    """for i in findall(r"(@[A-Za-z0-9_]*[A-Za-z]+[A-Za-z0-9_]*( |$|\b))", tex):
        tex = tex.replace(i[0], "")
    for i in findall(
            r"((http(s)?://)?(t|telegram)\.(me|dog)/[A-Za-z0-9_]+( |$|\b))",
            tex):
        tex = tex.replace(i[0], "")

    words = get_words()
    if words:
        word_list = words.split()
        for x in word_list:
            tex = tex.replace(x, "")"""
    return tex

async def del_username(_, __, m: Message):
    if m.chat.type == CT.PRIVATE:
        return False
    
    entities = None

    if m.caption:
        entities = m.caption.entities
    elif m.text:
        entities = m.text.entities

    if entities:
        for entity in entities:
            if entity.type == MET.MENTION:
                return True
    
    return False

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
allowed_approve = filters.create(approve_chan)
delete_mention = filters.create(del_username)


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
⤷ /approveall [channel id]: Will approve all the pending request in the chat.
⤷ /addapprove (/connect) [channel id]: Will add approve channel to database, will start auto approve.
⤷ /delapprove (/disconnect) [channel id]: Will remove chat from database, Will not auto approve.
from channel: it is the channel from you want to start forwarding messages, you can say source.
⤷ /rsschannel [channel id]: Will add the channel to the database, will send the updates of new anime to this chat
⤷ /addrssuser [rss_user]: Will add the user to the database, will send the updates of new anime to this user
⤷ /rmrssuser [rss_user]: Will remove the user from the database, will not send the updates of new anime to this user

to channel: it is the channel where the forwarded message will be sent, you can say destination

If you want to forward the content to a bot or an user just instead of id of to channel give me username of the bot with @
"""
    await m.reply_text(txt)

async def accept_join_req(chat: int, user: int):
    is_done = await ub.approve_all_chat_join_requests(chat)
    try:
        await bot.send_message(user, f"{'Approved' if is_done else 'Failed to approve'} all the pending join requests in the chat {chat}")
    except:
        try:
            await ub.send_message(user, f"{'Approved' if is_done else 'Failed to approve'} all the pending join requests in the chat {chat}")
        except:
            pass
    return
@bot.on_message(filters.command("approveall"))
async def approve_all_pendings(_, m: Message):
    if len(m.command) != 2:
        await m.reply_text("Please provide me chat id")
        return
    
    try:
        id_ = int(m.command[1])
    except ValueError:
        await m.reply_text("Chat id should be integer")
        return
    
    try:
        status = await bot.get_chat_member(id_, ub.me.id)
        if status.status not in [CMS.OWNER, CMS.ADMINISTRATOR]:
            await m.reply_text(f"Please make sure `{ub.me.id}` ({('@'+ub.me.username) if ub.me.username else ub.me.mention}) this id is admin in the given chat")
            return
    except:
        await m.reply_text(f"Please make sure `{ub.me.id}` ({('@'+ub.me.username) if ub.me.username else ub.me.mention}) this id and the bot ({bot.me.username}) are admin in the given chat")
        return
    await m.reply_text("Added the task in background I will let you know once the task gets completed")
    target = m.from_user.id if m.from_user else m.chat.id
    asyncio.create_task(accept_join_req(id_, target))

@bot.on_message(filters.command(["addapprove", "conntect"]) & bot_owner)
async def start_approving(_, m: Message):
    if len(m.command) != 2:
        await m.reply_text("Please give me chat id")
    
    
    try:
        id_ = int(m.command[1])
    except ValueError:
        await m.reply_text("Chat id should be integer")
        return
    
    try:
        meh = await bot.get_chat_member(id_, bot.me.id)
        if meh.status not in [CMS.OWNER, CMS.ADMINISTRATOR]:
            await m.reply_text("Make sure I am admin in the chat")
            return
    except:
        await m.reply_text("Please make sure I am part of the group chat and also an admin there")
        return
    
    insert_approve_channel(id_)
    await m.reply_text("I have added the chat in the auto approve chat. Now I will approve all the incoming request")
    return

@bot.on_message(filters.command(["delapprove", "disconnect"]) & bot_owner)
async def stop_approving(_, m: Message):
    if len(m.command) != 2:
        await m.reply_text("Please give me chat id")


    try:
        id_ = int(m.command[1])
    except ValueError:
        await m.reply_text("Chat id should be integer")
        return

    remove_approve_channel(id_)

    await m.reply_text("Removed the chat from the database. I will not approve any incoming requests")
    return

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
    try:
        links = splited[-1].strip().split("-")
        if len(links) !=2:
            await m.reply_text("Give me only two links")
            return
        msg_ids = [int(links[0].strip().split("/")[-1]), int(links[1].strip().split("/")[-1])]
        from_msg = int(min(msg_ids))
        to_msg = int(max(msg_ids))
        from_chat = links[0].strip().split("/")
        if from_chat[-3] == "c":
            from_chat_id = int("-100"+from_chat[-2])
        else:
            from_chat_id = from_chat[-2]

        to_edit = await m.reply_text(f"Frowarding {to_msg - from_msg} from chat id `{from_chat_id}` to `{to_chat_id}`")
        success = 0
        failed = 0
        empty = 0
        for i in range(from_msg, to_msg+1):
            print(i)
            try:
                msg = await ub.get_messages(from_chat_id, i)
                if msg.empty:
                    empty += 1
                    await asyncio.sleep(8)
                    continue
                
                elif msg.media:
                    if msg.caption:
                        text = msg.caption.html
                        new_cap = await replaceshits(text)
                    else:
                        new_cap = None 
                    await ub.copy_message(to_chat_id, from_chat_id, msg.id, new_cap, pm)
                    await asyncio.sleep(8)
                    success += 1
                    continue
                
                elif msg.text:
                    text = msg.text.html
                    new_cap = await replaceshits(text)
                    await ub.send_message(to_chat_id, new_cap, disable_web_page_preview=True)
                    success += 1
                    await asyncio.sleep(8)
                    continue
                    
                else:
                    failed += 1
                    await asyncio.sleep(8)
                    continue
            except Exception as e:
                print(e)
                failed += 1
                await asyncio.sleep(8)
                continue
        
        await to_edit.delete()
        await m.reply_text(f"Successfully forward {success} messages\nTotal empty messages skipped: {empty}\nFailed to forward: {failed} messages")
    except Exception as e:
        await m.reply_text(f"Got an error\n{e}")
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

@bot.on_message(filters.command("addrssuser") & bot_owner)
async def add_rss_user(_, m: Message):
    if len(m.command) != 2:
        await m.reply_text("Please give me rss user")
        return
    
    user = m.command[1].strip()
    
    global rss_users
    if user in rss_users:
        await m.reply_text("User already in the database")
        return

    insert_rss_user(user)
    rss_users.append(user)
    await m.reply_text("Added the user to the database. I will send the updates of new anime from this rss user")
    return

@bot.on_message(filters.command("rmrssuser") & bot_owner)
async def remove_rss_user(_, m: Message):
    if len(m.command) != 2:
        await m.reply_text("Please give me rss user")
        return
    
    user = m.command[1].strip()
    
    global rss_users
    if user not in rss_users:
        await m.reply_text("User not in the database")
        return

    remove_rss_user(user)
    rss_users.remove(user)
    await m.reply_text("Removed the user from the database. I will not send the updates of new anime from this rss user")
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

@bot.on_message(delete_mention)
async def delete(_, m: Message):
    try:
        await m.delete()
    except:
        try:
            await ub.delete_messages(m.chat.id, m.id)
        except:
            pass
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

@bot.on_chat_join_request(allowed_approve)
async def approve_this_user(_, r: ChatJoinRequest):
    await r.approve()
    return

@bot.on_message(filters.command("rsschannel") & bot_owner)
async def add_rss_channel(_, m: Message):
    if len(m.command) != 2:
        await m.reply_text("Please give me channel id")
        return
    
    try:
        id_ = int(m.command[1])
    except ValueError:
        await m.reply_text("Channel id should be integer")
        return
    
    global update_channel
    update_channel = id_

    try:
        meh = await bot.get_chat_member(id_, bot.me.id)
        if meh.status not in [CMS.OWNER, CMS.ADMINISTRATOR]:
            await m.reply_text("Make sure I am admin in the chat")
            return
    except:
        await m.reply_text("Please make sure I am part of the group chat and also an admin there")
        return
    
    rss_update_channel(id_)
    await m.reply_text("Added the channel to the database. I will send the updates of new anime to this chat")
    return


async def main():
    await bot.start()
    scheduler.add_job(anime_updates, "interval", minutes=5, max_instances=5)

    print("Starting userbot...")
    await ub.start()
    print("Userbot started")

    scheduler.start()
    print("Scheduler started")   

    bot.alive = True

    load_vars()
    print(f"Bot started on @{bot.me.username}")

    print("Loaded sudo users. Bot is now ready to use")

    await idle()

    print("Stopping bot...")

    await bot.stop()
    await ub.stop()

asyncio.get_event_loop().run_until_complete(main())
