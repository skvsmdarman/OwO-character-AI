# utils/db.py

import motor.motor_asyncio
from config import MONGO_URI, DB_NAME

# Establish a connection to the MongoDB server
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

# Define collections
users_collection = db["users"]
characters_collection = db["characters"]
redeem_codes_collection = db["redeem_codes"]

# --- User Management ---

async def get_user(user_id):
    """Fetches a user from the database."""
    return await users_collection.find_one({"_id": user_id})

async def update_user_balance(user_id, amount):
    """Updates a user's balance."""
    await users_collection.update_one(
        {"_id": user_id},
        {"$inc": {"balance": amount}},
        upsert=True
    )

async def add_character_to_user(user_id, character_id):
    """Adds a character to a user's collection."""
    await users_collection.update_one(
        {"_id": user_id},
        {"$addToSet": {"characters": character_id}},
        upsert=True
    )

async def get_user_characters(user_id):
    """Fetches a user's character collection."""
    user = await get_user(user_id)
    return user.get("characters", []) if user else []

async def set_user_language(user_id, language):
    """Sets the user's preferred language."""
    await users_collection.update_one(
        {"_id": user_id},
        {"$set": {"language": language}},
        upsert=True
    )

# --- Character Management ---

async def add_character(character_data):
    """Adds a new character to the database."""
    await characters_collection.insert_one(character_data)

async def get_character(character_id):
    """Fetches a character from the database."""
    return await characters_collection.find_one({"_id": character_id})

async def get_random_characters(count=3):
    """Fetches a specified number of random characters."""
    pipeline = [{"$sample": {"size": count}}]
    return await characters_collection.aggregate(pipeline).to_list(length=count)

# --- Redeem Code Management ---

async def add_redeem_code(code, reward_type, reward_value):
    """Adds a new redeem code to the database."""
    await redeem_codes_collection.insert_one({
        "_id": code,
        "reward_type": reward_type,
        "reward_value": reward_value,
        "used_by": []
    })

async def get_redeem_code(code):
    """Fetches a redeem code from the database."""
    return await redeem_codes_collection.find_one({"_id": code})

async def mark_code_as_used(code, user_id):
    """Marks a redeem code as used by a specific user."""
    await redeem_codes_collection.update_one(
        {"_id": code},
        {"$addToSet": {"used_by": user_id}}
    )
