from datetime import datetime, time as dtime
import os
import pandas as pd
import random
import telebot
import schedule
import time
from deep_translator import GoogleTranslator
from flask import Flask
from threading import Thread

# קריאת משתני סביבה
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_GROUP_ID = os.getenv("TELEGRAM_GROUP_ID")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("❌ TOKEN חסר! יש להגדיר את משתנה הסביבה TELEGRAM_BOT_TOKEN.")
if not TELEGRAM_GROUP_ID:
    raise ValueError("❌ GROUP ID חסר! יש להגדיר את משתנה הסביבה TELEGRAM_GROUP_ID.")

print("✅ TOKEN נטען בהצלחה:", TELEGRAM_BOT_TOKEN[:10], "...")
print("✅ GROUP ID נטען בהצלחה:", TELEGRAM_GROUP_ID)

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# קריאת הקובץ
ads_df = pd.read_csv("ads.csv")
print(f"✅ נטענו {len(ads_df)} מודעות בהצלחה!")

# פתיחים רנדומליים
HEADERS = [
    "💥 שובר שוק במחיר שלא יחזור!",
    "🔥 חייבים לראות את זה!",
    "🎯 מוצר מנצח במבצע בלעדי!",
    "🚀 הדיל שכולם מדברים עליו!",
    "✨ שווה בדיקה – הכי משתלם ברשת!",
    "😱 לא תאמינו למחיר הזה!",
    "🤑 פשוט לגנוב את זה!",
]

# בדיקת זמן לפי שעון ישראל
def is_israeli_daytime():
    now = datetime.utcnow()
    current_time = now.time()
    return dtime(5, 30) <= current_time <= dtime(19, 0)  # 08:30–22:00 בישראל

# בניית הודעה
def create_ad_message(ad):
    image_url = ad['Image Url']
    video_url = ad['Video Url']
    desc = GoogleTranslator(source='auto', target='iw').translate(ad['Product Desc'])

    origin_price = ad['Origin Price']
    discount_price = ad['Discount Price']
    discount = ad['Discount']
    sales = int(ad['Sales180Day'])
    rating = str(ad['Positive Feedback']).rstrip('%')
    product_url = ad['Promotion Url']

    header = random.choice(HEADERS)

    message = f"""{header}

{desc}

✔ {sales} מכירות! 📦
⭐ דירוג: {rating}% ⭐
💰 מחיר בלעדי: ₪{discount_price} (במקום ₪{origin_price}, הנחה של {discount}%)
🔗 לצפייה במוצר: {product_url}
"""
    return message.strip(), video_url if pd.notna(video_url) and video_url.endswith('.mp4') else image_url

# שליחת מודעה אקראית
def send_ad():
    global ads_df
    if "Sent" not in ads_df.columns:
        ads_df["Sent"] = False

    unsent_ads = ads_df[ads_df["Sent"] != True]
    if unsent_ads.empty:
        print("🔄 כל המודעות נשלחו. מתחילים סבב חדש.")
        ads_df["Sent"] = False
        unsent_ads = ads_df

    ad = unsent_ads.sample(1).iloc[0]  # בוחר אקראית
    message, media_url = create_ad_message(ad)

    try:
        if media_url.endswith(".mp4"):
            bot.send_video(chat_id=TELEGRAM_GROUP_ID, video=media_url, caption=message)
        else:
            bot.send_photo(chat_id=TELEGRAM_GROUP_ID, photo=media_url, caption=message)
        ads_df.loc[ads_df.index == ad.name, "Sent"] = True
        ads_df.to_csv("ads.csv", index=False)
        print("✅ מודעה נשלחה בהצלחה.")
    except Exception as e:
        print("❌ שגיאה בשליחת מודעה:", e)

# תזמון
def schedule_ads():
    print("⏰ מתזמן מודעות כל שעה וחצי בין 08:30 ל-22:00 לפי שעון ישראל.")
    schedule.every(90).minutes.do(lambda: send_ad() if is_israeli_daytime() else print("⏳ מחכים לשעות הפעילות..."))
    while True:
        schedule.run_pending()
        time.sleep(1)

# אפליקציית Flask ל-Render
app = Flask(__name__)

@app.route('/')
def home():
    return "הבוט באוויר! 🎈"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

# הרצת הכל
if __name__ == "__main__":
    send_ad()  # שליחה מיידית לבדיקה
    Thread(target=run_flask).start()
    Thread(target=schedule_ads).start()