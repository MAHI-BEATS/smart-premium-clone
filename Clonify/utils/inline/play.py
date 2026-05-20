import math
import random

from pyrogram.enums import ButtonStyle
from config import SUPPORT_CHAT, OWNER_USERNAME
from pyrogram.types import InlineKeyboardButton
from Clonify import app
import config
from Clonify.utils.formatters import time_to_seconds

PREMIUM_EMOJIS = [
    "5422831825178206894", 
    "5368324170673489600",
    "5206607081334906820",
    "5206380668048496464"
]

# 🎨 Dynamic Color Generator
def get_style_map():
    styles = [ButtonStyle.PRIMARY, ButtonStyle.SUCCESS, ButtonStyle.DANGER]
    random.shuffle(styles)
    # ✅ KeyErrors protection with safe fallback mapping
    return {
        1: styles[0], 
        2: styles[1], 
        3: styles[2], 
        5: styles[0]
    }

def track_markup(_, videoid, user_id, channel, fplay):
    s_map = get_style_map()
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}", style=s_map.get(2)
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}", style=s_map.get(2)
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}", style=s_map.get(1)
            )
        ],
    ]
    return buttons


def stream_markup_timer(_, chat_id, played, dur):
    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur)
    percentage = (played_sec / duration_sec) * 100
    umm = math.floor(percentage)
    if 0 < umm <= 10:
        bar = "◉—————————"
    elif 10 < umm < 20:
        bar = "—◉————————"
    elif 20 <= umm < 30:
        bar = "——◉———————"
    elif 30 <= umm < 40:
        bar = "———◉——————"
    elif 40 <= umm < 50:
        bar = "————◉—————"
    elif 50 <= umm < 60:
        bar = "—————◉————"
    elif 60 <= umm < 70:
        bar = "——————◉———"
    elif 70 <= umm < 80:
        bar = "———————◉——"
    elif 80 <= umm < 95:
        bar = "————————◉—"
    else:
        bar = "—————————◉"

    s_map = get_style_map()
    buttons = [
        [
            InlineKeyboardButton(
                text=f"{played} {bar} {dur}",
                callback_data="GetTimer", style=s_map.get(1)
            )
        ],
        [
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}", style=s_map.get(2)),
            InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}", style=s_map.get(3)),
            InlineKeyboardButton(text="↻", callback_data=f"ADMIN Replay|{chat_id}", style=s_map.get(1)),
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}", style=s_map.get(2)),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}", style=s_map.get(3)),
        ],
        [
            InlineKeyboardButton(text="CLONE_NOW", url="https://t.me/clone_MUSICrobot", style=s_map.get(1))
        ],
        [
            InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close", style=s_map.get(3)),
        ]
    ]
    return buttons


def stream_markup(_, chat_id):
    s_map = get_style_map()
    buttons = [
        [
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}", style=s_map.get(2)),
            InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}", style=s_map.get(3)),
            InlineKeyboardButton(text="↻", callback_data=f"ADMIN Replay|{chat_id}", style=s_map.get(1)),
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}", style=s_map.get(2)),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}", style=s_map.get(3)),
         ],
        [
             InlineKeyboardButton(text="CLONE_NOW", url="https://t.me/clone_MUSICrobot", style=s_map.get(1))
         ],
        [
            InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close", style=s_map.get(3)),
        ]
    ]
    return buttons   


def playlist_markup(_, videoid, user_id, ptype, channel, fplay):
    s_map = get_style_map()
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"PROPlaylists {videoid}|{user_id}|{ptype}|a|{channel}|{fplay}", style=s_map.get(1)
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"PROPlaylists {videoid}|{user_id}|{ptype}|v|{channel}|{fplay}", style=s_map.get(2)
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}", style=s_map.get(3)
            ),
        ],
    ]
    return buttons


def livestream_markup(_, videoid, user_id, mode, channel, fplay):
    s_map = get_style_map()
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_3"],
                callback_data=f"LiveStream {videoid}|{user_id}|{mode}|{channel}|{fplay}", style=s_map.get(2)
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}", style=s_map.get(3)
            ),
        ],
    ]
    return buttons


