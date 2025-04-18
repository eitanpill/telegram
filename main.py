import os
import random
import pandas as pd
import telebot
import schedule
import time
from flask import Flask
from threading import Thread
from deep_translator import GoogleTranslator

# קריאת טוקן וקבוצת טלגרם מהסביבה
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROUP_ID = os.getenv("TELEGRAM_GROUP_ID")

if not BOT_TOKEN:
    raise ValueError("❌ TOKEN חסר! יש להגדיר את משתנה הסביבה TELEGRAM_BOT_TOKEN.")
if not GROUP_ID:
    raise ValueError("❌ GROUP ID חסר! יש להגדיר את משתנה הסביבה TELEGRAM_GROUP_ID.")

print("✅ TOKEN נטען בהצלחה:", BOT_TOKEN[:10], "...")
print("✅ GROUP ID נטען בהצלחה:", GROUP_ID)

bot = telebot.TeleBot(BOT_TOKEN)
ads_file = "ads.csv"

# פתיחים אקראיים
openers = [
    "📢 מבצע מטורף! אל תפספסו!",
    "🔥 דיל שחייבים לראות!",
    "💥 שובר שוק במחיר שלא יחזור!",
    "⚡️ הכי משתלם שראינו החודש!",
]

def load_ads():
    try:
        df = pd.read_csv(ads_file)
        print(f"✅ נטענו {len(df)} מודעות בהצלחה!")
        return df
    except Exception as e:
        print("❌ שגיאה בטעינת המודעות:", e)
        return pd.DataFrame()

def save_ads(df):
    try:
        df.to_csv(ads_file, index=False)
        print("✅ המודעות נשמרו בהצלחה.")
    except Exception as e:
        print("❌ שגיאה בשמירת הקובץ:", e)

def translate_to_hebrew(text):
    try:
        return GoogleTranslator(source='auto', target='hebrew').translate(text)
    except Exception:
        return text

def create_ad_message(row):
    opener = random.choice(openers)
    desc_translated = translate_to_hebrew(str(row['Product Desc']))

    image_url = row['Video Url'] if pd.notna(row['Video Url']) else row['Image Url']
    sales = int(row['Sales180Day']) if pd.notna(row['Sales180Day']) else 0
    rating = f"{row['Positive Feedback']}%" if pd.notna(row['Positive Feedback']) else "לא ידוע"
    price = f"{row['Discount Price']} ₪" if pd.notna(row['Discount Price']) else "לא זמין"
    original_price = f"{row['Origin Price']} ₪" if pd.notna(row['Origin Price']) else ""
    discount = f"{row['Discount']}%" if pd.notna(row['Discount']) else ""

    product_url = row['Promotion Url']

    message = f"""{opener}

🎯 {desc_translated}

✔ {sales} מכירות! 📦
⭐ דירוג: {rating} ⭐
💰 מחיר בלעדי: {price}
🔗 [לצפייה במוצר]({product_url})
"""
    return image_url, message

def send_ad():
    df = load_ads()
    unsent = df[df['Sent'] != 'yes']
    if unsent.empty:
        print("🔁 כל המודעות נשלחו - מתחילים סבב חדש.")
        df['Sent'] = ''
        save_ads(df)
        return

    row = unsent.iloc[0]
    image_url, message = create_ad_message(row)

    try:
        if image_url.endswith(".mp4"):
            bot.send_video(GROUP_ID, image_url, caption=message, parse_mode='Markdown')
        else:
            bot.send_photo(GROUP_ID, image_url, caption=message, parse_mode='Markdown')
        print("✅ מודעה נשלחה בהצלחה.")
    except Exception as e:
        print("❌ שגיאה בשליחת מודעה:", e)
        return

    df.at[row.name, 'Sent'] = 'yes'
    save_ads(df)

def schedule_ads():
    schedule.every(30).minutes.do(send_ad)
    while True:
        schedule.run_pending()
        time.sleep(1)

# Flask app for uptime
app = Flask(__name__)
@app.route('/')
def index():
    return "Bot is running!"

if __name__ == '__main__':
    Thread(target=schedule_ads).start()
    app.run(host="0.0.0.0", port=8080)