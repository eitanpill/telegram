import os
import pandas as pd
import time
import random
from telebot import TeleBot
from datetime import datetime, time as dt_time
import pytz

# אזור הזמן לישראל
LOCAL_TIMEZONE = pytz.timezone("Asia/Jerusalem")

# קבלת הטוקן וה-Group ID ממשתני הסביבה
TOKEN = os.getenv("TELEGRAM_TOKEN")
GROUP_ID = os.getenv("TELEGRAM_GROUP_ID")

# בדיקה שהמשתנים מוגדרים
if not TOKEN:
    raise ValueError("⚠️ TELEGRAM_TOKEN חסר! יש להגדיר את משתנה הסביבה TELEGRAM_TOKEN.")
else:
    print(f"✅ TOKEN נטען בהצלחה: {TOKEN[:10]}...")

if not GROUP_ID:
    raise ValueError("⚠️ TELEGRAM_GROUP_ID חסר! יש להגדיר את משתנה הסביבה TELEGRAM_GROUP_ID.")
else:
    print(f"✅ GROUP ID נטען בהצלחה: {GROUP_ID}")

# אתחול הבוט
bot = TeleBot(TOKEN)

# נתיבי קבצים
ADS_FILE = 'ads.csv'
HISTORY_FILE = 'ads_history.csv'

# טעינת מודעות מקובץ
def load_ads():
    """
    טוען מודעות מקובץ CSV
    """
    try:
        if os.path.exists(ADS_FILE):
            df = pd.read_csv(ADS_FILE)
            print(f"✅ נטענו {len(df)} מודעות בהצלחה!")
            return df.to_dict('records')
        else:
            print(f"⚠️ הקובץ {ADS_FILE} לא נמצא!")
            return []
    except Exception as e:
        print(f"❌ שגיאה בטעינת המודעות: {e}")
        return []

# שמירת מודעה להיסטוריה
def save_to_history(ad):
    """
    שומר מודעה שפורסמה בקובץ היסטוריה כדי למנוע פרסום כפול
    """
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

# יצירת הודעה למודעה
def create_ad_message(ad):
    """
    יוצר הודעת טקסט עם פרטי המודעה
    """
    return (
        f"🎉 **מבצע מטורף!** 🎉\n\n"
        f"📦 **{ad['Product Desc']}**\n"
        f"💸 מחיר מקורי: {ad['Origin Price']}\n"
        f"💥 מחיר אחרי הנחה: {ad['Discount Price']} ({ad['Discount']} הנחה!)\n"
        f"👍 משוב חיובי: {ad.get('Positive Feedback', 'אין מידע')}\n"
        f"\n🔗 [לחץ כאן למוצר]({ad['Product Url']})\n\n"
        f"מהרו לפני שייגמר! 🚀"
    )

# שליחת מודעה
def send_ad():
    """
    שולח מודעה אקראית שלא נשלחה בעבר ושומר אותה בהיסטוריה
    """
    ads = load_ads()
    if not ads:
        print("⚠️ אין מודעות זמינות למשלוח.")
        return
    
    history_ads = pd.read_csv(HISTORY_FILE)['Product Desc'].tolist() if os.path.exists(HISTORY_FILE) else []
    
    available_ads = [ad for ad in ads if ad['Product Desc'] not in history_ads]

    if not available_ads:
        print("🎉 כל המודעות כבר נשלחו! אין מודעות חדשות.")
        return

    ad = random.choice(available_ads)
    message = create_ad_message(ad)
    image_url = ad.get('Image Url')

    try:
        if pd.notna(image_url):
            bot.send_photo(chat_id=GROUP_ID, photo=image_url, caption=message, parse_mode="Markdown")
        else:
            bot.send_message(chat_id=GROUP_ID, text=message, parse_mode="Markdown")
        
        print(f"✅ מודעה נשלחה בהצלחה: {ad['Product Desc']}")
        save_to_history(ad)
    except Exception as e:
        print(f"❌ שגיאה בשליחת המודעה: {e}")

# בדיקת זמן לשליחת מודעה
def is_within_schedule():
    """
    מחזיר True אם הזמן הנוכחי בטווח השעות של הפרסום
    """
    now = datetime.now(LOCAL_TIMEZONE).time()
    start_time = dt_time(8, 0)
    end_time = dt_time(23, 0)
    return start_time <= now <= end_time

# תזמון שליחת המודעות
def schedule_ads():
    """
    מתזמן שליחת מודעות כל שעה בין 08:00 ל-23:00
    """
    while True:
        if is_within_schedule():
            send_ad()
            now = datetime.now(LOCAL_TIMEZONE)
            next_hour = (now.replace(minute=0, second=0, microsecond=0) + pd.Timedelta(hours=1)).time()
            print(f"⏳ ממתין לשעה הבאה: {next_hour}")
            time.sleep(3600 - now.minute * 60 - now.second)
        else:
            print("⏳ מחוץ לטווח הפעילות, ממתין 60 שניות...")
            time.sleep(60)

# הפעלת הבוט
if __name__ == "__main__":
    print("✅ הבוט הופעל!")
    schedule_ads()