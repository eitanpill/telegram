import os
import pandas as pd
import time
import random
from telebot import TeleBot
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
history_file = 'ads_history.csv'  # קובץ היסטוריה למודעות שכבר פורסמו

# פונקציה לטעינת מודעות מקובץ CSV
def load_ads(file_path='ads.csv'):
    """
    טוען את רשימת המודעות מקובץ CSV
    """
    global ads
    try:
        # קריאת הקובץ עם הסרת רווחים משמות הכותרות
        data = pd.read_csv(file_path)
        data.columns = data.columns.str.strip()  # הסרת רווחים משמות העמודות

        # הצגת הכותרות לזיהוי בעיות
        print("🔍 כותרות שנמצאו בקובץ:", list(data.columns))

        # בדיקה אם 'Product Desc' קיים
        if 'Product Desc' not in data.columns:
            raise KeyError(f"❌ הכותרת 'Product Desc' לא נמצאה! כותרות בקובץ: {list(data.columns)}")

        ads = data.to_dict('records')  # המרה לרשימת מילונים
        print(f"✅ נטענו {len(ads)} מודעות בהצלחה!")
    except Exception as e:
        print(f"❌ שגיאה בטעינת המודעות: {e}")

# פונקציה לשמירת היסטוריית המודעות
def save_to_history(ad):
    """
    שומר מודעה שפורסמה לקובץ היסטוריה
    """
    try:
        if not os.path.exists(history_file):
            # יצירת קובץ היסטוריה אם לא קיים
            pd.DataFrame([ad]).to_csv(history_file, index=False)
        else:
            # הוספת המודעה לקובץ היסטוריה קיים
            history_data = pd.read_csv(history_file)
            history_data = history_data.append(ad, ignore_index=True)
            history_data.to_csv(history_file, index=False)
        print("✅ המודעה הועברה לקובץ היסטוריה.")
    except Exception as e:
        print(f"❌ שגיאה בשמירת ההיסטוריה: {e}")

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
    שולח מודעה רנדומלית שלא נשלחה בעבר ומעביר אותה להיסטוריה
    """
    global ads
    if not ads:
        print("⚠️ אין מודעות זמינות לפרסום.")
        return

    # בדיקה אם קיימת עמודה 'Product Desc'
    if 'Product Desc' not in ads[0]:
        print("❌ שגיאה: הכותרות בקובץ ads.csv לא תואמות את הציפיות!")
        print("🔍 כותרות שנמצאו:", list(ads[0].keys()))
        return

    # סינון מודעות שלא נשלחו עדיין
    available_ads = [ad for ad in ads if ad['Product Desc'] not in history_ads]

    if not available_ads:
        print("🎉 כל המודעות כבר נשלחו בעבר.")
        return

    ad = random.choice(available_ads)  # בחירת מודעה רנדומלית
    message = create_ad_message(ad)
    image_url = ad.get('Image Url')

    try:
        if pd.notna(image_url):
            bot.send_photo(chat_id=GROUP_ID, photo=image_url, caption=message, parse_mode="Markdown")
        else:
            bot.send_message(chat_id=GROUP_ID, text=message, parse_mode="Markdown")
        
        print(f"✅ מודעה פורסמה בהצלחה: {ad['Product Desc']}")
        save_to_history(ad)  # שמירת המודעה להיסטוריה
        ads.remove(ad)  # הסרת המודעה מרשימת המודעות
    except Exception as e:
        print(f"❌ שגיאה בשליחת המודעה: {e}")

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
    
    # מתזמן את הפרסומים
    print("✅ הבוט מוכן ומתחיל לפעול.")
    schedule_ads()