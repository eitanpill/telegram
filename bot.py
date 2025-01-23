import os
import pandas as pd
import telebot
import schedule
import time
from flask import Flask

# --- טעינת משתנים ---
TOKEN = os.getenv('BOT_TOKEN', '8130275609:ABCDEF...')
GROUP_ID = os.getenv('GROUP_ID', '-1002423906987')
CSV_FILE = 'ads.csv'

bot = telebot.TeleBot(TOKEN)

# --- בדיקת חיבור ---
print(f"✅ TOKEN נטען בהצלחה: {TOKEN[:10]}...")
print(f"✅ GROUP ID נטען בהצלחה: {GROUP_ID}")

# --- קריאת הקובץ ---
try:
    ads = pd.read_csv(CSV_FILE)
    print(f"✅ נטענו {len(ads)} מודעות בהצלחה!")
except Exception as e:
    print(f"❌ שגיאה בטעינת הקובץ: {e}")
    ads = pd.DataFrame()

# --- פונקציה ליצירת הודעת מודעה ---
def create_ad_message(row):
    image_url = row['Image Url']
    video_url = row['Video Url']
    product_desc = row['Product Desc']
    origin_price = row['Origin Price']
    discount_price = row['Discount Price']
    discount = row['Discount']
    sales = row['Sales180Day']
    positive_feedback = row['Positive Feedback']
    product_url = row['Product Url']

    message = f"""
📢 *מבצע חדש!*

📸 תמונה: {image_url}
🎥 וידאו: {video_url}

🛒 *{product_desc}*
💰 מחיר מקורי: {origin_price}
🔖 מחיר מבצע: {discount_price}
💸 הנחה: {discount}%
🔥 מכירות ב-180 ימים: {sales}
👍 פידבק חיובי: {positive_feedback}%

🔗 [לרכישה]({product_url})
"""
    return message

# --- שליחת הודעת מודעה ---
def send_ad():
    for _, row in ads.iterrows():
        try:
            message = create_ad_message(row)
            bot.send_message(GROUP_ID, message, parse_mode='Markdown')
            print(f"✅ נשלחה מודעה: {row['Product Desc']}")
            time.sleep(2)  # השהייה בין שליחת הודעות
        except Exception as e:
            print(f"❌ שגיאה בשליחת המודעה: {e}")

# --- הפעלת לו"ז ---
def schedule_ads():
    schedule.every().day.at("10:00").do(send_ad)
    print("✅ לוח זמנים להפצת מודעות הוגדר בהצלחה.")

# --- Flask ל-Render ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def keep_alive():
    app.run(host='0.0.0.0', port=8080)

# --- הפעלת הבוט ---
if __name__ == "__main__":
    keep_alive()
    schedule_ads()
    while True:
        schedule.run_pending()
        time.sleep(1)