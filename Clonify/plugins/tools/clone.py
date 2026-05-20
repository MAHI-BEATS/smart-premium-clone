import re
import logging
import asyncio
import importlib
import requests
from sys import argv
from datetime import datetime, timedelta

from pyrogram import idle, Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import (
    AccessTokenExpired,
    AccessTokenInvalid,
)
import pyrogram.errors

from Clonify import app
from config import API_ID, API_HASH, OWNER_ID, LOGGER_ID, CLONE_LOGGER, SUPPORT_CHAT
from Clonify.misc import SUDOERS
from Clonify.utils.database import get_assistant, clonebotdb
from Clonify.utils.database.clonedb import has_user_cloned_any_bot, get_owner_id_from_db
from Clonify.utils.decorators.language import language

CLONES = set()
ACTIVE_CLONES = {}

C_BOT_DESC = "Wᴀɴᴛ ᴀ ʙᴏᴛ ʟɪᴋᴇ ᴛʜɪs? Cʟᴏɴᴇ ɪᴛ ɴᴏᴡ! ✅\n\nVɪsɪᴛ: @clone_MUSICrobot ᴛᴏ ɢᴇᴛ sᴛᴀʀᴛᴇᴅ!\n\n - Uᴘᴅᴀᴛᴇ: @BETABOT_HUB\n - Oᴡɴᴇʀ: https://t.me/ll_DEVIL_SHIV_ll"

C_BOT_COMMANDS = [
    {"command": "/start", "description": "sᴛᴀʀᴛs ᴛʜᴇ ᴍᴜsɪᴄ ʙᴏᴛ"},
    {"command": "/help", "description": "ɢᴇᴛ ʜᴇʟᴩ ᴍᴇɴᴜ ᴡɪᴛʜ ᴇxᴩʟᴀɴᴀᴛɪᴏɴ ᴏғ ᴄᴏᴍᴍᴀɴᴅs."},
    {"command": "/play", "description": "sᴛᴀʀᴛs sᴛʀᴇᴀᴍɪɴɢ ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ ᴛʀᴀᴄᴋ ᴏɴ ᴠɪᴅᴇᴏᴄʜᴀᴛ."},
    {"command": "/pause", "description": "ᴩᴀᴜsᴇ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴩʟᴀʏɪɴɢ sᴛʀᴇᴀᴍ."},
    {"command": "/resume", "description": "ʀᴇsᴜᴍᴇ ᴛʜᴇ ᴩᴀᴜsᴇᴅ sᴛʀᴇᴀᴍ."},
    {"command": "/skip", "description": "ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴩʟᴀʏɪɴɢ sᴛʀᴇᴀᴍ ᴀɴᴅ sᴛᴀʀᴛ sᴛʀᴇᴀᴍɪɴɢ ᴛʜᴇ ɴᴇxᴛ ᴛʀᴀᴄᴋ ɪɴ ǫᴜᴇᴜᴇ."},
    {"command": "/end", "description": "ᴄʟᴇᴀʀs ᴛʜᴇ ǫᴜᴇᴜᴇ ᴀɴᴅ ᴇɴᴅ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴩʟᴀʏɪɴɢ sᴛʀᴇᴀᴍ."},
    {"command": "/ping", "description": "ᴛʜᴇ ᴩɪɴɢ ᴀɴᴅ sʏsᴛᴇᴍ sᴛᴀᴛs ᴏғ ᴛʜᴇ ʙᴏᴛ."},
    {"command": "/id", "description": "ɢᴇᴛ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ɢʀᴏᴜᴘ ɪᴅ. ɪғ ᴜsᴇᴅ ʙʏ ʀᴇᴘʟʏɪɴɢ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ, ɢᴇᴛs ᴛʜᴀᴛ ᴜsᴇʀ's ɪᴅ."}
]