def slider_markup(_, videoid, user_id, query, query_type, channel, fplay):
    query = f"{query[:20]}"
    s_map = get_style_map()
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}", style=s_map.get(1)
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}", style=s_map.get(2)
            ),
        ],
        [
            InlineKeyboardButton(
                text="◁",
                callback_data=f"slider B|{query_type}|{query}|{user_id}|{channel}|{fplay}", style=s_map.get(1)
            ),
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {query}|{user_id}", style=s_map.get(3)
            ),
            InlineKeyboardButton(
                text="▷",
                callback_data=f"slider F|{query_type}|{query}|{user_id}|{channel}|{fplay}", style=s_map.get(2)
            ),
        ],
    ]
    return buttons


def telegram_markup(_, chat_id):
    s_map = get_style_map()
    buttons = [
        [
            InlineKeyboardButton(
                text="Next",
                callback_data=f"PanelMarkup None|{chat_id}", style=s_map.get(1)
            ),
            InlineKeyboardButton(text=_["CLOSEMENU_BUTTON"], callback_data="close", style=s_map.get(3)),
        ],
    ]
    return buttons


def queue_markup(_, videoid, chat_id):
    s_map = get_style_map()

    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_3"],
                url=f"https://t.me/{app.username}?startgroup=true", style=s_map.get(1)
            ),
        ],
        [
            InlineKeyboardButton(
                text="II ᴘᴀᴜsᴇ",
                callback_data=f"ADMIN Pause|{chat_id}", style=s_map.get(3)
            ),
            InlineKeyboardButton(text="▢ sᴛᴏᴘ", callback_data=f"ADMIN Stop|{chat_id}", style=s_map.get(3)),
            InlineKeyboardButton(
                text="sᴋɪᴘ ‣‣I", callback_data=f"ADMIN Skip|{chat_id}", style=s_map.get(2)
            ),
        ],
        [
            InlineKeyboardButton(
                text="▷ ʀᴇsᴜᴍᴇ", callback_data=f"ADMIN Resume|{chat_id}", style=s_map.get(1)
            ),
            InlineKeyboardButton(
                text="ʀᴇᴘʟᴀʏ ↺", callback_data=f"ADMIN Replay|{chat_id}", style=s_map.get(2)
            ),
        ],
        [
            InlineKeyboardButton(
                text="ᴍᴏʀᴇ",
                callback_data=f"PanelMarkup None|{chat_id}", style=s_map.get(1)
            ),
        ],
    ]
    return buttons


def stream_markup2(_, chat_id):
    s_map = get_style_map()
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_3"],
                url=f"https://t.me/{app.username}?startgroup=true", style=s_map.get(1)
            ),
        ],
        [
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}", style=s_map.get(2)),
            InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}", style=s_map.get(3)),
            InlineKeyboardButton(text="↻", callback_data=f"ADMIN Replay|{chat_id}", style=s_map.get(1)),
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}", style=s_map.get(2)),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}", style=s_map.get(3)),
        ],
        [
            InlineKeyboardButton(
                text="CLONE_NOW", url="https://t.me/clone_MUSICrobot", style=s_map.get(1)
            ),
        ],
        [
            InlineKeyboardButton(text=_["CLOSEMENU_BUTTON"], callback_data="close", style=s_map.get(3)),
        ],
    ]
    return buttons


def stream_markup_timer2(_, chat_id, played, dur):
    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur)
    percentage = (played_sec / duration_sec) * 100
    umm = math.floor(percentage)
    if 0 < umm <= 40:
        bar = "◉——————————"
    elif 10 < umm < 20:
        bar = "—◉—————————"
    elif 20 < umm < 30:
        bar = "——◉————————"
    elif 30 <= umm < 40:
        bar = "———◉———————"
    elif 40 <= umm < 50:
        bar = "————◉——————"
    elif 50 <= umm < 60:
        bar = "——————◉————"
    elif 50 <= umm < 70:
        bar = "———————◉———"
    else:
        bar = "——————————◉"

    s_map = get_style_map()
    buttons = [
        [
            InlineKeyboardButton(
                text=f"{played} {bar} {dur}",
                callback_data="GetTimer", style=s_map.get(1)
            )
        ],
        [
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}", style=s_map.get(2)),
            InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}", style=s_map.get(3)),
            InlineKeyboardButton(text="↻", callback_data=f"ADMIN Replay|{chat_id}", style=s_map.get(1)),
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}", style=s_map.get(2)),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}", style=s_map.get(3)),
        ],
        [
            InlineKeyboardButton(text=_["CLOSEMENU_BUTTON"], callback_data="close", style=s_map.get(3)),
        ],
    ]
    return buttons


