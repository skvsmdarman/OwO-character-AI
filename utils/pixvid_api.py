# utils/pixvid_api.py

import aiohttp
from config import PIXVID_API_KEY

API_URL = "https://pixvid.org/api/1/upload"

async def upload_image(image_data: bytes, title: str = None, description: str = None):
    """Uploads an image to pixvid.org."""
    headers = {"X-API-Key": PIXVID_API_KEY}
    data = aiohttp.FormData()
    data.add_field("source", image_data, content_type="image/jpeg")
    if title:
        data.add_field("title", title)
    if description:
        data.add_field("description", description)

    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL, data=data, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                return None