# --- DELAYED START FUNCTION ---
async def delayed_start(bot_token, session_string, wait_time, botNumber):
    await asyncio.sleep(wait_time)
    logging.info(f"Attempting delayed start for clone {botNumber} after {wait_time}s...")
    try:
        ai = Client(
            bot_token,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=bot_token,
            plugins=dict(root="Clonify.cplugin"),
            in_memory=True
        )
        await ai.start()
        bot_info = await ai.get_me()
        if bot_info.id not in CLONES:
            CLONES.add(bot_info.id)
        ACTIVE_CLONES[bot_info.id] = ai
        logging.info(f"✅ Delayed start successful for Clone {botNumber}: @{bot_info.username}")
    except Exception as e:
        logging.error(f"❌ Delayed start failed for Clone {botNumber}: {e}")
# ------------------------------


@app.on_message(filters.command("clone"))
@language
async def clone_txt(client, message, _):
    userbot = await get_assistant(message.chat.id)

    userid = message.from_user.id
    has_already_cbot = await has_user_cloned_any_bot(userid)

    if has_already_cbot:
        if message.from_user.id != OWNER_ID:
            return await message.reply_text(_["C_B_H_0"])

    if len(message.command) > 1:
        bot_token = message.text.split("/clone", 1)[1].strip()
        mi = await message.reply_text(_["C_B_H_2"])
        try:
            ai = Client(
                bot_token,
                api_id=API_ID,
                api_hash=API_HASH,
                bot_token=bot_token,
                plugins=dict(root="Clonify.cplugin"), 
            )
            await ai.start()
            bot = await ai.get_me()
            bot_id = bot.id
            c_b_owner_fname = message.from_user.first_name
            c_bot_owner = message.from_user.id

        except (AccessTokenExpired, AccessTokenInvalid):
            await mi.edit_text(_["C_B_H_3"])
            return
        except Exception as e:
            if "database is locked" in str(e).lower():
                await message.reply_text(_["C_B_H_4"])
            else:
                await mi.edit_text(f"An error occurred: {str(e)}")
            return

        await mi.edit_text(_["C_B_H_5"])
        try:
            await app.send_message(
                CLONE_LOGGER, f"**#New_Cloned_Bot**\n\n**ʙᴏᴛ:- {bot.mention}**\n**ᴜsᴇʀɴᴀᴍᴇ:** @{bot.username}\n**ʙᴏᴛ ɪᴅ :** `{bot_id}`\n\n**ᴏᴡɴᴇʀ : ** [{c_b_owner_fname}](tg://user?id={c_bot_owner})"
            )
            await userbot.send_message(bot.username, "/start")

            details = {
                "bot_id": bot.id,
                "is_bot": True,
                "user_id": message.from_user.id,
                "name": bot.first_name,
                "token": bot_token,
                "username": bot.username,
                "channel": "BETABOT_HUB",
                "support": "BETABOT_SUPPORT",
                "Date": str(datetime.now().date()),
            }
            clonebotdb.insert_one(details)
            CLONES.add(bot.id)

            def set_bot_commands():
                url = f"https://api.telegram.org/bot{bot_token}/setMyCommands"
                params = {"commands": C_BOT_COMMANDS}
                requests.post(url, json=params)

            set_bot_commands()

            def set_bot_desc():
                url = f"https://api.telegram.org/bot{bot_token}/setMyDescription"
                params = {"description": C_BOT_DESC}
                response = requests.post(url, data=params)
                if response.status_code == 200:
                    logging.info(f"Successfully updated Description for bot: {bot_token}")
                else:
                    logging.error(f"Failed to update Description: {response.text}")

            set_bot_desc()

            await mi.edit_text(_["C_B_H_6"].format(bot.username))
        except BaseException as e:
            logging.exception("Error while cloning bot.")
            await mi.edit_text(
                f"⚠️ <b>ᴇʀʀᴏʀ:</b>\n\n<code>{e}</code>\n\n**ᴋɪɴᴅʟʏ ғᴏᴡᴀʀᴅ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴛᴏ @BETABOT_HUB ᴛᴏ ɢᴇᴛ ᴀssɪsᴛᴀɴᴄᴇ**"
            )
    else:
        await message.reply_text(_["C_B_H_1"])


