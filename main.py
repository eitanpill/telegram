import os
import pandas as pd
import time
from telebot import TeleBot
from keep_alive import keep_alive
from datetime import datetime, time as dt_time
import pytz

# משתנים גלובליים
LOCAL_TIMEZONE = pytz.timezone("Asia/Jerusalem")  # אזור הזמן לישראל
TOKEN = os.getenv("TELEGRAM_TOKEN")  # הטוקן נלקח מתוך משתני הסביבה
GROUP_ID = os.getenv("TELEGRAM_GROUP_ID")  # ה-Group ID נלקח מתוך משתני הסביבה

# בדיקה אם הטוקן וה-Group ID מוגדרים
if not TOKEN:
    raise ValueError("⚠️ TOKEN חסר! יש להגדיר את משתנה הסביבה TELEGRAM_TOKEN.")
else:
    print(f"✅ TOKEN נטען בהצלחה: {TOKEN[:10]}...")

if not GROUP_ID:
    raise ValueError("⚠️ GROUP ID חסר! יש להגדיר את משתנה הסביבה TELEGRAM_GROUP_ID.")
else:
    print(f"✅ GROUP ID נטען בהצלחה: {GROUP_ID}")

# אתחול הבוט
bot = TeleBot(TOKEN)

ads = []  # רשימת המודעות
sent_ads = set()  # מודעות שכבר נשלחו

# פונקציה לטעינת מודעות מקובץ CSV
def load_ads(file_path='ads.csv'):
    """
    טוען את רשימת המודעות מקובץ CSV
    """
    global ads
    try:
        data = pd.read_csv(file_path)  # קריאת הקובץ
        ads = data.to_dict('records')  # המרה לרשימת מילונים
        print(f"✅ נטענו {len(ads)} מודעות בהצלחה!")
    except Exception as e:
        print(f"❌ שגיאה בטעינת המודעות: {e}")

# פונקציה ליצירת תוכן ההודעה
def create_ad_message(row):
    """
    יוצר טקסט מודעה משורה בקובץ
    """
    product_desc = row['Product Desc']
    origin_price = row['Origin Price']
    discount_price = row['Discount Price']
    discount = row['Discount']
    product_url = row['Product Url']
    feedback = row.get('Positive Feedback', 'אין מידע')
    
    return (
        f"🎉 **מבצע מטורף!** 🎉\n\n"
        f"📦 **{product_desc}**\n"
        f"💸 מחיר מקורי: {origin_price}\n"
        f"💥 מחיר לאחר הנחה: {discount_price} ({discount} הנחה!)\n"
        f"👍 משוב חיובי: {feedback}\n"
        f"\n🔗 [לחץ כאן למוצר]({product_url})\n\n"
        f"מהרו לפני שייגמר! 🚀"
    )

# פונקציה לשליחת מודעה
def send_ad():
    """
    שולח מודעה שלא נשלחה בעבר
    """
    global sent_ads
    if len(sent_ads) < len(ads):
        for i, ad in enumerate(ads):
            if i not in sent_ads:
                message = create_ad_message(ad)
                image_url = ad.get('Image Url')
                try:
                    if pd.notna(image_url):
                        bot.send_photo(chat_id=GROUP_ID, photo=image_url, caption=message, parse_mode="Markdown")
                    else:
                        bot.send_message(chat_id=GROUP_ID, text=message, parse_mode="Markdown")
                    print(f"✅ מודעה מספר {i+1} פורסמה בהצלחה!")
                    sent_ads.add(i)
                    break
                except Exception as e:
                    print(f"❌ שגיאה בשליחת המודעה: {e}")
    else:
        print("🎉 כל המודעות כבר פורסמו היום!")

# פונקציה לבדיקה אם הזמן הנוכחי מתאים לפרסום
def is_within_schedule():
    """
    בודק אם הזמן הנוכחי בטווח השעות
    """
    now = datetime.now(LOCAL_TIMEZONE).time()
    start_time = dt_time(8, 0)
    end_time = dt_time(23, 0)
    return start_time <= now <= end_time

# תזמון שליחת המודעות
def schedule_ads():
    """
    מתזמן שליחת מודעות כל שעה עגולה
    """
    while True:
        if is_within_schedule():
            send_ad()
            now = datetime.now(LOCAL_TIMEZONE)
            next_hour = (now.replace(minute=0, second=0, microsecond=0) + pd.Timedelta(hours=1)).time()
            print(f"⏳ ממתין לשעה הבאה: {next_hour}")
            time.sleep(3600 - now.minute * 60 - now.second)
        else:
            print("⏳ הזמן מחוץ לטווח הפעילות. ממתין...")
            time.sleep(60)

# הפעלת הבוט ושמירה על פעילות
if __name__ == "__main__":
    # טוען מודעות מהקובץ
    load_ads('ads.csv')
    
    # מפעיל את Flask לשמירה על הבוט פעיל
    keep_alive()
    print("✅ הבוט מוכן ומתחיל לפעול.")
    
    # מתזמן את הפרסומים
    schedule_ads()