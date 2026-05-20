import asyncio
from typing import Dict, List, Union

from pyrogram import filters, Client
from pyrogram.enums import ChatMembersFilter
from pyrogram.errors import (
    FloodWait,
    RPCError,
    PeerIdInvalid,
    UserIsBlocked,
    UserDeactivated,
    AuthKeyUnregistered
)

from Clonify import app
from Clonify.misc import SUDOERS
from Clonify.utils.database import (
    get_active_chats,
    get_authuser_names,
    get_client,
    get_served_chats,
    get_served_users,
)
from Clonify.utils.database.clonedb import (
    get_all_clones,
    get_served_chats_clone,
    get_served_users_clone,
    get_clonebot_owner
)
from Clonify.utils.decorators.language import language
from Clonify.utils.formatters import alpha_to_int
from config import adminlist, API_ID, API_HASH

# Global Flags
IS_BROADCASTING = False
IS_CBROADCASTING = False

# ==========================================
#        NORMAL BROADCAST COMMAND
# ==========================================

@app.on_message(filters.command("broadcast") & SUDOERS)
@language
async def braodcast_message(client, message, _):
    global IS_BROADCASTING
    if message.reply_to_message:
        x = message.reply_to_message.id
        y = message.chat.id
    else:
        if len(message.command) < 2:
            return await message.reply_text(_["broad_2"])
        query = message.text.split(None, 1)[1]
        if "-pin" in query:
            query = query.replace("-pin", "")
        if "-nobot" in query:
            query = query.replace("-nobot", "")
        if "-pinloud" in query:
            query = query.replace("-pinloud", "")
        if "-assistant" in query:
            query = query.replace("-assistant", "")
        if "-user" in query:
            query = query.replace("-user", "")
        if query.strip() == "":
            return await message.reply_text(_["broad_8"])

    IS_BROADCASTING = True
    await message.reply_text(_["broad_1"])

    if "-nobot" not in message.text:
        sent = 0
        pin = 0
        chats = []
        schats = await get_served_chats()
        for chat in schats:
            chats.append(int(chat["chat_id"]))
        for i in chats:
            try:
                m = (
                    await app.forward_messages(i, y, x)
                    if message.reply_to_message
                    else await app.send_message(i, text=query)
                )
                if "-pin" in message.text:
                    try:
                        await m.pin(disable_notification=True)
                        pin += 1
                    except:
                        continue
                elif "-pinloud" in message.text:
                    try:
                        await m.pin(disable_notification=False)
                        pin += 1
                    except:
                        continue
                sent += 1
                await asyncio.sleep(0.2)
            except FloodWait as fw:
                flood_time = int(fw.value)
                if flood_time > 200:
                    continue
                await asyncio.sleep(flood_time)
            except:
                continue
        try:
            await message.reply_text(_["broad_3"].format(sent, pin))
        except:
            pass

    if "-user" in message.text:
        susr = 0
        served_users = []
        susers = await get_served_users()
        for user in susers:
            served_users.append(int(user["user_id"]))
        for i in served_users:
            try:
                m = (
                    await app.forward_messages(i, y, x)
                    if message.reply_to_message
                    else await app.send_message(i, text=query)
                )
                susr += 1
                await asyncio.sleep(0.2)
            except FloodWait as fw:
                flood_time = int(fw.value)
                if flood_time > 200:
                    continue
                await asyncio.sleep(flood_time)
            except:
                pass
        try:
            await message.reply_text(_["broad_4"].format(susr))
        except:
            pass

    if "-assistant" in message.text:
        aw = await message.reply_text(_["broad_5"])
        text = _["broad_6"]
        from Clonify.core.userbot import assistants

        for num in assistants:
            sent = 0
            client_ass = await get_client(num)
            async for dialog in client_ass.get_dialogs():
                try:
                    if message.reply_to_message:
                        await client_ass.forward_messages(dialog.chat.id, y, x)
                    else:
                        await client_ass.send_message(dialog.chat.id, text=query)
                    sent += 1
                    await asyncio.sleep(3)
                except FloodWait as fw:
                    flood_time = int(fw.value)
                    if flood_time > 200:
                        continue
                    await asyncio.sleep(flood_time)
                except:
                    continue
            text += _["broad_7"].format(num, sent)
        try:
            await aw.edit_text(text)
        except:
            pass
            
    IS_BROADCASTING = False


# ==========================================
#        CLONE BROADCAST COMMANDS
# ==========================================

@app.on_message(filters.command("stopcbroadcast") & SUDOERS)
async def stop_clone_broadcast(client, message):
    global IS_CBROADCASTING
    if not IS_CBROADCASTING:
        return await message.reply_text("❌ **No Clone Broadcast is currently running.**")
    
    IS_CBROADCASTING = False
    await message.reply_text("🛑 **Stopping Broadcast...**\nProcess will halt after current bot.")