@app.on_message(
    filters.command(
        [
            "delbot",
            "rmbot",
            "delcloned",
            "delclone",
            "deleteclone",
            "removeclone",
            "cancelclone",
        ]
    )
)
@language
async def delete_cloned_bot(client, message, _):
    try:
        if len(message.command) < 2:
            await message.reply_text(_["C_B_H_8"])
            return

        query_value = " ".join(message.command[1:])
        if query_value.startswith("@"):
            query_value = query_value[1:]
        
        status = await message.reply_text(_["C_B_H_9"])

        cloned_bot = await clonebotdb.find_one({"$or": [{"token": query_value}, {"username": query_value}]})
        
        if cloned_bot:
            owner_id = cloned_bot['user_id']
            try:
                owner_obj = await client.get_users(int(owner_id))
                owner_mention = owner_obj.mention
            except:
                owner_mention = f"[{owner_id}](tg://user?id={owner_id})"

            bot_info = (
                f"**#Remove_Clone_Bot**\n\n"
                f"**ʙᴏᴛ ɴᴀᴍᴇ:** {cloned_bot['name']}\n"
                f"**ʙᴏᴛ ɪᴅ:** `{cloned_bot['bot_id']}`\n"
                f"**ᴜsᴇʀɴᴀᴍᴇ:** @{cloned_bot['username']}\n"
                f"**ᴏᴡɴᴇʀ:** {owner_mention}"
            )

            C_OWNER = await get_owner_id_from_db(cloned_bot['bot_id'])
            OWNERS = [OWNER_ID, C_OWNER]

            if message.from_user.id not in OWNERS:
                return await status.edit_text(_["NOT_C_OWNER"].format(SUPPORT_CHAT))

            target_bot_id = cloned_bot["bot_id"]
            target_token = cloned_bot["token"]

            if target_bot_id in ACTIVE_CLONES:
                try:
                    await ACTIVE_CLONES[target_bot_id].stop()
                    del ACTIVE_CLONES[target_bot_id]
                    logging.info(f"Bot {target_bot_id} stopped from memory.")
                except Exception as e:
                    logging.error(f"Failed to stop bot {target_bot_id}: {e}")
            else:
                try:
                    temp_client = Client(
                        f"kill_{target_bot_id}", 
                        api_id=API_ID, 
                        api_hash=API_HASH, 
                        bot_token=target_token, 
                        in_memory=True, 
                        no_updates=True
                    )
                    await temp_client.start()
                    await temp_client.log_out() 
                    logging.info(f"Bot {target_bot_id} session killed remotely.")
                except Exception as e:
                    logging.error(f"Could not kill session for {target_bot_id}: {e}")

            await clonebotdb.delete_one({"_id": cloned_bot["_id"]})
            if cloned_bot["bot_id"] in CLONES:
                CLONES.remove(cloned_bot["bot_id"])

            await status.edit_text(_["C_B_H_10"])
            try:
                await app.send_message(CLONE_LOGGER, bot_info)
            except:
                pass
        else:
            await status.edit_text(_["C_B_H_11"])
    except Exception as e:
        await message.reply_text(_["C_B_H_12"])
        logging.exception(e)


