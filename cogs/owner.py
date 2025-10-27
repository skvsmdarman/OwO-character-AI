# cogs/owner.py

import uuid
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from utils.db import get_user, users_collection, add_character, add_redeem_code
from utils.pixvid_api import upload_image
from config import OWNER_ID

# States for ConversationHandler
PHOTO, NAME, GREETING, PERSONA, RARITY, PRICE = range(6)

async def create_character_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the character creation process."""
    user = await get_user(update.effective_user.id)
    if not (user and user.get("is_artist")):
        await update.message.reply_text("❌ You are not authorized to create characters.")
        return ConversationHandler.END

    await update.message.reply_text("Let's create a new character. First, please send me the character's image.")
    return PHOTO

async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gets the character's photo and asks for the name."""
    if not update.message.photo:
        await update.message.reply_text("❌ Please send an image.")
        return PHOTO

    context.user_data['photo'] = update.message.photo[-1]
    await update.message.reply_text("Great! Now, what is the character's name?")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gets the character's name and asks for the greeting."""
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Got it. What is the character's greeting message?")
    return GREETING

async def get_greeting(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gets the character's greeting and asks for the persona."""
    context.user_data['greeting'] = update.message.text
    await update.message.reply_text("Perfect. Now, describe the character's persona.")
    return PERSONA

async def get_persona(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gets the character's persona and asks for the rarity."""
    context.user_data['persona'] = update.message.text
    await update.message.reply_text("Almost done. What is the character's rarity (e.g., common, rare, legendary)?")
    return RARITY

async def get_rarity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gets the character's rarity and asks for the price."""
    context.user_data['rarity'] = update.message.text
    await update.message.reply_text("Finally, what is the character's price in OwO Coins?")
    return PRICE

async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gets the character's price and creates the character."""
    try:
        price = int(update.message.text)
    except ValueError:
        await update.message.reply_text("❌ Invalid price. Please enter a number.")
        return PRICE

    photo_file = await context.user_data['photo'].get_file()
    photo_data = await photo_file.download_as_bytearray()

    response = await upload_image(bytes(photo_data), title=context.user_data['name'])
    if not response or "image" not in response:
        await update.message.reply_text("❌ Failed to upload character image.")
        return ConversationHandler.END

    character_id = str(uuid.uuid4())
    character_data = {
        "_id": character_id,
        "name": context.user_data['name'],
        "title": "", # Title is not asked in this flow, can be added
        "greeting": context.user_data['greeting'],
        "persona": context.user_data['persona'],
        "avatar_url": response["image"]["url"],
        "rarity": context.user_data['rarity'],
        "price": price,
    }
    await add_character(character_data)
    await update.message.reply_text(f"✅ Character '{context.user_data['name']}' created with ID: {character_id}")

    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the character creation process."""
    await update.message.reply_text("Character creation cancelled.")
    context.user_data.clear()
    return ConversationHandler.END

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

create_character_handler = ConversationHandler(
    entry_points=[CommandHandler("create_character", create_character_start)],
    states={
        PHOTO: [MessageHandler(filters.PHOTO, get_photo)],
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        GREETING: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_greeting)],
        PERSONA: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_persona)],
        RARITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_rarity)],
        PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_price)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