@app.on_message(filters.command("cbroadcast") & SUDOERS)
async def clone_broadcast_handler(client, message):
    global IS_CBROADCASTING
    
    if IS_CBROADCASTING:
        return await message.reply_text("⚠️ **Broadcast already running!** Stop it first.")

    # --- COMMAND PARSING ---
    query = None
    if message.reply_to_message:
        query = message.reply_to_message.text or message.reply_to_message.caption
    else:
        if len(message.command) < 2:
            return await message.reply_text(
                "<b>📣 Clone Broadcast Manager</b>\n\n"
                "<b>Usage:</b> `/cbroadcast [Message] [Flags]`\n"
                "<b>Flags:</b> `-owner`, `-user`, `-group`, `-all`, `-pin`"
            )
        query = message.text.split(None, 1)[1]

    pin = "-pin" in message.text
    send_owners = "-owner" in message.text or "-all" in message.text
    send_users = "-user" in message.text or "-all" in message.text
    send_groups = "-group" in message.text or "-all" in message.text

    if not send_users and not send_groups and not send_owners:
        send_groups = True

    if query:
        for flag in ["-pin", "-owner", "-user", "-group", "-all"]:
            query = query.replace(flag, "")
        query = query.strip()

    if not query:
        return await message.reply_text("❌ **Message is empty! Clone broadcast supports text and captions only.**")

    IS_CBROADCASTING = True
    status_msg = await message.reply_text("🔄 **Analyzing Clones...**")

    # --- FETCH CLONES ---
    all_clones_data = []
    try:
        async for c in get_all_clones():
            all_clones_data.append(c)
    except Exception as e:
        IS_CBROADCASTING = False
        return await status_msg.edit_text(f"❌ **DB Error:** {e}")

    total_clones = len(all_clones_data)
    if total_clones == 0:
        IS_CBROADCASTING = False
        return await status_msg.edit_text("❌ **No Clones Found.**")

    await status_msg.edit_text(f"🚀 **Targeting {total_clones} Clones...**")

    success_clones = 0
    failed_clones = 0
    total_sent = 0

    # --- MAIN LOOP ---
    for clone in all_clones_data:
        if not IS_CBROADCASTING: break

        token = clone.get('token')
        bot_id = clone.get('bot_id')

        if not token or not bot_id:
            failed_clones += 1
            continue

        # --- A. COLLECT TARGETS ---
        target_ids = set()

        if send_owners:
            try:
                owner = await get_clonebot_owner(bot_id)
                if owner:
                    target_ids.add(int(owner))
            except:
                pass

        if send_users:
            try:
                users_list = await get_served_users_clone(bot_id)
                for u in users_list:
                    target_ids.add(int(u['user_id']))
            except:
                pass

        if send_groups:
            try:
                chats_list = await get_served_chats_clone(bot_id)
                for c in chats_list:
                    target_ids.add(int(c['chat_id']))
            except:
                pass

        if not target_ids:
            continue

        # --- B. SEND MESSAGES ---
        try:
            async with Client(
                f"clone_{bot_id}", # In-memory name
                api_id=API_ID,
                api_hash=API_HASH,
                bot_token=token,
                in_memory=True,
                no_updates=True
            ) as clone_app:
                
                clone_sent_count = 0
                try:
                    await clone_app.get_me()
                except (AuthKeyUnregistered, UserDeactivated):
                    failed_clones += 1
                    continue

                for chat_id in target_ids:
                    if not IS_CBROADCASTING: break
                    
                    try:
                        sent = await clone_app.send_message(chat_id, text=query)
                        
                        if pin and sent and str(chat_id).startswith("-100"):
                            try:
                                await sent.pin(disable_notification=True)
                            except:
                                pass
                        
                        clone_sent_count += 1
                        total_sent += 1
                        await asyncio.sleep(0.2)
                    
                    except FloodWait as e:
                        await asyncio.sleep(int(e.value))
                    except Exception:
                        continue
                
                if clone_sent_count > 0:
                    success_clones += 1
                
        except Exception:
            failed_clones += 1
            continue

    # --- FINAL REPORT ---
    IS_CBROADCASTING = False
    await status_msg.edit_text(
        f"✅ **Broadcast Completed!**\n\n"
        f"🤖 **Total Clones:** {total_clones}\n"
        f"📢 **Active Sending:** {success_clones}\n"
        f"⚠️ **Failed/Revoked:** {failed_clones}\n"
        f"📨 **Messages Sent:** {total_sent}"
    )


# ==========================================
#        AUTO CLEAN TASK
# ==========================================

async def auto_clean():
    while not await asyncio.sleep(10):
        try:
            served_chats = await get_active_chats()
            for chat_id in served_chats:
                if chat_id not in adminlist:
                    adminlist[chat_id] = []
                    async for user in app.get_chat_members(
                        chat_id, filter=ChatMembersFilter.ADMINISTRATORS
                    ):
                        if user.privileges.can_manage_video_chats:
                            adminlist[chat_id].append(user.user.id)
                    authusers = await get_authuser_names(chat_id)
                    for user in authusers:
                        user_id = await alpha_to_int(user)
                        adminlist[chat_id].append(user_id)
        except:
            continue

asyncio.create_task(auto_clean())
