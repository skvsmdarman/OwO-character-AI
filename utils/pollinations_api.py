# utils/pollinations_api.py

import aiohttp
from urllib.parse import quote
from config import POLLINATIONS_API_KEY

BASE_URL = "https://text.pollinations.ai"

async def generate_text(prompt: str, model: str = "openai", temperature: float = 0.7, max_tokens: int = 500):
    """Generates text using the Pollinations.AI API."""
    url = f"{BASE_URL}/{quote(prompt)}"
    params = {
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "apikey": POLLINATIONS_API_KEY
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                return await response.text()
            else:
                return "Sorry, I'm having trouble thinking right now."

async def generate_response_with_history(messages: list, model: str = "openai", temperature: float = 0.7, max_tokens: int = 500):
    """Generates a response based on a message history using the OpenAI compatible endpoint."""
    url = f"{BASE_URL}/openai"
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    headers = {
        "Authorization": f"Bearer {POLLINATIONS_API_KEY}",
        "Content-Type": "application/json"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data["choices"][0]["message"]["content"]
            else:
                return "Sorry, I'm having trouble thinking right now."

async def analyze_image(image_url: str, prompt: str, model: str = "openai"):
    """Analyzes an image using the Vision API."""
    url = f"{BASE_URL}/openai"
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }
        ],
        "max_tokens": 500
    }
    headers = {
        "Authorization": f"Bearer {POLLINATIONS_API_KEY}",
        "Content-Type": "application/json"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data["choices"][0]["message"]["content"]
            else:
                return "I'm sorry, I couldn't analyze the image."