def panel_markup_1(_, videoid, chat_id):
    s_map = get_style_map()
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_3"],
                url=f"https://t.me/{app.username}?startgroup=true", style=s_map.get(1)
            ),
        ],
        [
            InlineKeyboardButton(
                text="sᴜғғʟᴇ",
                callback_data=f"ADMIN Shuffle|{chat_id}", style=s_map.get(2)
            ),
            InlineKeyboardButton(text="ʟᴏᴏᴘ ↺", callback_data=f"ADMIN Loop|{chat_id}", style=s_map.get(1)),
        ],
        [
            InlineKeyboardButton(
                text="◁ 10 sᴇᴄ",
                callback_data=f"ADMIN 1|{chat_id}", style=s_map.get(3)
            ),
            InlineKeyboardButton(
                text="10 sᴇᴄ ▷",
                callback_data=f"ADMIN 2|{chat_id}", style=s_map.get(2)
            ),
        ],
        [
            InlineKeyboardButton(
                text="ʜᴏᴍᴇ",
                callback_data=f"Pages Back|2|{videoid}|{chat_id}", style=s_map.get(1)
            ),
            InlineKeyboardButton(
                text="ɴᴇxᴛ",
                callback_data=f"Pages Forw|2|{videoid}|{chat_id}", style=s_map.get(2)
            ),
        ],
    ]
    return buttons


def panel_markup_2(_, videoid, chat_id):
    s_map = get_style_map()
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_3"],
                url=f"https://t.me/{app.username}?startgroup=true", style=s_map.get(1)
            ),
        ],
        [
            InlineKeyboardButton(
                text="🕒 0.5x",
                callback_data=f"SpeedUP {chat_id}|0.5", style=s_map.get(2)
            ),
            InlineKeyboardButton(
                text="🕓 0.75x",
                callback_data=f"SpeedUP {chat_id}|0.75", style=s_map.get(1)
            ),
            InlineKeyboardButton(
                text="🕤 1.0x",
                callback_data=f"SpeedUP {chat_id}|1.0", style=s_map.get(2)
            ),
        ],
        [
            InlineKeyboardButton(
                text="🕤 1.5x",
                callback_data=f"SpeedUP {chat_id}|1.5", style=s_map.get(1)
            ),
            InlineKeyboardButton(
                text="🕛 2.0x",
                callback_data=f"SpeedUP {chat_id}|2.0", style=s_map.get(3)
            ),
        ],
        [
            InlineKeyboardButton(
                text="ʙᴀᴄᴋ",
                callback_data=f"Pages Back|1|{videoid}|{chat_id}", style=s_map.get(1)
            ),
        ],
    ]
    return buttons


def panel_markup_5(_, videoid, chat_id):
    s_map = get_style_map()
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_3"],
                url=f"https://t.me/{app.username}?startgroup=true", style=s_map.get(1)
            ),
        ],
        [
            InlineKeyboardButton(text="ᴘᴀᴜsᴇ", callback_data=f"ADMIN Pause|{chat_id}", style=s_map.get(3)),
            InlineKeyboardButton(text="sᴛᴏᴘ", callback_data=f"ADMIN Stop|{chat_id}", style=s_map.get(3)),
            InlineKeyboardButton(text="sᴋɪᴘ", callback_data=f"ADMIN Skip|{chat_id}", style=s_map.get(2)),
        ],
        [
            InlineKeyboardButton(
                text="ʀᴇsᴜᴍᴇ", callback_data=f"ADMIN Resume|{chat_id}", style=s_map.get(2)
            ),
            InlineKeyboardButton(
                text="ʀᴇᴘʟᴀʏ", callback_data=f"ADMIN Replay|{chat_id}", style=s_map.get(1)
            ),
        ],
        [
            InlineKeyboardButton(
                text="ʜᴏᴍᴇ",
                callback_data=f"MainMarkup {videoid}|{chat_id}", style=s_map.get(1)
            ),
            InlineKeyboardButton(
                text="ɴᴇxᴛ",
                callback_data=f"Pages Forw|1|{videoid}|{chat_id}", style=s_map.get(2)
            ),
        ],
    ]
    return buttons


