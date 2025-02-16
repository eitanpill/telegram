import os
import pandas as pd
import time
from telebot import TeleBot
from datetime import datetime, time as dt_time
import pytz

# ✅ הגדרת אזור זמן
LOCAL_TIMEZONE = pytz.timezone("Asia/Jerusalem")  # אזור הזמן לישראל

# ✅ טעינת משתנים מהסביבה
TOKEN = os.getenv("TELEGRAM_TOKEN")
GROUP_ID = os.getenv("TELEGRAM_GROUP_ID")

# ✅ בדיקת משתני סביבה
if not TOKEN:
    raise ValueError("⚠️ TELEGRAM_TOKEN חסר! יש להגדיר את משתנה הסביבה.")
else:
    print(f"✅ TOKEN נטען בהצלחה: {TOKEN[:10]}...")

if not GROUP_ID:
    raise ValueError("⚠️ TELEGRAM_GROUP_ID חסר! יש להגדיר את משתנה הסביבה.")
else:
    print(f"✅ GROUP ID נטען בהצלחה: {GROUP_ID}")

# ✅ אתחול הבוט
bot = TeleBot(TOKEN)

# ✅ טעינת מודעות מקובץ CSV
def load_ads(file_path='ads.csv'):
    """
    טוען את רשימת המודעות מקובץ CSV
    """
    try:
        df = pd.read_csv(file_path)

        # בדיקה אם עמודת Sent קיימת
        if 'Sent' not in df.columns:
            print("⚠️ עמודת 'Sent' חסרה! מוסיף אותה עם ערך ברירת מחדל 'no'.")
            df['Sent'] = 'no'
            df.to_csv(file_path, index=False)

        print(f"✅ נטענו {len(df)} מודעות בהצלחה!")
        return df
    except Exception as e:
        print(f"❌ שגיאה בטעינת המודעות: {e}")
        return pd.DataFrame()

# ✅ יצירת הודעת מודעה
def create_ad_message(product):
    """
    יוצר טקסט של מודעה ממידע המוצר
    """
    try:
        return (
            f"🎉 **מבצע מטורף!** 🎉\n\n"
            f"📦 **{product['Product Desc']}**\n"
            f"💸 מחיר מקורי: {product['Origin Price']}\n"
            f"💥 מחיר לאחר הנחה: {product['Discount Price']} ({product['Discount']} הנחה!)\n"
            f"👍 משוב חיובי: {product.get('Positive Feedback', 'אין מידע')}\n"
            f"\n🔗 [לחץ כאן למוצר]({product['Product Url']})\n\n"
            f"מהרו לפני שייגמר! 🚀"
        )
    except KeyError as e:
        print(f"❌ שגיאה בהרכבת ההודעה: חסר מפתח {e}")
        return None

# ✅ שליחת מודעה רנדומלית
def send_ad():
    """
    שולח מודעה שלא נשלחה, מסמן אותה כ"נשלחה" ומעדכן בקובץ
    """
    global ads_df
    print("🔍 send_ad() הופעלה! בודק אם יש מודעות זמינות...")

    available_products = ads_df[ads_df["Sent"] == "no"]

    if available_products.empty:
        print("🎉 כל המודעות כבר נשלחו היום! אין מוצרים לשליחה.")
        return

    # ✅ בחירת מוצר רנדומלי
    product = available_products.sample(1).iloc[0]
    print(f"📢 נבחר מוצר: {product['Product Desc']}")

    message = create_ad_message(product)
    if not message:
        return

    image_url = product.get('Image Url', None)
    video_url = product.get('Video Url', None)

    try:
        if pd.notna(video_url) and isinstance(video_url, str) and video_url.strip():
            print(f"🎥 שולח וידאו: {video_url}")
            bot.send_video(chat_id=GROUP_ID, video=video_url, caption=message, parse_mode="Markdown")
        elif pd.notna(image_url) and isinstance(image_url, str) and image_url.strip():
            print(f"🖼️ שולח תמונה: {image_url}")
            bot.send_photo(chat_id=GROUP_ID, photo=image_url, caption=message, parse_mode="Markdown")
        else:
            print(f"📄 שולח הודעת טקסט בלבד")
            bot.send_message(chat_id=GROUP_ID, text=message, parse_mode="Markdown")

        print(f"✅ מודעה פורסמה: {product['Product Desc']}")

        # ✅ סימון המוצר כ"נשלח"
        ads_df.loc[ads_df.index == product.name, 'Sent'] = 'yes'
        ads_df.to_csv("ads.csv", index=False)
        
    except Exception as e:
        print(f"❌ שגיאה בשליחת המודעה: {e}")

# ✅ בדיקה אם הזמן הנוכחי בטווח השעות
def is_within_schedule():
    """
    בודק אם השעה בטווח 8:00 - 22:00
    """
    now = datetime.now(LOCAL_TIMEZONE).time()
    return dt_time(8, 0) <= now <= dt_time(22, 0)

# ✅ תזמון שליחת המודעות
def schedule_ads():
    """
    מתזמן שליחת מודעות כל שעה עגולה
    """
    while True:
        now = datetime.now(LOCAL_TIMEZONE)
        current_time = now.strftime('%H:%M:%S')

        print(f"⏳ [{current_time}] בודק אם הזמן מתאים לשליחת הודעה...")

        if is_within_schedule():
            print(f"⌛️ [{current_time}] בתוך שעות הפעילות - שולח הודעה...")
            send_ad()

            # ✅ מחשב את הזמן לשעה הבאה
            next_hour = (now.replace(minute=0, second=0, microsecond=0) + pd.Timedelta(hours=1)).time()
            print(f"⏳ ממתין לשעה הבאה: {next_hour}")
            time.sleep(3600 - now.minute * 60 - now.second)
        else:
            print(f"⏳ [{current_time}] מחוץ לשעות הפעילות, ממתין...")
            time.sleep(60)

# ✅ הפעלת הבוט
if __name__ == "__main__":
    ads_df = load_ads('ads.csv')

    # ✅ שולח הודעה ראשונה מיד עם ההפעלה
    print("🚀 הבוט התחיל לפעול!")
    send_ad()

    # ✅ תזמון השליחה
    schedule_ads()