# main.py

import logging
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram import Update

load_dotenv()
from config import TELEGRAM_BOT_TOKEN, SESSION_TIMEOUT
from cogs.games import spin_command, bowl_command, dice_command, claim_command, balance_command, roll_command
from cogs.character_management import start_command, inventory_command, language_command, stop_command, redeem_command, end_session, mood_command, inventory_callback_handler, inline_inventory
from telegram.ext import InlineQueryHandler
from cogs.shop import shop_command, shop_callback_handler
from cogs.owner import add_artist, remove_artist, create_redeem_code, create_character_handler
from cogs.fun import reply_command, owo_command
from utils.pollinations_api import generate_response_with_history
from cogs.character_management import user_sessions
from utils.db import get_user

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles incoming text messages for character conversations."""
    user_id = update.effective_user.id
    if user_id in user_sessions:
        session = user_sessions[user_id]
        session["message_history"].append({"role": "user", "content": update.message.text})

        # Get the user's language preference
        user_language = "english" # Default language
        user = await get_user(user_id)
        if user and "language" in user:
            user_language = user["language"]

        # Add language-specific instructions to the prompt
        prompt_suffix = f" (respond in {user_language})"
        session["message_history"][-1]["content"] += prompt_suffix

        response = await generate_response_with_history(session["message_history"], model=session.get("model", "openai"))
        session["message_history"].append({"role": "assistant", "content": response})
        await update.message.reply_text(response)

        # Reset session timeout
        session["session_job"].schedule_removal()
        session["session_job"] = context.job_queue.run_once(
            end_session,
            SESSION_TIMEOUT,
            data={"user_id": user_id}
        )

def main() -> None:
    """Starts the bot."""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("spin", spin_command))
    application.add_handler(CommandHandler("bowl", bowl_command))
    application.add_handler(CommandHandler("dice", dice_command))
    application.add_handler(CommandHandler("roll", roll_command))
    application.add_handler(CommandHandler("inventory", inventory_command))
    application.add_handler(CommandHandler("language", language_command))
    application.add_handler(CommandHandler("shop", shop_command))
    application.add_handler(CommandHandler("redeem", redeem_command))
    application.add_handler(CommandHandler("stop", stop_command))
    application.add_handler(CommandHandler("mood", mood_command))
    application.add_handler(CommandHandler("add_artist", add_artist))
    application.add_handler(CommandHandler("remove_artist", remove_artist))
    application.add_handler(create_character_handler)
    application.add_handler(CommandHandler("create_redeem_code", create_redeem_code))
    application.add_handler(CommandHandler("reply", reply_command))
    application.add_handler(CommandHandler("owo", owo_command))
    application.add_handler(CommandHandler("claim", claim_command))
    application.add_handler(CommandHandler("balance", balance_command))

    # Register callback query handlers
    application.add_handler(CallbackQueryHandler(shop_callback_handler, pattern="^buy_|^shop_next_|^shop_prev_"))
    application.add_handler(CallbackQueryHandler(inventory_callback_handler, pattern="^inv_next_|^inv_prev_"))

    # Register message handler for character conversations
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Register inline query handler
    application.add_handler(InlineQueryHandler(inline_inventory))

    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()
