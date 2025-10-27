# cogs/owner.py

import uuid
from telegram import Update
from telegram.ext import ContextTypes
from utils.db import get_user, users_collection, add_character, add_redeem_code
from utils.pixvid_api import upload_image
from config import OWNER_ID

async def add_artist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Adds a user to the artist role."""
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Unauthorized.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /add_artist <user_id>")
        return

    try:
        user_id = int(context.args[0])
        await users_collection.update_one({"_id": user_id}, {"$set": {"is_artist": True}}, upsert=True)
        await update.message.reply_text(f"✅ User {user_id} has been granted artist permissions.")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID.")

async def remove_artist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Removes a user from the artist role."""
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Unauthorized.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /remove_artist <user_id>")
        return

    try:
        user_id = int(context.args[0])
        await users_collection.update_one({"_id": user_id}, {"$set": {"is_artist": False}})
        await update.message.reply_text(f"✅ User {user_id} has had their artist permissions revoked.")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID.")


async def create_character(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Creates a new character."""
    user = await get_user(update.effective_user.id)
    if not (user and user.get("is_artist")):
        await update.message.reply_text("❌ You are not authorized to create characters.")
        return

    if not update.message.caption or not update.message.photo:
        await update.message.reply_text("Usage: Please send an image with a caption in the format:\n/create_character <name>; <title>; <greeting>; <rarity>; <price>")
        return

    try:
        args = update.message.caption.split('; ')
        name, title, greeting, rarity, price_str = args
        price = int(price_str)
    except (ValueError, IndexError):
        await update.message.reply_text("Usage: Please send an image with a caption in the format:\n/create_character <name>; <title>; <greeting>; <rarity>; <price>")
        return

    if not update.message.photo:
        await update.message.reply_text("❌ Please attach an image for the character.")
        return

    photo = await update.message.photo[-1].get_file()
    photo_data = await photo.download_as_bytearray()

    response = await upload_image(bytes(photo_data), title=name)
    if not response or "image" not in response:
        await update.message.reply_text("❌ Failed to upload character image.")
        return

    character_id = str(uuid.uuid4())
    character_data = {
        "_id": character_id,
        "name": name,
        "title": title,
        "greeting": greeting,
        "avatar_url": response["image"]["url"],
        "rarity": "common",  # Default rarity
        "price": 100,      # Default price
    }
    await add_character(character_data)
    await update.message.reply_text(f"✅ Character '{name}' created with ID: {character_id}")


async def create_redeem_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Creates a redeem code for coins or characters."""
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Unauthorized.")
        return

    if len(context.args) != 3:
        await update.message.reply_text("Usage: /create_redeem_code <reward_type: coin|character> <reward_value> <amount>")
        return

    reward_type, reward_value, amount_str = context.args
    try:
        amount = int(amount_str)
    except ValueError:
        await update.message.reply_text("❌ Invalid amount.")
        return

    codes = []
    for _ in range(amount):
        code = str(uuid.uuid4())
        await add_redeem_code(code, reward_type, reward_value)
        codes.append(code)

    await update.message.reply_text(f"✅ Generated {amount} redeem codes:\n" + "\n".join(codes))
