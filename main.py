
import os
import telebot
import pandas as pd
import schedule
import time
import random
import threading
from flask import Flask
from deep_translator import GoogleTranslator

# Load environment variables
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROUP_ID = os.getenv("TELEGRAM_GROUP_ID")

if not TOKEN:
    raise ValueError("❌ TOKEN חסר! יש להגדיר את משתנה הסביבה TELEGRAM_BOT_TOKEN.")
else:
    print("✅ TOKEN נטען בהצלחה:", TOKEN[:10], "...")

if not GROUP_ID:
    raise ValueError("❌ GROUP ID חסר! יש להגדיר את משתנה הסביבה TELEGRAM_GROUP_ID.")
else:
    print("✅ GROUP ID נטען בהצלחה:", GROUP_ID)

bot = telebot.TeleBot(TOKEN)

ADS_FILE = "ads.csv"
ads_df = pd.read_csv(ADS_FILE)
ads_df = ads_df.fillna("")

print(f"✅ נטענו {len(ads_df)} מודעות בהצלחה!")

# פתיחים מגניבים
openings = [
    "🔥 אל תפספסו את זה!",
    "💥 שובר שוק במחיר שלא יחזור!",
    "🚨 הנחה מטורפת שמחכה רק לכם!",
    "🎯 מציאה אמיתית שאתם חייבים לראות!",
    "🤑 מוצר לוהט במחיר בלעדי!",
    "🎁 עכשיו במחיר מיוחד לזמן מוגבל!",
]

def translate_to_hebrew(text):
    try:
        return GoogleTranslator(source='auto', target='hebrew').translate(text)
    except Exception as e:
        print("שגיאה בתרגום:", e)
        return text

def create_ad_message(row):
    try:
        desc = translate_to_hebrew(str(row["Product Desc"]).strip())
        original_price = str(row["Origin Price"]).replace("ILS", "").replace("₪", "").strip()
        discount_price = str(row["Discount Price"]).replace("ILS", "").replace("₪", "").strip()
        discount = str(row["Discount"]).replace("%", "").strip()
        sales = int(row["Sales180Day"])
        feedback = str(row["Positive Feedback"]).replace("%", "").strip()
        url = row["Promotion Url"]

        # פותח רנדומלי
        opening_line = random.choice(openings)

        # בניית ההודעה
        message = f"{opening_line}\n\n"
        message += f"{desc}\n\n"
        message += f"✔ {sales} מכירות! 📦\n"
        message += f"⭐ דירוג: {feedback}% ⭐\n"
        message += f"🎯 הנחה של {discount}%\n"
        message += f"💰 מחיר בלעדי: ₪ {discount_price}\n"
        message += f"🔗 לצפייה במוצר\n{url}"

        return message
    except Exception as e:
        print("שגיאה ביצירת מודעה:", e)
        return None

def send_ad():
    global ads_df
    for index, row in ads_df.iterrows():
        if row["Sent"] != "Yes":
            message = create_ad_message(row)
            if message:
                image_url = row["Image Url"]
                video_url = row["Video Url"]
                try:
                    if video_url and video_url.startswith("http"):
                        bot.send_video(GROUP_ID, video_url, caption=message)
                    elif image_url and image_url.startswith("http"):
                        bot.send_photo(GROUP_ID, image_url, caption=message)
                    else:
                        bot.send_message(GROUP_ID, message)
                    ads_df.at[index, "Sent"] = "Yes"
                    ads_df.to_csv(ADS_FILE, index=False)
                    print(f"✅ מודעה מספר {index+1} נשלחה")
                except Exception as e:
                    print(f"שגיאה בשליחת מודעה מספר {index+1}:", e)
            break
    else:
        # כל המודעות נשלחו – אפס את העמודה
        print("🔄 כל המודעות נשלחו. מתחילים סבב חדש.")
        ads_df["Sent"] = ""
        ads_df.to_csv(ADS_FILE, index=False)

# תזמון יומי
def schedule_ads():
    schedule.every().day.at("11:00").do(send_ad)
    while True:
        schedule.run_pending()
        time.sleep(1)

# שרת Flask לשמירה על פעילות הבוט
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

# הרצת הבוט + Flask במקביל
if __name__ == "__main__":
    print("✅ הבוט מוכן ומתחיל לפעול.")
    threading.Thread(target=schedule_ads).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
