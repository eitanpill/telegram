import csv
import random
import time
import telebot
from datetime import datetime
import logging
import os

# Token and Group ID
TELEGRAM_TOKEN = '8144674866:AAE8olkDboxTdVWWFeg-a5wU9r10k1gSEmE'
GROUP_ID = -1002423906987  # Group ID of the target group
CSV_FILE_PATH = '/Users/eitanpelles/Desktop/telegram-bot/ads.csv'

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Set up logging
logging.basicConfig(level=logging.INFO)

# Load the products from CSV
def load_products():
    products = []
    try:
        with open(CSV_FILE_PATH, 'r', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                products.append(row)
        logging.info(f"Loaded {len(products)} products from CSV.")
        return products
    except Exception as e:
        logging.error(f"Error loading products: {e}")
        return []

# Format the message
def format_message(product):
    """
    Format the message with image, details, and link to product.
    """
    message = (
        f"🌟 {product['Product Desc']} 🌟\n\n"
        f"💰 מחיר מקורי: {product['Origin Price']} ₪\n"
        f"💥 מחיר מבצע: {product['Discount Price']} ₪\n"
        f"✨ הנחה: {product['Discount']}%\n"
        f"👍 פידבק חיובי: {product['Positive Feedback']}%\n\n"
        f"🛒 לרכישת המוצר לחצו כאן: {product['Product Url']}\n"
    )
    
    # If there is an image URL, send the image first
    image_url = product.get('Image Url', None)
    if image_url:
        return image_url, message
    
    return None, message

# Send a product message with image (if available)
def send_product(products):
    """
    Sends a random product to the group, with an image and product details.
    """
    product = random.choice(products)
    image_url, message = format_message(product)
    
    try:
        if image_url:
            bot.send_photo(GROUP_ID, image_url, caption=message)
        else:
            bot.send_message(GROUP_ID, message)
        
        logging.info(f"Sent message: {message}")
    except Exception as e:
        logging.error(f"Error sending message: {e}")

# Function to get the current time and check if it's time to send a message
def schedule_messages(products):
    """
    Send a message every hour at an exact time from 8 AM to 11 PM.
    """
    current_time = datetime.now()
    current_hour = current_time.hour
    current_minute = current_time.minute

    # Check if it's exactly on the hour
    if current_minute == 0 and 8 <= current_hour <= 23:
        send_product(products)
    
    # Sleep until the next hour (but no need to send immediately)
    time.sleep(60)  # Check every minute

# Main function to start the bot
def main():
    products = load_products()
    if not products:
        logging.error("No products loaded. Exiting...")
        return
    
    # Run the schedule in a loop
    while True:
        schedule_messages(products)

if __name__ == "__main__":
    main()