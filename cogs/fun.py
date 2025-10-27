# cogs/fun.py

import random
from telegram import Update
from telegram.ext import ContextTypes
from utils.db import get_user_characters, get_character
from utils.pollinations_api import generate_text

async def reply_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Replies to a message with a random character from the user's inventory."""
    user_id = update.effective_user.id
    user_characters = await get_user_characters(user_id)

    if not user_characters:
        await update.message.reply_text("❌ You don't have any characters to reply with.")
        return

    if not update.message.reply_to_message or not update.message.reply_to_message.text:
        await update.message.reply_text("❌ Please reply to a message to use this command.")
        return

    character_id = random.choice(user_characters)
    character = await get_character(character_id)

    if not character:
        await update.message.reply_text("❌ Could not load character information.")
        return

    prompt = f"You are {character['name']}. {character.get('persona', '')}. Reply to the following message in a humorous way: '{update.message.reply_to_message.text}'"
    response = await generate_text(prompt)

    await update.message.reply_to_message.reply_text(f"**{character['name']} says:**\n{response}", parse_mode="Markdown")

async def owo_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Owo-ifies a message with a random character from the user's inventory."""
    user_id = update.effective_user.id
    user_characters = await get_user_characters(user_id)

    if not user_characters:
        await update.message.reply_text("❌ You don't have any characters to owo-ify with.")
        return

    if not context.args:
        await update.message.reply_text("❌ Please provide some text to owo-ify.")
        return

    character_id = random.choice(user_characters)
    character = await get_character(character_id)

    if not character:
        await update.message.reply_text("❌ Could not load character information.")
        return

    text_to_owo = " ".join(context.args)
    prompt = f"You are {character['name']}. {character.get('persona', '')}. Rephrase the following text in a witty and 'owo' style: '{text_to_owo}'"
    response = await generate_text(prompt)

    await update.message.reply_text(f"**{character['name']} says:**\n{response}", parse_mode="Markdown")
