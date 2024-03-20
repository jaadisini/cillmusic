import asyncio
import html
import re
from random import shuffle
from time import time

from pyrogram import filters, Client
from pyrogram.enums import ParseMode
from pyrogram.types import ChatPermissions, Message
from pyrogram.errors import FloodWait, UserNotParticipant

from Auput import app
from Auput.misc import SUDOERS, db


from Auput.utils.decorators.admins import list_admins


tagallgcid = []


@app.on_message(filters.command("all", "/") & filters.group)
#@AdminRightsCheck
async def on_tagall_handler_cmd(client, message: Message):
    if message.from_user.id not in (await list_admins(message.chat.id)):
        return
    if message.chat.id in tagallgcid:
        return await message.reply_text("sedang ada perintah: <code>all</code> yang digunakan")
    tagallgcid.append(message.chat.id)
    text = message.text.split(None, 1)[1] if len(message.text.split()) != 1 else ""
    m = message.reply_to_message or message
    users = []
    async for member in message.chat.get_members():
        if (member.user.is_bot or member.user.is_deleted):
            continue
        users.append(member.user.mention)
        if message.chat.id not in tagallgcid:
            break
        if len(users) < 5:
            continue
        await asyncio.sleep(1.5)
        await m.reply_text(
            ", ".join(users) + "\n\n" + text, quote=bool(message.reply_to_message)
        )
        users.clear()
    try:
        tagallgcid.remove(message.chat.id)
    except Exception:
        pass



@app.on_message(filters.command("cancel", "/") & filters.group)
#@AdminRightsCheck
async def on_stop_tag_handler(c: Client, m: Message):
    if m.from_user.id not in (await list_admins(m.chat.id)):
        return
    if m.chat.id not in tagallgcid:
        return await m.reply_text(
            "sedang tidak ada perintah: <code>all</code> yang digunakan"
        )
    try:
        tagallgcid.remove(m.chat.id)
    except Exception:
        pass
    await m.reply_text("ok tagall berhasil dibatalkan")
