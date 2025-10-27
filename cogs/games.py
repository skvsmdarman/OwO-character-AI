# cogs/games.py

import asyncio
import datetime
import random
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import DiceEmoji
from utils.db import get_user, update_user_balance, update_last_claim
from config import MIN_CLAIM_AMOUNT, MAX_CLAIM_AMOUNT

# In-memory storage for daily spin/game counts
daily_spin_data = {}
daily_bowl_data = {}
daily_dice_data = {}
MAX_PLAYS_PER_DAY = 3

async def spin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /spin command."""
    user_id = update.effective_user.id
    today = datetime.date.today()

    if user_id not in daily_spin_data or daily_spin_data[user_id]['last_spin_date'] != today:
        daily_spin_data[user_id] = {'last_spin_date': today, 'spin_count': 0}

    if daily_spin_data[user_id]['spin_count'] >= MAX_PLAYS_PER_DAY:
        await update.message.reply_text(f"❌ You've used your {MAX_PLAYS_PER_DAY} spins today. Come back tomorrow!")
        return

    daily_spin_data[user_id]['spin_count'] += 1

    spinner_msg = await context.bot.send_dice(chat_id=update.effective_chat.id, emoji="🎰")
    await asyncio.sleep(3)
    dice_value = spinner_msg.dice.value

    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=spinner_msg.message_id)

    if dice_value >= 60:
        win = 100
        outcome_str = "Jackpot! All 7s! (Triple match)"
    elif 40 <= dice_value < 60:
        win = 50
        outcome_str = "Two symbols match!"
    else:
        win = 20
        outcome_str = "No big match, but you still win!"

    await update_user_balance(user_id, win)
    user = await get_user(user_id)
    new_balance = user.get("balance", 0)

    result_text = (
        f"🎰 **Spin Result:**\n"
        f"⭐ Outcome: {outcome_str}\n"
        f"💰 You won **{win} OwO coins**!\n"
        f"🏆 Your total balance: **{new_balance} OwO coins**\n"
        f"🔄 Spins today: **{daily_spin_data[user_id]['spin_count']}/{MAX_PLAYS_PER_DAY}**"
    )
    await update.message.reply_text(result_text, parse_mode="Markdown")


async def claim_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Allows a user to claim their daily OwO Coins."""
    user_id = update.effective_user.id
    user = await get_user(user_id)
    today = datetime.date.today().isoformat()

    if user and user.get("last_claim_date") == today:
        await update.message.reply_text("❌ You have already claimed your daily OwO Coins. Come back tomorrow!")
        return

    claim_amount = random.randint(MIN_CLAIM_AMOUNT, MAX_CLAIM_AMOUNT)
    await update_user_balance(user_id, claim_amount)
    await update_last_claim(user_id)

    user = await get_user(user_id)
    new_balance = user.get("balance", 0)

    await update.message.reply_text(
        f"🎉 You have claimed **{claim_amount} OwO Coins**!\n"
        f"🏆 Your new balance is **{new_balance} OwO Coins**."
    )

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays the user's OwO Coin balance."""
    user_id = update.effective_user.id
    user = await get_user(user_id)
    balance = user.get("balance", 0) if user else 0
    await update.message.reply_text(f"💰 Your current balance is: {balance} OwO Coins")


async def bowl_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /bowl command."""
    user_id = update.effective_user.id
    today = datetime.date.today()

    if user_id not in daily_bowl_data or daily_bowl_data[user_id]['last_date'] != today:
        daily_bowl_data[user_id] = {'last_date': today, 'count': 0}

    if daily_bowl_data[user_id]['count'] >= MAX_PLAYS_PER_DAY:
        await update.message.reply_text("❌ You've already played 3 bowling games today. Come back tomorrow!")
        return

    daily_bowl_data[user_id]['count'] += 1

    bowl_msg = await context.bot.send_dice(chat_id=update.effective_chat.id, emoji=DiceEmoji.BOWLING)
    await asyncio.sleep(3)
    dice_value = bowl_msg.dice.value

    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=bowl_msg.message_id)

    if dice_value in [3, 4, 5, 6]:
        win = 500
        outcome_str = f"🎳 Great! You knocked down {dice_value} pins!"
    elif dice_value == 2:
        win = 250
        outcome_str = "🎳 You knocked down 2 pins!"
    else:
        win = 125
        outcome_str = "🎳 You knocked down 1 pin!"

    await update_user_balance(user_id, win)
    user = await get_user(user_id)
    new_balance = user.get("balance", 0)

    result_text = (
        f"{outcome_str}\n"
        f"💰 You won **{win} OwO coins**!\n"
        f"🏆 Your total balance: **{new_balance} OwO coins**\n"
        f"🔄 Bowling games today: **{daily_bowl_data[user_id]['count']}/{MAX_PLAYS_PER_DAY}**"
    )
    await update.message.reply_text(result_text, parse_mode="Markdown")


async def dice_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /dice command."""
    user_id = update.effective_user.id
    today = datetime.date.today()

    if user_id not in daily_dice_data or daily_dice_data[user_id]['last_date'] != today:
        daily_dice_data[user_id] = {'last_date': today, 'count': 0}

    if daily_dice_data[user_id]['count'] >= MAX_PLAYS_PER_DAY:
        await update.message.reply_text("❌ You've already played 3 dice games today. Come back tomorrow!")
        return

    daily_dice_data[user_id]['count'] += 1

    dice_msg = await context.bot.send_dice(chat_id=update.effective_chat.id, emoji=DiceEmoji.DICE)
    await asyncio.sleep(3)
    dice_value = dice_msg.dice.value

    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=dice_msg.message_id)

    wins = {6: 150, 5: 120, 4: 100, 3: 80, 2: 50, 1: 25}
    win = wins.get(dice_value, 20)
    outcome_str = f"🎲 You rolled a {dice_value}!"

    await update_user_balance(user_id, win)
    user = await get_user(user_id)
    new_balance = user.get("balance", 0)

    result_text = (
        f"{outcome_str}\n"
        f"💰 You won **{win} OwO coins**!\n"
        f"🏆 Your total balance: **{new_balance} OwO coins**\n"
        f"🔄 Dice games today: **{daily_dice_data[user_id]['count']}/{MAX_PLAYS_PER_DAY}**"
    )
    await update.message.reply_text(result_text, parse_mode="Markdown")
