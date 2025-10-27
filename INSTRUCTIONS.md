# Environment Variable Setup

This document explains how to set up the necessary environment variables for both local development and deployment on Heroku.

## Local Development

For local development, you will need to create a `.env` file in the root directory of the project. This file will store your secret keys and other configuration variables.

1.  **Create the `.env` file:**

    ```bash
    touch .env
    ```

2.  **Add the following variables to the `.env` file:**

    ```
    TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
    MONGO_URI="your_mongodb_uri"
    POLLINATIONS_API_KEY="your_pollinations_api_key"
    PIXVID_API_KEY="your_pixvid_api_key"
    OWNER_ID="your_owner_id"
    ```

    Replace the placeholder values with your actual credentials.

## Heroku Deployment

When deploying to Heroku, you will not use a `.env` file. Instead, you will set the environment variables in the Heroku dashboard.

1.  **Go to your Heroku app's dashboard.**
2.  **Navigate to the "Settings" tab.**
3.  **Click on "Reveal Config Vars".**
4.  **Add the following key-value pairs:**

    *   `TELEGRAM_BOT_TOKEN`: `your_telegram_bot_token`
    *   `MONGO_URI`: `your_mongodb_uri`
    *   `POLLINATIONS_API_KEY`: `your_pollinations_api_key`
    *   `PIXVID_API_KEY`: `your_pixvid_api_key`
    *   `OWNER_ID`: `your_owner_id`

    Again, replace the placeholder values with your actual credentials.
