# cogs/shop.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.db import get_random_characters, get_character, get_user, update_user_balance, add_character_to_user, get_user_characters

async def shop_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays the character shop."""
    await send_shop_message(update, context)

async def send_shop_message(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 0):
    """Sends the shop message with characters and navigation."""
    user_id = update.effective_user.id
    characters = await get_random_characters(3)  # For simplicity, we'll keep it random
    if not characters:
        await context.bot.send_message(update.effective_chat.id, "The shop is empty at the moment.")
        return

    char = characters[0]  # Display one character at a time
    buttons = [
        [InlineKeyboardButton(f"Buy {char['name']} - {char['price']} OwO Coins", callback_data=f"buy_{char['_id']}_{user_id}")],
        [
            InlineKeyboardButton("Previous", callback_data=f"shop_prev_{user_id}"),
            InlineKeyboardButton("Next", callback_data=f"shop_next_{user_id}")
        ]
    ]

    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
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

    parts = data.split("_")
    action = parts[0]

    if action in ["shop_next", "shop_prev"]:
        if user_id != int(parts[1]):
            await query.answer("This is not for you.", show_alert=True)
            return
        await send_shop_message(query, context)
        await query.message.delete()

    elif action == "buy":
        character_id = parts[1]
        if user_id != int(parts[2]):
            await query.answer("This is not for you.", show_alert=True)
            return

        user_characters = await get_user_characters(user_id)
        if character_id in user_characters:
            await query.answer("You already own this character.", show_alert=True)
            return

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
            await query.answer("❌ You don't have enough OwO Coins to buy this character.", show_alert=True)
