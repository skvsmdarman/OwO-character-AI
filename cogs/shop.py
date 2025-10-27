# cogs/shop.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.db import get_random_characters, get_character, get_user, update_user_balance, add_character_to_user

async def shop_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays the character shop."""
    await send_shop_message(update.message.chat_id, context)

async def send_shop_message(chat_id: int, context: ContextTypes.DEFAULT_TYPE, page: int = 0):
    """Sends the shop message with characters and navigation."""
    characters = await get_random_characters(3) # For simplicity, we'll keep it random
    if not characters:
        await context.bot.send_message(chat_id, "The shop is empty at the moment.")
        return

    char = characters[0] # Display one character at a time
    buttons = [
        [InlineKeyboardButton(f"Buy {char['name']} - {char['price']} OwO Coins", callback_data=f"buy_{char['_id']}")],
        [
            InlineKeyboardButton("Previous", callback_data="shop_prev"),
            InlineKeyboardButton("Next", callback_data="shop_next")
        ]
    ]

    await context.bot.send_photo(
        chat_id=chat_id,
        photo=char['avatar_url'],
        caption=f"Welcome to the shop!\n\n**{char['name']}**\n{char['title']}",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="Markdown"
    )

async def shop_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles button presses in the shop."""
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if data == "shop_next" or data == "shop_prev":
        await send_shop_message(query.message.chat_id, context)
        await query.message.delete()

    elif data.startswith("buy_"):
        character_id = data.split("_")[1]
        character = await get_character(character_id)
        if not character:
            await query.edit_message_text("❌ Character not found.")
            return

        user = await get_user(user_id)
        user_balance = user.get("balance", 0) if user else 0
        price = character.get("price", 0)

        if user_balance >= price:
            await update_user_balance(user_id, -price)
            await add_character_to_user(user_id, character_id)
            await query.edit_message_text(f"✅ You have successfully purchased {character['name']}!")
        else:
            await query.edit_message_text("❌ You don't have enough OwO Coins to buy this character.")