async def restart_bots():
    global CLONES
    try:
        logging.info("Restarting all cloned bots........")
        
        bots = []
        async for bot in clonebotdb.find():
            bots.append(bot)
            
        botNumber = 1
        
        for bot_data in bots:
            bot_token = bot_data.get("token") 
            session_string = bot_data.get("session_string")

            if not bot_token:
                continue

            url = f"https://api.telegram.org/bot{bot_token}/getMe"
            try:
                response = requests.get(url)
                if response.status_code == 401:
                    logging.error(f"Removing Dead Clone (Invalid Token): {bot_token}")
                    await clonebotdb.delete_one({"token": bot_token})
                    continue
            except Exception:
                pass 

            try:
                ai = Client(
                    f"{bot_token}",
                    api_id=API_ID,
                    api_hash=API_HASH,
                    bot_token=bot_token,
                    plugins=dict(root="Clonify.cplugin"),
                    in_memory=True,
                )
                
                try:
                    await ai.start()
                except FloodWait as e:
                    wait_time = e.value + 6 
                    logging.warning(f"⚠️ FloodWait {wait_time}s on Clone {botNumber}. Moving to background task...")
                    asyncio.create_task(delayed_start(bot_token, session_string, wait_time, botNumber))
                    botNumber += 1
                    continue
                except Exception as e:
                    logging.error(f"Could not start clone {botNumber}: {e}")
                    continue

                bot_info = await ai.get_me()
                if bot_info.id not in CLONES:
                    CLONES.add(bot_info.id)
                
                ACTIVE_CLONES[bot_info.id] = ai
                
                if session_string:
                    try:
                        ass_client = Client(
                            f"Ass_{bot_token}",
                            api_id=API_ID,
                            api_hash=API_HASH,
                            session_string=session_string,
                            no_updates=True,
                            in_memory=True
                        )
                        try:
                            await ass_client.start()
                        except FloodWait:
                            pass
                        except Exception:
                            pass
                            
                        if ass_client.is_connected:
                            ai.assistant = ass_client 
                        logging.info(f"Assistant Auto-Started for Clone: {bot_info.first_name}")
                    except Exception as e:
                        logging.error(f"Failed to auto-start assistant for {bot_token}: {e}")

                print(f"Clone {botNumber} Started: @{bot_info.username}")
                
                if botNumber % 10 == 0:
                    await asyncio.sleep(5)
                else:
                    await asyncio.sleep(0.5)
                
                botNumber += 1

            except Exception as e:
                logging.exception(f"Error starting clone {bot_token}: {e}")

        try:
            await app.send_message(
                CLONE_LOGGER, f"**Process Completed!**\nActive bots started.\nFloodWait bots will auto-start in background."
            )
        except:
            pass
    except Exception as e:
        logging.exception("Error while restarting bots.")


@app.on_message(filters.command("delallclone") & filters.user(OWNER_ID))
@language
async def delete_all_cloned_bots(client, message, _):
    try:
        await message.reply_text(_["C_B_H_14"])
        
        count = 0
        for bot_id, bot_client in list(ACTIVE_CLONES.items()):
            try:
                await bot_client.stop()
                count += 1
            except:
                pass
        ACTIVE_CLONES.clear()

        await clonebotdb.delete_many({})
        CLONES.clear()
        await message.reply_text(f"{_['C_B_H_15']} (Stopped {count} active instances)")
    except Exception as e:
        await message.reply_text("An error occurred while deleting all cloned bots.")
        logging.exception(e)


@app.on_message(filters.command(["mybot", "mybots"], prefixes=["/", "."]))
@language
async def my_cloned_bots(client, message, _):
    try:
        user_id = message.from_user.id
        
        cloned_bots = []
        async for bot in clonebotdb.find({"user_id": user_id}):
            cloned_bots.append(bot)
        
        if not cloned_bots:
            await message.reply_text(_["C_B_H_16"])
            return
        
        total_clones = len(cloned_bots)
        text = f"**ʏᴏᴜʀ ᴄʟᴏɴᴇᴅ ʙᴏᴛs : {total_clones}**\n\n"
        
        for bot in cloned_bots:
            text += f"**ʙᴏᴛ ɴᴀᴍᴇ:** {bot['name']}\n"
            text += f"**ʙᴏᴛ ᴜsᴇʀɴᴀᴍᴇ:** @{bot['username']}\n\n"
        
        await message.reply_text(text)
    except Exception as e:
        logging.exception(e)
        await message.reply_text("An error occurred while fetching your cloned bots.")