def panel_markup_3(_, videoid, chat_id):
    s_map = get_style_map()
    buttons = [
        [
            InlineKeyboardButton(
                text="🕒 0.5x",
                callback_data=f"SpeedUP {chat_id}|0.5", style=s_map.get(1)
            ),
            InlineKeyboardButton(
                text="🕓 0.75x",
                callback_data=f"SpeedUP {chat_id}|0.75", style=s_map.get(2)
            ),
            InlineKeyboardButton(
                text="🕤 1.0x",
                callback_data=f"SpeedUP {chat_id}|1.0", style=s_map.get(1)
            ),
        ],
        [
            InlineKeyboardButton(
                text="🕤 1.5x",
                callback_data=f"SpeedUP {chat_id}|1.5", style=s_map.get(2)
            ),
            InlineKeyboardButton(
                text="🕛 2.0x",
                callback_data=f"SpeedUP {chat_id}|2.0", style=s_map.get(3)
            ),
        ],
        [
            InlineKeyboardButton(
                text="ʙᴀᴄᴋ",
                callback_data=f"Pages Back|2|{videoid}|{chat_id}", style=s_map.get(1)
            ),
        ],
    ]
    return buttons

# Zeo
def panel_markup_4(_, vidid, chat_id, played, dur):
    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur)
    percentage = (played_sec / duration_sec) * 100
    umm = math.floor(percentage)
    if 0 < umm <= 40:
        bar = "◉——————————"
    elif 10 < umm < 20:
        bar = "—◉—————————"
    elif 20 < umm < 30:
        bar = "——◉————————"
    elif 30 <= umm < 40:
        bar = "———◉———————"
    elif 40 <= umm < 50:
        bar = "————◉——————"
    elif 50 <= umm < 60:
        bar = "——————◉————"
    elif 50 <= umm < 70:
        bar = "———————◉———"
    else:
        bar = "——————————◉"

    s_map = get_style_map()
    buttons = [
        [
            InlineKeyboardButton(
                text=f"{played} {bar} {dur}",
                callback_data="GetTimer", style=s_map.get(1)
            )
        ],
        [
            InlineKeyboardButton(
                text="II ᴘᴀᴜsᴇ",
                callback_data=f"ADMIN Pause|{chat_id}", style=s_map.get(3)
            ),
            InlineKeyboardButton(
                text="▢ sᴛᴏᴘ ▢", callback_data=f"ADMIN Stop|{chat_id}", style=s_map.get(3)
            ),
            InlineKeyboardButton(
                text="sᴋɪᴘ ‣‣I", callback_data=f"ADMIN Skip|{chat_id}", style=s_map.get(2)
            ),
        ],
        [
            InlineKeyboardButton(
                text="▷ ʀᴇsᴜᴍᴇ", callback_data=f"ADMIN Resume|{chat_id}", style=s_map.get(1)
            ),
            InlineKeyboardButton(
                text="ʀᴇᴘʟᴀʏ ↺", callback_data=f"ADMIN Replay|{chat_id}", style=s_map.get(2)
            ),
        ],
        [
            InlineKeyboardButton(
                text="ʜᴏᴍᴇ",
                callback_data=f"MainMarkup {vidid}|{chat_id}", style=s_map.get(1)
            ),
        ],
    ]
    return buttons


def panel_markup_clone(_, vidid, chat_id):
    s_map = get_style_map()
    buttons = [
        [
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}", style=s_map.get(2)),
            InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}", style=s_map.get(3)),
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}", style=s_map.get(1)),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}", style=s_map.get(3)),
        ],
        [InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close", style=s_map.get(3))],
    ]
    return buttons
