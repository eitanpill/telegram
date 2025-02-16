import os
import time
import random
import pandas as pd
import schedule
import telebot

# ✅ טעינת משתני סביבה
TOKEN = os.getenv("TELEGRAM_TOKEN")
GROUP_ID = os.getenv("TELEGRAM_GROUP_ID")

if not TOKEN:
    raise ValueError("⚠️ TELEGRAM_TOKEN חסר! יש להגדיר את משתנה הסביבה TELEGRAM_TOKEN.")
if not GROUP_ID:
    raise ValueError("⚠️ TELEGRAM_GROUP_ID חסר! יש להגדיר את משתנה הסביבה TELEGRAM_GROUP_ID.")

bot = telebot.TeleBot(TOKEN)

# ✅ טעינת קובץ המודעות
CSV_FILE = "ads.csv"

# 🔄 פונקציה לטעינת נתונים מהקובץ
def load_ads():
    try:
        df = pd.read_csv(CSV_FILE)
        if 'Sent' not in df.columns:
            df['Sent'] = "No"  # הוספת עמודה למעקב אם המודעה נשלחה
        print(f"📜 קובץ נטען עם {len(df)} מודעות.")
        return df
    except Exception as e:
        print(f"❌ שגיאה בטעינת הקובץ: {e}")
        return None

# 🛒 פונקציה לבחירת מודעה שלא נשלחה
def get_unsent_ad():
    df = load_ads()
    if df is None:
        print("⚠️ לא ניתן לטעון את קובץ המודעות.")
        return None, None

    available_ads = df[df['Sent'] == "No"]
    
    if available_ads.empty:
        print("⚠️ אין מודעות חדשות לשליחה!")
        return None, None

    ad = available_ads.sample(n=1).iloc[0]  # בחירת מודעה אקראית
    print(f"🎯 מודעה שנבחרה לשליחה: {ad['Product Desc']}")
    return ad, df

# 📝 פונקציה ליצירת תוכן מודעה
def create_ad_message(ad):
    product_desc = ad.get("Product Desc", "אין תיאור")
    origin_price = ad.get("Origin Price", "לא ידוע")
    discount_price = ad.get("Discount Price", "לא ידוע")
    discount = ad.get("Discount", "0%")
    feedback = ad.get("Positive Feedback", "אין מידע")
    product_url = ad.get("Product Url", "#")

    message = (
        f"🎉 *מבצע מטורף!* 🎉\n\n"
        f"📦 *{product_desc}*\n"
        f"💸 מחיר מקורי: {origin_price}\n"
        f"💥 מחיר לאחר הנחה: {discount_price} ({discount} הנחה!)\n"
        f"👍 משוב חיובי: {feedback}\n\n"
        f"🔗 [לחץ כאן למוצר]({product_url})\n\n"
        f"מהרו לפני שייגמר! 🚀"
    )
    return message

# ✈️ פונקציה לשליחת מודעה
def send_ad():
    print("📢 מנסה לשלוח מודעה...")
    ad, df = get_unsent_ad()
    if ad is None:
        return

    message = create_ad_message(ad)
    video_url = ad.get("Video Url", "").strip()
    image_url = ad.get("Image Url", "").strip()

    try:
        if video_url:
            print(f"🎥 שולח וידאו: {video_url}")
            bot.send_video(GROUP_ID, video_url, caption=message, parse_mode="Markdown")
        elif image_url:
            print(f"🖼 שולח תמונה: {image_url}")
            bot.send_photo(GROUP_ID, image_url, caption=message, parse_mode="Markdown")
        else:
            print("📩 שולח טקסט בלבד")
            bot.send_message(GROUP_ID, message, parse_mode="Markdown")
        
        print("✅ מודעה נשלחה בהצלחה!")
        
        # ✅ סימון המודעה כנשלחה בקובץ
        df.loc[df["Product Desc"] == ad["Product Desc"], "Sent"] = "Yes"
        df.to_csv(CSV_FILE, index=False)
        print(f"📌 {ad['Product Desc']} סומן כ'נשלח'")

    except Exception as e:
        print(f"❌ שגיאה בשליחת מודעה: {e}")

# ⏰ תזמון שליחה כל שעה עגולה
def schedule_ads():
    print("⏳ מתזמן שליחה כל שעה עגולה...")
    schedule.every().hour.at(":00").do(send_ad)

# ✅ הפעלת שליחה ראשונית
print("🚀 הבוט הופעל! שולח מודעה ראשונה...")
send_ad()

# ✅ תזמון שליחות
schedule_ads()

# 🔄 לולאת ריצה תמידית
while True:
    schedule.run_pending()
    time.sleep(60)