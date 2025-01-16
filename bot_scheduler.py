import os
import pandas as pd
import asyncio
from telegram import Bot
from datetime import datetime, time

# קבלת הערכים מתוך Secrets
TOKEN = os.getenv('TOKEN')  # הטוקן נלקח מתוך Secrets
GROUP_ID = os.getenv('GROUP_ID')  # ה-Group ID נלקח מתוך Secrets

# אתחול הבוט
bot = Bot(token=TOKEN)

# משתנים גלובליים
ads = []  # רשימת המודעות
current_ad_index = 0  # אינדקס המודעה הנוכחית

# פונקציה ליצירת טקסט המודעה
def create_ad_message(row):
    """
    יצירת טקסט המודעה מבוסס על שורה בקובץ CSV
    """
    product_desc = row['Product Desc']
    origin_price = row['Origin Price']
    discount_price = row['Discount Price']
    discount = row['Discount']
    product_url = row['Product Url']
    feedback = row.get('Positive Feedback', 'אין מידע')  # משוב חיובי (ברירת מחדל: אין מידע)

    # יצירת טקסט ההודעה
    message = (
        f"🎉 **מבצע מטורף!** 🎉\n\n"
        f"📦 **{product_desc}**\n"
        f"💸 מחיר מקורי: {origin_price}\n"
        f"💥 מחיר לאחר הנחה: {discount_price} ({discount} הנחה!)\n"
        f"👍 משוב חיובי: {feedback}\n"
        f"\n🔗 [לחץ כאן למוצר]({product_url})\n\n"
        f"מהרו לפני שייגמר! 🚀"
    )
    return message

# פונקציה לטעינת מודעות מקובץ CSV
def load_ads(file_path):
    """
    קריאת קובץ CSV ויצירת רשימת מודעות
    """
    global ads
    try:
        data = pd.read_csv(file_path)  # קריאת הקובץ
        ads = data.to_dict('records')  # המרה לרשימת מילונים
        print(f"✅ נטענו {len(ads)} מודעות בהצלחה!")
    except Exception as e:
        print(f"❌ שגיאה בטעינת המודעות: {e}")

# פונקציה לשליחת המודעה הבאה
async def send_next_ad():
    """
    שליחת המודעה הבאה בתור לקבוצה
    """
    global current_ad_index

    if current_ad_index < len(ads):
        try:
            ad = ads[current_ad_index]
            message = create_ad_message(ad)
            image_url = ad.get('Image Url')  # קישור לתמונה

            # הדפסות למעקב
            print(f"📤 שליחת הודעה ל-Group ID: {GROUP_ID}")
            print(f"📩 תוכן ההודעה: {message}")
            print(f"🖼️ תמונה: {image_url}")

            # שליחת המודעה עם תמונה
            if pd.notna(image_url):  # אם יש קישור לתמונה
                await bot.send_photo(chat_id=GROUP_ID, photo=image_url, caption=message, parse_mode='Markdown')
            else:
                await bot.send_message(chat_id=GROUP_ID, text=message, parse_mode='Markdown')

            print(f"✅ מודעה מספר {current_ad_index + 1} פורסמה בהצלחה!")
            current_ad_index += 1
        except Exception as e:
            print(f"❌ שגיאה בפרסום המודעה: {e}")
    else:
        print("🎉 כל המודעות פורסמו!")

# פונקציה לבדיקה אם הזמן הנוכחי בטווח
def is_within_schedule():
    """
    בודקת אם הזמן הנוכחי בין 8:00 ל-23:45
    """
    now = datetime.now().time()
    start_time = time(8, 0)  # 8:00 בבוקר
    end_time = time(23, 45)  # 23:45 בערב
    return start_time <= now <= end_time

# תזמון פרסומים
async def schedule_ads():
    """
    הפעלת תזמון פרסום המודעות
    """
    # שליחת המודעה הראשונה מיד עם התחלת העבודה
    print("📤 שולח את המודעה הראשונה מידית...")
    await send_next_ad()  # שליחת המודעה הראשונה

    # תזמון מודעות כל 45 דקות
    while True:
        if is_within_schedule():
            await send_next_ad()
            await asyncio.sleep(2700)  # המתנה של 45 דקות (2700 שניות)
        else:
            print("⏳ הזמן הנוכחי מחוץ לטווח הפרסום. ממתין...")
            await asyncio.sleep(60)  # בדיקה חוזרת כל דקה

# התחלת הבוט
file_path = 'ads.csv'  # שם הקובץ צריך להיות ב-Replit
load_ads(file_path)  # טען מודעות

# שליחת הודעת בדיקה מידית
try:
    bot.send_message(chat_id=GROUP_ID, text="🚀 הודעת בדיקה: הבוט מחובר לטלגרם!")
    print("✅ הודעת בדיקה נשלחה בהצלחה!")
except Exception as e:
    print(f"❌ שגיאה בשליחת הודעת הבדיקה: {e}")

print("⏳ הבוט מתחיל לפעול...")
asyncio.run(schedule_ads())