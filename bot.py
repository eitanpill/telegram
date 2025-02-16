import os
import time
import random
import pandas as pd
import pytz
from datetime import datetime, time as dt_time
from telebot import TeleBot

# ✅ הדפסת מצב התחלתי ללוג
print("✅ הבוט התחיל לפעול... בודק חיבורים!")

# 🔑 משתני סביבה
TOKEN = os.getenv("TELEGRAM_TOKEN")
GROUP_ID = os.getenv("TELEGRAM_GROUP_ID")

# 🔍 בדיקה שהמשתנים מוגדרים
if not TOKEN:
    raise ValueError("⚠️ TELEGRAM_TOKEN חסר! יש להגדיר את משתנה הסביבה.")
else:
    print(f"✅ TELEGRAM_TOKEN נטען בהצלחה.")

if not GROUP_ID:
    raise ValueError("⚠️ TELEGRAM_GROUP_ID חסר! יש להגדיר את משתנה הסביבה.")
else:
    print(f"✅ TELEGRAM_GROUP_ID נטען בהצלחה: {GROUP_ID}")

# 🤖 אתחול הבוט
bot = TeleBot(TOKEN)

# 🕒 הגדרת אזור זמן ישראל
LOCAL_TIMEZONE = pytz.timezone("Asia/Jerusalem")

# 🔄 קובץ ההיסטוריה
HISTORY_FILE = "ads_history.csv"

# 📂 קובץ המודעות
ADS_FILE = "ads.csv"

# 📥 טעינת היסטוריית מודעות
def load_history():
    if os.path.exists(HISTORY_FILE):
        history = pd.read_csv(HISTORY_FILE)
        return set(history["Product Desc"].tolist())
    return set()

# 📤 שמירת מודעה שפורסמה
def save_to_history(ad):
    try:
        if not os.path.exists(HISTORY_FILE):
            pd.DataFrame([ad]).to_csv(HISTORY_FILE, index=False)
        else:
            history_data = pd.read_csv(HISTORY_FILE)
            history_data = pd.concat([history_data, pd.DataFrame([ad])], ignore_index=True)
            history_data.to_csv(HISTORY_FILE, index=False)
        print("✅ המודעה נשמרה בהיסטוריה.")
    except Exception as e:
        print(f"❌ שגיאה בשמירת ההיסטוריה: {e}")

# 📥 טעינת המודעות מהקובץ
def load_ads():
    global ads
    try:
        df = pd.read_csv(ADS_FILE)
        ads = df.to_dict("records")
        print(f"✅ נטענו {len(ads)} מודעות בהצלחה!")
    except Exception as e:
        print(f"❌ שגיאה בטעינת המודעות: {e}")
        ads = []

# 📌 יצירת הודעה מהמודעה
def create_ad_message(ad):
    return (
        f"🎉 **מבצע מטורף!** 🎉\n\n"
        f"📦 **{ad['Product Desc']}**\n"
        f"💰 מחיר מקורי: {ad['Origin Price']} $\n"
        f"🔥 מחיר לאחר הנחה: {ad['Discount Price']} $ ({ad['Discount']} הנחה!)\n"
        f"👍 משוב חיובי: {ad.get('Positive Feedback', 'אין מידע')}\n"
        f"\n🔗 [לחץ כאן למוצר]({ad['Product Url']})\n\n"
        f"מהרו לפני שייגמר! 🚀"
    )

# 📤 שליחת הודעה
def send_ad():
    global ads
    if not ads:
        print("⚠️ אין מודעות זמינות לפרסום.")
        return

    history_ads = load_history()
    available_ads = [ad for ad in ads if ad["Product Desc"] not in history_ads]

    if not available_ads:
        print("⚠️ אין מודעות חדשות לשלוח.")
        return

    ad = random.choice(available_ads)
    message = create_ad_message(ad)
    
    try:
        if pd.notna(ad["Video Url"]):
            bot.send_video(GROUP_ID, ad["Video Url"], caption=message, parse_mode="Markdown")
        elif pd.notna(ad["Image Url"]):
            bot.send_photo(GROUP_ID, ad["Image Url"], caption=message, parse_mode="Markdown")
        else:
            bot.send_message(GROUP_ID, message, parse_mode="Markdown")

        print(f"✅ מודעה נשלחה: {ad['Product Desc']}")
        save_to_history(ad)
        ads.remove(ad)
    except Exception as e:
        print(f"❌ שגיאה בשליחת המודעה: {e}")

# ⏳ בדיקה אם הזמן הנוכחי מתאים
def is_within_schedule():
    now = datetime.now(LOCAL_TIMEZONE).time()
    start_time = dt_time(8, 0)
    end_time = dt_time(23, 0)
    return start_time <= now <= end_time

# 📅 תזמון שליחת המודעות
def schedule_ads():
    print("✅ לוח זמנים להפצת מודעות הוגדר בהצלחה.")
    while True:
        if is_within_schedule():
            send_ad()
            now = datetime.now(LOCAL_TIMEZONE)
            next_hour = (now.replace(minute=0, second=0, microsecond=0) + pd.Timedelta(hours=1)).time()
            print(f"⏳ המודעה הבאה תישלח בשעה: {next_hour}")
            time.sleep(3600 - now.minute * 60 - now.second)
        else:
            print("⏳ הזמן מחוץ לטווח הפעילות, ממתין...")
            time.sleep(60)

# 🚀 הפעלת הבוט
if __name__ == "__main__":
    load_ads()
    send_ad()  # שליחת הודעה ראשונה עם ההפעלה
    schedule_ads()