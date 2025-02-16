import os
import random
import time
import pandas as pd
import telebot
import schedule

# 🛠️ טעינת משתני הסביבה
TOKEN = os.getenv("TELEGRAM_TOKEN")
GROUP_ID = os.getenv("TELEGRAM_GROUP_ID")

# 🛠️ בדיקה שהכל תקין
if not TOKEN:
    raise ValueError("⚠️ TELEGRAM_TOKEN חסר! יש להגדיר את משתנה הסביבה TELEGRAM_TOKEN.")
if not GROUP_ID:
    raise ValueError("⚠️ TELEGRAM_GROUP_ID חסר! יש להגדיר את משתנה הסביבה TELEGRAM_GROUP_ID.")

# 📡 יצירת חיבור לבוט
bot = telebot.TeleBot(TOKEN)

# 🔍 היסטוריית מוצרים שנשלחו כדי למנוע כפילויות
history_ads = []

# 🎯 פונקציה לטעינת המודעות
def load_ads(file_path="ads.csv"):
    global ads
    try:
        data = pd.read_csv(file_path)
        data.columns = data.columns.str.strip()  # הסרת רווחים מיותרים

        print(f"✅ עמודות בקובץ: {data.columns.tolist()}")  # בדיקה

        if data.empty:
            print("⚠️ הקובץ ריק! אין מודעות לשלוח.")
            return []

        ads = data.to_dict("records")  # המרת הנתונים לרשימה
        print(f"✅ נטענו {len(ads)} מודעות בהצלחה!")
        return ads
    except Exception as e:
        print(f"❌ שגיאה בטעינת המודעות: {e}")
        return []

# 📝 יצירת הודעת מודעה מעוצבת
def create_ad_message(row):
    print("🔍 טוען מודעה:", row)  # בדיקה

    product_desc = row.get("Product Desc", "🛍️ מוצר לא ידוע").strip()
    origin_price = row.get("Origin Price", "לא ידוע").strip()
    discount_price = row.get("Discount Price", "לא ידוע").strip()
    discount = row.get("Discount", "0%").strip()
    sales = row.get("Sales180Day", "לא ידוע").strip()
    feedback = row.get("Positive Feedback", "אין מידע").strip()
    product_url = row.get("Product Url", "").strip()
    image_url = row.get("Image Url", "").strip()
    video_url = row.get("Video Url", "").strip()

    if not product_desc or not product_url:
        print("⚠️ מוצר חסר נתונים - לא נשלח.")
        return None

    message = (
        f"🎉 **מבצע מיוחד!** 🎉\n\n"
        f"📦 **{product_desc}**\n"
        f"💸 מחיר מקורי: ~~{origin_price}~~\n"
        f"🔥 מחיר מבצע: **{discount_price}** ({discount} הנחה!)\n"
        f"📊 מכירות ב-180 ימים אחרונים: {sales}\n"
        f"👍 משוב חיובי: {feedback}\n\n"
        f"🔗 [🔗 קישור למוצר]({product_url})\n\n"
        f"⚡ **מהרו לפני שייגמר!** ⚡"
    )

    return message, image_url, video_url

# 🚀 שליחת מודעה רנדומלית
def send_ad():
    global history_ads

    if not ads:
        print("⚠️ אין מודעות זמינות לשליחה.")
        return

    available_ads = [ad for ad in ads if ad["Product Desc"] not in history_ads]

    if not available_ads:
        print("⚠️ כל המודעות כבר נשלחו בעבר. מרענן רשימה...")
        history_ads.clear()  # איפוס היסטוריה
        available_ads = ads

    ad = random.choice(available_ads)
    result = create_ad_message(ad)

    if not result:
        return

    message, image_url, video_url = result

    try:
        if video_url:
            bot.send_video(GROUP_ID, video_url, caption=message, parse_mode="Markdown")
        elif image_url:
            bot.send_photo(GROUP_ID, image_url, caption=message, parse_mode="Markdown")
        else:
            bot.send_message(GROUP_ID, message, parse_mode="Markdown")

        history_ads.append(ad["Product Desc"])  # הוספה להיסטוריה
        print("✅ מודעה נשלחה בהצלחה!")
    except Exception as e:
        print(f"❌ שגיאה בשליחת ההודעה: {e}")

# 📅 תזמון שליחת המודעות כל שעה עגולה
def schedule_ads():
    schedule.every().hour.at(":00").do(send_ad)
    print("✅ תזמון אוטומטי כל שעה עגולה נקבע בהצלחה!")

# 🚀 הפעלת הבוט
if __name__ == "__main__":
    print("✅ הבוט התחיל לפעול... בודק חיבורים!")

    ads = load_ads()  # טעינת מודעות
    send_ad()  # שליחת מודעה ראשונה מיד עם ההפעלה
    schedule_ads()  # קביעת לוח זמנים

    # לולאה אינסופית לשמירה על ריצה
    while True:
        schedule.run_pending()
        time.sleep(1)