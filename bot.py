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
CSV_FILE = 'ads.csv'  # קובץ המודעות

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

# טעינת מודעות
def load_ads():
    """
    טוען את רשימת המודעות מקובץ CSV
    """
    try:
        data = pd.read_csv(CSV_FILE)
        if 'Sent' not in data.columns:
            data['Sent'] = 'no'  # יצירת עמודת מעקב אם לא קיימת
        return data
    except Exception as e:
        print(f"❌ שגיאה בטעינת המודעות: {e}")
        return pd.DataFrame()

# שמירת המודעות לאחר עדכון הסטטוס
def save_ads(data):
    """
    שומר את קובץ המודעות לאחר עדכון הסטטוס
    """
    try:
        data.to_csv(CSV_FILE, index=False)
        print("✅ קובץ המודעות עודכן בהצלחה!")
    except Exception as e:
        print(f"❌ שגיאה בעדכון קובץ המודעות: {e}")

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

# פונקציה לבחירת מוצר שלא נשלח
def pick_random_product(data):
    """
    בוחר מוצר רנדומלי שלא נשלח עדיין
    """
    available_products = data[data["Sent"] != "yes"]
    if available_products.empty:
        print("🎉 כל המודעות כבר נשלחו היום! מאתחל מחדש...")
        data["Sent"] = "no"  # מאפס את המודעות שנשלחו
        save_ads(data)
        available_products = data

    return available_products.sample(1).iloc[0]  # בחירת שורה אחת רנדומלית

# פונקציה לשליחת מודעה
def send_ad():
    """
    שולח מודעה שלא נשלחה בעבר
    """
    global ads
    try:
        product = pick_random_product(ads)
        message = create_ad_message(product)
        image_url = product.get('Image Url')
        video_url = product.get('Video Url')
        index = ads[ads["Product Desc"] == product["Product Desc"]].index[0]

        if pd.notna(video_url) and str(video_url).strip():
            bot.send_video(chat_id=GROUP_ID, video=video_url, caption=message, parse_mode="Markdown")
        elif pd.notna(image_url) and str(image_url).strip():
            bot.send_photo(chat_id=GROUP_ID, photo=image_url, caption=message, parse_mode="Markdown")
        else:
            bot.send_message(chat_id=GROUP_ID, text=message, parse_mode="Markdown")

        print(f"✅ מודעה נשלחה: {product['Product Desc']}")

        # סימון המוצר שנשלח
        ads.at[index, "Sent"] = "yes"
        save_ads(ads)

    except Exception as e:
        print(f"❌ שגיאה בשליחת המודעה: {e}")

# פונקציה לבדיקה אם הזמן הנוכחי מתאים לפרסום
def is_within_schedule():
    """
    בודק אם הזמן הנוכחי בטווח השעות
    """
    now = datetime.now(LOCAL_TIMEZONE).time()
    start_time = dt_time(8, 0)
    end_time = dt_time(22, 0)
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
    print("🚀 הבוט התחיל לפעול!")
    
    # טוען מודעות מהקובץ
    ads = load_ads()
    
    # שולח הודעה מיד בהפעלה
    send_ad()

    # מפעיל את Flask לשמירה על הבוט פעיל
    keep_alive()
    
    # מתזמן את הפרסומים
    schedule_ads()