@app.on_message(filters.command("cloned") & SUDOERS)
@language
async def list_cloned_bots(client, message, _):
    try:
        cloned_bots = []
        async for bot in clonebotdb.find():
            cloned_bots.append(bot)

        if not cloned_bots:
            await message.reply_text(_["C_B_H_13"])
            return

        total_clones = len(cloned_bots)
        text = f"**ᴛᴏᴛᴀʟ ᴄʟᴏɴᴇᴅ ʙᴏᴛs: `{total_clones}`**\n\n"

        chunk_size = 10
        chunks = [cloned_bots[i:i + chunk_size] for i in range(0, len(cloned_bots), chunk_size)]

        for chunk in chunks:
            chunk_text = text
            for bot in chunk:
                user_id = bot.get("user_id")
                bot_id = bot.get("bot_id", "Unknown")
                name = bot.get("name", "Unknown")
                username = bot.get("username", "Unknown")
                session = bot.get("session_string") 

                if session:
                    assistant_status = "✅ Connected"
                else:
                    assistant_status = "❌ None"
                
                created_on = bot.get("Date", "Unknown")
                if created_on is False:
                    created_on = "Unknown"

                if not user_id:
                    owner_name = "Data Missing"
                    owner_profile_link = "#"
                else:
                    try:
                        owner = await client.get_users(user_id)
                        owner_name = owner.first_name
                        owner_profile_link = f"tg://user?id={user_id}"
                    except pyrogram.errors.PeerIdInvalid:
                        owner_name = "Deleted User"
                        owner_profile_link = "#"
                    except Exception as e:
                        logging.error(f"Error fetching user {user_id}: {e}")
                        owner_name = "Unknown User"
                        owner_profile_link = "#"

                chunk_text += f"**ʙᴏᴛ ɪᴅ :** `{bot_id}`\n"
                chunk_text += f"**ʙᴏᴛ ɴᴀᴍᴇ :** {name}\n"
                chunk_text += f"**ʙᴏᴛ ᴜsᴇʀɴᴀᴍᴇ :** @{username}\n"
                chunk_text += f"**ᴏᴡɴᴇʀ :** [{owner_name}]({owner_profile_link})\n"
                chunk_text += f"**ᴀssɪsᴛᴀɴᴛ :** {assistant_status}\n"
                chunk_text += f"**ᴄʀᴇᴀᴛᴇᴅ ᴏɴ :** {created_on}\n\n"

            await message.reply_text(chunk_text)

    except Exception as e:
        logging.exception(e)
        await message.reply_text("An error occurred while listing cloned bots.")


@app.on_message(filters.command("totalbots") & SUDOERS)
@language
async def list_cloned_bots_total(client, message, _):
    try:
        cloned_bots = []
        async for bot in clonebotdb.find():
            cloned_bots.append(bot)

        if not cloned_bots:
            await message.reply_text("No bots have been cloned yet.")
            return

        total_clones = len(cloned_bots)
        text = f"**ᴛᴏᴛᴀʟ ᴄʟᴏɴᴇᴅ ʙᴏᴛs : `{total_clones}`**\n\n"        

        await message.reply_text(text)
    except Exception as e:
        logging.exception(e)
        await message.reply_text("An error occurred while listing cloned bots.")


@app.on_message(filters.command("active") & SUDOERS)
async def list_active_bots(client, message):
    try:
        days = int(message.command[1]) if len(message.command) > 1 else 30
        limit_date = datetime.now() - timedelta(days=days)

        text = f"**🟢 Active Bots (Used in last {days} days):**\n\n"
        count = 0
        
        async for bot in clonebotdb.find({"last_activity": {"$gte": limit_date}}):
            last_active = bot.get("last_activity")
            if last_active:
                last_active = last_active.strftime("%d-%m-%Y")
            else:
                last_active = "Just Created"
            
            text += f"**Bot:** @{bot['username']}\n**Last Active:** {last_active}\n\n"
            count += 1
            
        if count == 0:
            await message.reply_text(f"**❌ No active bots found in last {days} days.**")
        else:
            if len(text) > 4000:
                with open("active_bots.txt", "w", encoding="utf-8") as f:
                    f.write(text.replace("*", ""))
                await message.reply_document("active_bots.txt", caption=f"Total Active: {count}")
                import os
                os.remove("active_bots.txt")
            else:
                await message.reply_text(text)

    except Exception as e:
        await message.reply_text(f"Error: {e}")


