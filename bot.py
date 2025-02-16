import os
import pandas as pd
import time
import random
from telebot import TeleBot
from keep_alive import keep_alive
from datetime import datetime, time as dt_time
import pytz
import re

# משתנים גלובליים
LOCAL_TIMEZONE = pytz.timezone("Asia/Jerusalem")  # אזור הזמן לישראל
TOKEN = os.getenv("TELEGRAM_TOKEN")  # טוקן מתוך משתני הסביבה
GROUP_ID = os.getenv("TELEGRAM_GROUP_ID")  # Group ID מתוך משתני הסביבה

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

# פונקציה למילוט תווים מיוחדים ב-Markdown V2
def escape_markdown_v2(text):
    escape_chars = r"*_[]()~`>#+-=|{}.!<>"
    return re.sub(r"([{}])".format(re.escape(escape_chars)), r"\\\1", str(text))

# פונקציה לטעינת מודעות מקובץ CSV
def load_ads(file_path='ads.csv'):
    """
    טוען את רשימת המודעות מקובץ CSV
    """
    try:
        df = pd.read_csv(file_path)
        
        # אם עמודת "Sent" לא קיימת, נוסיף אותה
        if 'Sent' not in df.columns:
            df['Sent'] = 'no'
        
        print(f"✅ נטענו {len(df)} מודעות בהצלחה!")
        return df
    except Exception as e:
        print(f"❌ שגיאה בטעינת המודעות: {e}")
        return pd.DataFrame()

# פונקציה ליצירת תוכן ההודעה
def create_ad_message(row):
    """
    יוצר טקסט מודעה משורה בקובץ
    """
    product_desc = escape_markdown_v2(row.get('Product Desc', 'אין תיאור'))
    origin_price = escape_markdown_v2(row.get('Origin Price', 'לא ידוע'))
    discount_price = escape_markdown_v2(row.get('Discount Price', 'לא ידוע'))
    discount = escape_markdown_v2(row.get('Discount', '0%'))
    product_url = escape_markdown_v2(row.get('Product Url', '#'))
    feedback = escape_markdown_v2(row.get('Positive Feedback', 'אין מידע'))
    
    return (
        f"🎉 *מבצע מטורף!* 🎉\n\n"
        f"📦 *{product_desc}*\n"
        f"💸 *מחיר מקורי:* {origin_price}\n"
        f"💥 *מחיר לאחר הנחה:* {discount_price} ({discount} הנחה!)\n"
        f"👍 *משוב חיובי:* {feedback}\n"
        f"\n🔗 [לחץ כאן למוצר]({product_url})\n\n"
        f"מהרו לפני שייגמר! 🚀"
    )

# פונקציה לבחירת מודעה שלא נשלחה
def pick_random_product(df):
    """
    מחזירה מוצר אקראי שלא נשלח
    """
    available_products = df[df["Sent"] == "no"]
    
    if available_products.empty:
        print("🎉 כל המודעות כבר נשלחו היום!")
        return None
    
    return available_products.sample(1).iloc[0]

# פונקציה לשליחת מודעה
def send_ad():
    """
    שולח מודעה שלא נשלחה בעבר ומעדכן את הקובץ
    """
    global ads_df

    product = pick_random_product(ads_df)

    if product is None:
        return  # אין מוצרים זמינים

    message = create_ad_message(product)
    image_url = product.get('Image Url')
    video_url = product.get('Video Url')

    try:
        if pd.notna(video_url) and video_url.strip():
            bot.send_video(chat_id=GROUP_ID, video=video_url, caption=message, parse_mode="MarkdownV2")
        elif pd.notna(image_url) and image_url.strip():
            bot.send_photo(chat_id=GROUP_ID, photo=image_url, caption=message, parse_mode="MarkdownV2")
        else:
            bot.send_message(chat_id=GROUP_ID, text=message, parse_mode="MarkdownV2")

        print(f"✅ המודעה פורסמה בהצלחה: {product['Product Desc']}")

        # סימון המוצר כ"נשלח"
        ads_df.loc[ads_df["Product Desc"] == product["Product Desc"], "Sent"] = "yes"
        ads_df.to_csv("ads.csv", index=False)  # שמירת הנתונים לקובץ

    except Exception as e:
        print(f"❌ שגיאה בשליחת המודעה: {e}")

# פונקציה לבדיקה אם הזמן הנוכחי מתאים לפרסום
def is_within_schedule():
    """
    בודק אם הזמן הנוכחי בטווח השעות 8:00-22:00
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
    
    # שומר את הבוט פעיל עם Flask
    keep_alive()
    print("🚀 הבוט התחיל לפעול!")

    # שליחת הודעה ראשונה מיד עם ההפעלה
    send_ad()

    # מתזמן את הפרסומים
    schedule_ads()