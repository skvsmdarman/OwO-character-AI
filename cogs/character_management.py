# cogs/character_management.py

import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.db import get_user, get_user_characters, get_character, set_user_language, get_redeem_code, mark_code_as_used, update_user_balance, add_character_to_user
from config import SESSION_TIMEOUT

user_sessions = {}

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /start command and character interactions."""
    user_id = update.effective_user.id
    args = context.args

    if args:
        character_id = args[0]
        mood = args[1] if len(args) > 1 else "normal"
        user_characters = await get_user_characters(user_id)

        if character_id in user_characters:
            character = await get_character(character_id)
            if character:
                await start_chat_session(update, context, user_id, character, mood)
            else:
                await update.message.reply_text("❌ Character not found.")
        else:
            await update.message.reply_text("❌ You don't own this character.")
    else:
        await update.message.reply_text("Welcome! Use /inventory to see your characters or /shop to get new ones.")

async def mood_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sets the mood for the chat session."""
    user_id = update.effective_user.id
    if user_id not in user_sessions:
        await update.message.reply_text("You need to be in a chat session to set the mood.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /mood [normal|intimate]")
        return

    mood = context.args[0].lower()
    if mood not in ["normal", "intimate"]:
        await update.message.reply_text("Invalid mood. Please choose from: normal, intimate")
        return

    models = {
        "normal": "openai",
        "intimate": "mistral"
    }
    user_sessions[user_id]["model"] = models.get(mood, "openai")
    await update.message.reply_text(f"Mood set to {mood}.")


async def start_chat_session(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, character: dict, mood: str = "normal"):
    """Initializes a chat session with a character."""
    session_job = context.job_queue.run_once(end_session, SESSION_TIMEOUT, data={"user_id": user_id})

    models = {
        "normal": "openai",
        "intimate": "mistral"
    }
    model = models.get(mood, "openai")

    user_sessions[user_id] = {
        "character_id": character["_id"],
        "message_history": [{"role": "system", "content": character["greeting"]}],
        "session_job": session_job,
        "model": model
    }
    await update.message.reply_text(
        f"💬 Chatting with {character['name']} (Mood: {mood})\n"
        f"Type /stop to end the session.\n"
        f"Session will timeout after {SESSION_TIMEOUT // 60} minutes of inactivity."
    )


async def inventory_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays the user's character inventory."""
    user_id = update.effective_user.id
    user_characters = await get_user_characters(user_id)

    if not user_characters:
        await update.message.reply_text("📦 Your inventory is empty. Use /shop to get characters!")
        return

    buttons = []
    for char_id in user_characters:
        character = await get_character(char_id)
        if character:
            buttons.append([InlineKeyboardButton(
                f"{character['name']} - {character['title']}",
                callback_data=f"view_{char_id}"
            )])

    await update.message.reply_text("📚 Your Inventory:", reply_markup=InlineKeyboardMarkup(buttons))


async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sets the user's preferred language."""
    user_id = update.effective_user.id
    args = context.args

    if args:
        language = args[0].lower()
        supported_languages = ["english", "persian", "hinglish"]
        if language in supported_languages:
            await set_user_language(user_id, language)
            await update.message.reply_text(f"Language set to {language.capitalize()}.")
        else:
            await update.message.reply_text("❌ Unsupported language. Please choose from: english, persian, hinglish.")
    else:
        await update.message.reply_text("Usage: /language [english|persian|hinglish]")


async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Stops the current chat session."""
    user_id = update.effective_user.id
    if user_id in user_sessions:
        user_sessions[user_id]["session_job"].schedule_removal()
        del user_sessions[user_id]
        await update.message.reply_text("❎ Ended session.")
    else:
        await update.message.reply_text("No active session to stop.")


async def end_session(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback to end a user's session after a period of inactivity."""
    user_id = context.job.data["user_id"]
    if user_id in user_sessions:
        del user_sessions[user_id]
        await context.bot.send_message(user_id, "⏱️ Session timed out due to inactivity.")

async def redeem_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Redeems a code for a reward."""
    user_id = update.effective_user.id
    if not context.args:
        await update.message.reply_text("Usage: /redeem <code>")
        return

    code = context.args[0]
    redeem_code = await get_redeem_code(code)

    if not redeem_code:
        await update.message.reply_text("❌ Invalid redeem code.")
        return

    if user_id in redeem_code.get("used_by", []):
        await update.message.reply_text("❌ You have already used this code.")
        return

    reward_type = redeem_code["reward_type"]
    reward_value = redeem_code["reward_value"]

    if reward_type == "coin":
        await update_user_balance(user_id, int(reward_value))
        await update.message.reply_text(f"✅ You have redeemed {reward_value} OwO Coins!")
    elif reward_type == "character":
        await add_character_to_user(user_id, reward_value)
        character = await get_character(reward_value)
        character_name = character['name'] if character else 'Unknown Character'
        await update.message.reply_text(f"✅ You have redeemed the character: {character_name}!")

    await mark_code_as_used(code, user_id)
