import os
import pandas as pd
import time
from telebot import TeleBot
from keep_alive import keep_alive
from datetime import datetime, time as dt_time
import pytz

# משתנים גלובליים
LOCAL_TIMEZONE = pytz.timezone("Asia/Jerusalem")  # אזור הזמן לישראל
TOKEN = os.getenv("TELEGRAM_TOKEN")  # הטוקן מתוך משתני הסביבה
GROUP_ID = os.getenv("TELEGRAM_GROUP_ID")  # ה-Group ID מתוך משתני הסביבה

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

# פונקציה לטעינת המודעות מקובץ CSV
def load_ads(file_path='ads.csv'):
    """
    טוען את רשימת המודעות מקובץ CSV, ומוודא שהעמודה Sent קיימת
    """
    try:
        df = pd.read_csv(file_path)
        
        # לוודא שאין רווחים בשמות העמודות
        df.columns = df.columns.str.strip()
        
        # בדיקה אם העמודה Sent קיימת, אם לא – יצירה שלה
        if 'Sent' not in df.columns:
            print("⚠️ עמודת 'Sent' לא נמצאה! נוצרת עמודה חדשה עם 'no'.")
            df['Sent'] = 'no'
        
        # הדפסת נתונים ללוגים
        sent_yes = df[df['Sent'] == 'yes'].shape[0]
        sent_no = df[df['Sent'] == 'no'].shape[0]
        print(f"✅ מודעות שנשלחו (yes): {sent_yes}")
        print(f"✅ מודעות שלא נשלחו (no): {sent_no}")

        return df
    except Exception as e:
        print(f"❌ שגיאה בטעינת המודעות: {e}")
        return pd.DataFrame()

# פונקציה ליצירת הודעה
def create_ad_message(row):
    """
    יוצר הודעת טקסט מעוצבת ממוצר
    """
    product_desc = row.get('Product Desc', 'אין תיאור')
    origin_price = row.get('Origin Price', 'לא ידוע')
    discount_price = row.get('Discount Price', 'לא ידוע')
    discount = row.get('Discount', '0%')
    product_url = row.get('Product Url', '#')
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
    שולח מוצר שלא נשלח בעבר, מסמן אותו כ'נשלח' ושומר לקובץ
    """
    global ads_df
    
    available_products = ads_df[ads_df["Sent"] == "no"]

    if available_products.empty:
        print("🎉 כל המודעות כבר נשלחו היום!")
        return

    # בחירת מוצר רנדומלי
    product = available_products.sample(1).iloc[0]

    message = create_ad_message(product)
    image_url = product.get('Image Url', None)
    video_url = product.get('Video Url', None)

    try:
        if pd.notna(video_url) and isinstance(video_url, str) and video_url.strip():
            bot.send_video(chat_id=GROUP_ID, video=video_url, caption=message, parse_mode="Markdown")
        elif pd.notna(image_url) and isinstance(image_url, str) and image_url.strip():
            bot.send_photo(chat_id=GROUP_ID, photo=image_url, caption=message, parse_mode="Markdown")
        else:
            bot.send_message(chat_id=GROUP_ID, text=message, parse_mode="Markdown")

        print(f"✅ מודעה פורסמה: {product['Product Desc']}")

        # סימון המוצר כ'נשלח'
        ads_df.loc[ads_df.index == product.name, 'Sent'] = 'yes'
        ads_df.to_csv("ads.csv", index=False)
        
    except Exception as e:
        print(f"❌ שגיאה בשליחת המודעה: {e}")

# פונקציה לבדיקה אם הזמן הנוכחי מתאים לפרסום
def is_within_schedule():
    """
    בודק אם השעה הנוכחית בטווח 08:00 - 22:00
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
            print(f"⌛️ השעה {datetime.now(LOCAL_TIMEZONE).strftime('%H:%M')} - שולחים הודעה...")
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
    ads_df = load_ads('ads.csv')

    # שמירה על הבוט פעיל
    keep_alive()
    print("✅ הבוט מוכן ומתחיל לפעול.")

    # שולח הודעה ראשונה מיד
    send_ad()

    # מתזמן את הפרסומים
    schedule_ads()