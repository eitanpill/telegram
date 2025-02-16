import os
import pandas as pd
import time
import random
from telebot import TeleBot
from datetime import datetime, time as dt_time
import pytz

# 🌍 משתנים גלובליים
LOCAL_TIMEZONE = pytz.timezone("Asia/Jerusalem")  # אזור הזמן ישראל
TOKEN = os.getenv("TELEGRAM_TOKEN")  # טעינת הטוקן
GROUP_ID = os.getenv("TELEGRAM_GROUP_ID")  # טעינת ה-GROUP ID

# ✅ בדיקה אם הטוקן וה-Group ID מוגדרים
if not TOKEN:
    raise ValueError("⚠️ TELEGRAM_TOKEN חסר! יש להגדיר אותו.")
else:
    print(f"✅ TELEGRAM_TOKEN נטען בהצלחה.")

if not GROUP_ID:
    raise ValueError("⚠️ TELEGRAM_GROUP_ID חסר! יש להגדיר אותו.")
else:
    print(f"✅ TELEGRAM_GROUP_ID נטען בהצלחה: {GROUP_ID}")

# 📌 אתחול הבוט
bot = TeleBot(TOKEN)

# 📝 פונקציה לטעינת מודעות
def load_ads(file_path='ads.csv'):
    try:
        df = pd.read_csv(file_path)
        print(f"✅ נטענו {len(df)} מודעות בהצלחה!")
        
        # אם אין עמודת 'Sent' נוסיף אותה עם ערך ברירת מחדל "no"
        if 'Sent' not in df.columns:
            df['Sent'] = 'no'
            df.to_csv(file_path, index=False)

        return df
    except Exception as e:
        print(f"❌ שגיאה בטעינת קובץ המודעות: {e}")
        return None

# 📝 פונקציה לשליחת הודעה לטלגרם
def send_ad():
    df = load_ads()  # טוען את המודעות מהקובץ
    if df is None or df.empty:
        print("⚠️ אין מודעות זמינות לשליחה.")
        return
    
    available_ads = df[df['Sent'] == 'no']  # בודק מודעות שלא נשלחו
    
    if available_ads.empty:
        print("🎉 כל המודעות כבר נשלחו!")
        return
    
    ad = available_ads.sample(n=1).iloc[0]  # בוחר מודעה רנדומלית

    # בניית ההודעה
    product_desc = ad.get("Product Desc", "אין תיאור")
    origin_price = ad.get("Origin Price", "לא ידוע")
    discount_price = ad.get("Discount Price", "לא ידוע")
    discount = ad.get("Discount", "0%")
    product_url = ad.get("Product Url", "אין קישור")
    image_url = ad.get("Image Url", None)
    video_url = ad.get("Video Url", None)
    feedback = ad.get("Positive Feedback", "אין מידע")

    message = (
        f"🎉 **מבצע מטורף!** 🎉\n\n"
        f"📦 **{product_desc}**\n"
        f"💸 מחיר מקורי: {origin_price}\n"
        f"💥 מחיר לאחר הנחה: {discount_price} ({discount} הנחה!)\n"
        f"👍 משוב חיובי: {feedback}\n"
        f"\n🔗 [לחץ כאן למוצר]({product_url})\n\n"
        f"מהרו לפני שייגמר! 🚀"
    )

    try:
        if pd.notna(video_url) and isinstance(video_url, str) and video_url.strip():
            bot.send_video(chat_id=GROUP_ID, video=video_url, caption=message, parse_mode="Markdown")
            print("📽️ נשלחה הודעה עם וידאו.")
        elif pd.notna(image_url) and isinstance(image_url, str) and image_url.strip():
            bot.send_photo(chat_id=GROUP_ID, photo=image_url, caption=message, parse_mode="Markdown")
            print("🖼️ נשלחה הודעה עם תמונה.")
        else:
            bot.send_message(chat_id=GROUP_ID, text=message, parse_mode="Markdown")
            print("📄 נשלחה הודעה ללא תמונה/וידאו.")

        # עדכון העמודה "Sent" ל- "yes" כדי למנוע שליחה חוזרת
        df.loc[df["Product Desc"] == product_desc, "Sent"] = "yes"
        df.to_csv('ads.csv', index=False)  # שמירת העדכון בקובץ
        print(f"✅ המוצר '{product_desc}' סומן כנשלח.")
    except Exception as e:
        print(f"❌ שגיאה בשליחת המודעה: {e}")

# 🕒 פונקציה לבדוק אם הזמן מתאים לשליחת הודעה
def is_within_schedule():
    now = datetime.now(LOCAL_TIMEZONE).time()
    return dt_time(8, 0) <= now <= dt_time(22, 0)  # עובד רק בין 08:00 - 22:00

# ⏳ תזמון שליחת מודעות כל שעה
def schedule_ads():
    while True:
        if is_within_schedule():
            print(f"⌛️ השעה {datetime.now(LOCAL_TIMEZONE).strftime('%H:%M')} - שולחים הודעה...")
            send_ad()
            time.sleep(3600)  # ממתין שעה לפני שליחה נוספת
        else:
            print("🕒 מחוץ לשעות הפעילות. ממתין 10 דקות...")
            time.sleep(600)  # ממתין 10 דקות לפני בדיקה חוזרת

# 🚀 הפעלת הבוט
if __name__ == "__main__":
    print("✅ הבוט מוכן ומתחיל לפעול.")
    
    # שולח הודעה ראשונה עם ההפעלה
    send_ad()
    
    # מפעיל את לולאת התזמון
    schedule_ads()