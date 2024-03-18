import re
from datetime import datetime, timedelta

from pyrogram import filters
from pyrogram.types import ChatPermissions

from Auput import app
from Auput.misc import SUDOERS
from Auput.utils.decorators.errors import capture_err
from Auput.utils.decorators.permissions import adminsOnly
from Auput.utils.decorators.admins import list_admins
from Auput.utils.database.mongodatabase import (
    delete_blacklist_filter,
    get_blacklisted_words,
    save_blacklist_filter,
)
from Auput.utils.filter_group import blacklist_filters_group

def get_arg(message: Message):
    msg = message.text
    msg = msg.replace(" ", "", 1) if msg[1] == " " else msg
    split = msg[1:].replace("\n", " \n").split(" ")
    if " ".join(split[1:]).strip() == "":
        return ""
    return " ".join(split[1:])

@app.on_message(filters.command("bl") & ~filters.private)
@adminsOnly("can_restrict_members")
async def save_filters(_, message):
trigger = get_arg(message)
    if message.reply_to_message:
        trigger = message.reply_to_message.text or message.reply_to_message.caption
    
    if not trigger:
        return await message.reply_text(
            "balas atau masukan pesan"
        )
    chat_id = message.chat.id
    await save_blacklist_filter(chat_id, word)
    await message.reply_text(f"__**Blacklisted {word}.**__")


@app.on_message(filters.command("listbl") & ~filters.private)
@capture_err
async def get_filterss(_, message):
    data = await get_blacklisted_words(message.chat.id)
    if not data:
        await message.reply_text("**No blacklisted words in this chat.**")
    else:
        msg = f"List of blacklisted words in {message.chat.title} :\n"
        for word in data:
            msg += f"**-** `{word}`\n"
        await message.reply_text(msg)


@app.on_message(filters.command("delbl") & ~filters.private)
@adminsOnly("can_restrict_members")
async def del_filter(_, message):
    if len(message.command) < 2:
        return await message.reply_text("Gunakan:\n/delbl balas atau masukan pesan]")
    word = message.text.split(None, 1)[1].strip()
    if not word:
        return await message.reply_text("Gunakan:\n/delbl balas atau masukan pesan")
    chat_id = message.chat.id
    deleted = await delete_blacklist_filter(chat_id, word)
    if deleted:
        return await message.reply_text(f"**Whitelisted {word}.**")
    await message.reply_text("**No such blacklist filter.**")


@app.on_message(filters.text & ~filters.private, group=blacklist_filters_group)
@capture_err
async def blacklist_filters_re(_, message):
    text = message.text.lower().strip()
    if not text:
        return
    chat_id = message.chat.id
    user = message.from_user
    if not user:
        return
    if user.id in SUDOERS:
        return
    list_of_filters = await get_blacklisted_words(chat_id)
    for word in list_of_filters:
        pattern = r"( |^|[^\w])" + re.escape(word) + r"( |$|[^\w])"
        if re.search(pattern, text, flags=re.IGNORECASE):
            if user.id in await list_admins(chat_id):
                return
            try:
                await message.delete()
                await message.chat.restrict_member(
                    user.id,
                    ChatPermissions(),
                    until_date=datetime.now() + timedelta(minutes=60),
                )
            except Exception:
                return
            return await app.send_message(
                chat_id,
                f"Muted {user.mention} [`{user.id}`] for 1 hour "
                + f"due to a blacklist match on {word}.",
            )
