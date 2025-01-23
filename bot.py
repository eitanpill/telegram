import os
import pandas as pd
import telebot
from flask import Flask
from threading import Thread
import schedule
import time

# טוען משתנים מסביבת העבודה
TOKEN = os.getenv("TELEGRAM_BOT_API_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")
CSV_FILE_PATH = os.getenv("CSV_FILE_PATH", "ads.csv")

# בדיקה אם כל המשתנים נטענו
if not TOKEN or not GROUP_ID or not CSV_FILE_PATH:
    raise ValueError("Missing required environment variables!")

print(f"✅ TOKEN נטען בהצלחה: {TOKEN[:10]}...")
print(f"✅ GROUP ID נטען בהצלחה: {GROUP_ID}")

# טוען את המודעות מתוך קובץ ה-CSV
try:
    ads = pd.read_csv(CSV_FILE_PATH)
    ads.columns = ads.columns.str.strip()  # מסיר רווחים משמות עמודות
    print(f"✅ נטענו {len(ads)} מודעות בהצלחה!")
except Exception as e:
    print(f"❌ שגיאה בטעינת קובץ ה-CSV: {e}")
    raise

# יצירת אובייקט של הבוט
bot = telebot.TeleBot(TOKEN)

# פונקציה לשליחת הודעות לקבוצה
def send_ad():
    for _, row in ads.iterrows():
        try:
            product_desc = row.get("Product Desc", "No Description Available")
            price = row.get("Discount Price", "Unknown Price")
            link = row.get("Product Url", "No URL Available")

            # בניית ההודעה
            message = f"📦 {product_desc}\n💰 {price}\n🔗 {link}"
            bot.send_message(GROUP_ID, message)
            print(f"✅ הודעה נשלחה: {product_desc}")
        except Exception as e:
            print(f"❌ שגיאה בשליחת הודעה: {e}")

# תזמון שליחה אוטומטית
def schedule_ads():
    schedule.every().hour.do(send_ad)  # דוגמה: שליחת מודעה כל שעה
    while True:
        schedule.run_pending()
        time.sleep(1)

# שרת Flask לשמירה על פעילות הבוט
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 8080)))

# הרצת הבוט
if __name__ == "__main__":
    print("✅ הבוט מוכן ומתחיל לפעול.")
    Thread(target=run_flask).start()  # הרצת Flask ברקע
    schedule_ads()  # הפעלת התזמון