@app.on_message(filters.command("botstats") & SUDOERS)
async def bot_statistics(client, message):
    try:
        msg = await message.reply_text("🔄 **Calculating Stats...**")
        
        limit_date = datetime.now() - timedelta(days=30)
        
        total = await clonebotdb.count_documents({})
        active = await clonebotdb.count_documents({"last_activity": {"$gte": limit_date}})
        inactive = await clonebotdb.count_documents({
            "$or": [
                {"last_activity": {"$lt": limit_date}},
                {"last_activity": {"$exists": False}}
            ]
        })
        
        text = (
            f"**📊 CLONE BOT STATISTICS**\n\n"
            f"**🤖 Total Bots:** `{total}`\n"
            f"**🟢 Active (Last 30 Days):** `{active}`\n"
            f"**🔴 Inactive (Dead):** `{inactive}`\n"
        )
        await msg.edit_text(text)
    except Exception as e:
        await message.reply_text(f"Error: {e}")


@app.on_message(filters.command("inactive") & SUDOERS)
async def list_inactive_bots(client, message):
    try:
        days = int(message.command[1]) if len(message.command) > 1 else 30
        limit_date = datetime.now() - timedelta(days=days)

        text = f"**⚠️ Inactive Bots (Not used in {days} days):**\n\n"
        count = 0
        
        async for bot in clonebotdb.find({
            "$or": [
                {"last_activity": {"$lt": limit_date}},
                {"last_activity": {"$exists": False}}
            ]
        }):
            last_active = bot.get("last_activity", "Never/Unknown")
            if last_active != "Never/Unknown":
                last_active = last_active.strftime("%d-%m-%Y")
            
            text += f"**Bot:** @{bot['username']}\n**Last Active:** {last_active}\n\n"
            count += 1
            
        if count == 0:
            await message.reply_text(f"**✅ No inactive bots found older than {days} days.**")
        else:
            if len(text) > 4000:
                with open("inactive_bots.txt", "w", encoding="utf-8") as f:
                    f.write(text.replace("*", ""))
                await message.reply_document("inactive_bots.txt", caption=f"Total Inactive: {count}")
                import os
                os.remove("inactive_bots.txt")
            else:
                await message.reply_text(text)

    except Exception as e:
        await message.reply_text(f"Error: {e}")


@app.on_message(filters.command("delinactive") & SUDOERS)
async def delete_inactive_bots(client, message):
    try:
        days = int(message.command[1]) if len(message.command) > 1 else 30
        limit_date = datetime.now() - timedelta(days=days)
        
        to_delete = await clonebotdb.count_documents({
            "$or": [
                {"last_activity": {"$lt": limit_date}},
                {"last_activity": {"$exists": False}}
            ]
        })
        
        if to_delete == 0:
            return await message.reply_text("No inactive bots to delete.")
            
        await message.reply_text(f"Deleting {to_delete} bots inactive for {days} days...")
        
        bots_to_delete = clonebotdb.find({
            "$or": [
                {"last_activity": {"$lt": limit_date}},
                {"last_activity": {"$exists": False}}
            ]
        })
        async for bot in bots_to_delete:
            bot_id = bot.get("bot_id")
            if bot_id in ACTIVE_CLONES:
                try:
                    await ACTIVE_CLONES[bot_id].stop()
                    del ACTIVE_CLONES[bot_id]
                except:
                    pass

        await clonebotdb.delete_many({
            "$or": [
                {"last_activity": {"$lt": limit_date}},
                {"last_activity": {"$exists": False}}
            ]
        })
        
        await message.reply_text(f"**✅ Successfully deleted {to_delete} inactive bots!**\n\nNote: Please restart the bot to clear memory cache.")
        
    except Exception as e:
        await message.reply_text(f"Error: {e}")
