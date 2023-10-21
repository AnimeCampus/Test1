from pyrogram import Client, filters
from pyrogram.types import Message
import requests
from bs4 import BeautifulSoup
import logging


# Replace with your actual API ID, API hash, and bot token
api_id = "28640015"
api_hash = "e8f539f9fcca3eb5284edababf5062fe"
bot_token = "6062250856:AAEI_suUfM-_MKhJT5cODnWgYJbkH3To9o4"
chat_id = "-1002058050288"  # Replace with the chat ID where you want to send logs and errors

# Create the Pyrogram client
app = Client(
    "pinterest_bot",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    filename='bot.log',  # Log file name
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Function to send log messages to the specified chat
async def send_log_to_chat(text):
    try:
        await app.send_message(chat_id, text)
    except Exception as e:
        logger.error(f"Failed to send log to chat: {str(e)}")

@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    # This command sends a welcome message when the user types /start
    await message.reply("Welcome to the Pinterest Image Download Bot! Use /help to learn how to use this bot.")

@app.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    # This command sends instructions on how to use the bot when the user types /help
    help_text = "This bot allows you to download Pinterest images. To use it, simply type /download followed by your search query."
    await message.reply(help_text)

@app.on_message(filters.command("download"))
async def download_pinterest_images(client: Client, message: Message):
    try:
        # Get the user's query from the message text after the /download command
        query = " ".join(message.text.split()[1:])

        if not query:
            await message.reply("Please provide a search query after /download.")
            return

        # Search Pinterest for the user's query
        search_url = f"https://www.pinterest.com/search/pins/?q={query}"
        response = requests.get(search_url)

        if response.status_code == 200:
            # Parse the HTML content of the search results
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find up to 5 image elements in the search results
            img_elements = soup.find_all("img")

            if img_elements:
                # Send up to 5 images
                for i, img_element in enumerate(img_elements[:5]):
                    image_url = img_element.get("src")

                    # Download the image
                    img_response = requests.get(image_url)

                    if img_response.status_code == 200:
                        with open(f"downloaded_image_{i + 1}.jpg", "wb") as file:
                            file.write(img_response.content)

                        # Send the downloaded image
                        await client.send_photo(
                            chat_id=message.chat.id,
                            photo=f"downloaded_image_{i + 1}.jpg",
                            caption=f"Image {i + 1} for query: {query}"
                        )

                await message.reply("Images downloaded and sent successfully.")
            else:
                await message.reply(f"No images found for query: {query}.")
        else:
            await message.reply("Failed to access Pinterest search results.")
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        logger.error(error_message)
        await message.reply(error_message)
        await send_log_to_chat(error_message)

print("Bot started")

if __name__ == "__main__":
    app.start()
    app.idle()
