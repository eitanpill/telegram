import os
import pandas as pd
import random
import time
from telebot import TeleBot

# 📌 טעינת משתני סביבה
TOKEN = os.getenv("TELEGRAM_TOKEN")
GROUP_ID = os.getenv("TELEGRAM_GROUP_ID")

# 📌 אתחול הבוט
bot = TeleBot(TOKEN)

# 📌 קריאת הקובץ ads.csv
ads_file = "ads.csv"

def load_ads():
    try:
        df = pd.read_csv(ads_file)
        if "Sent" not in df.columns:
            df["Sent"] = "No"  # יצירת עמודה אם לא קיימת
        return df
    except Exception as e:
        print(f"❌ שגיאה בטעינת קובץ המודעות: {e}")
        return pd.DataFrame()

# 📌 שליחת מודעה רנדומלית שלא נשלחה
def send_ad():
    global ads_df
    available_ads = ads_df[ads_df["Sent"] == "No"]  # סינון מודעות שלא נשלחו
    if available_ads.empty:
        print("⚠️ אין מודעות חדשות לשליחה.")
        return

    ad = available_ads.sample(1).iloc[0]  # בחירת מודעה רנדומלית
    
    # 🔹 יצירת ההודעה
    message = f"""🎉 *מבצע מטורף!* 🎉

📦 {ad.get("Product Desc", "אין תיאור")}
💸 *מחיר מקורי:* {ad.get("Origin Price", "לא ידוע")}
💥 *מחיר לאחר הנחה:* {ad.get("Discount Price", "לא ידוע")} ({ad.get("Discount", "0%")} הנחה!)
👍 *משוב חיובי:* {ad.get("Positive Feedback", "אין מידע")}

🔗 [קישור למוצר]({ad.get("Product Url", "#")})

🚀 מהרו לפני שייגמר!
"""
    
    # 🔹 שליחת ההודעה עם וידאו או תמונה
    try:
        if pd.notna(ad["Video Url"]) and ad["Video Url"].startswith("http"):
            bot.send_video(GROUP_ID, ad["Video Url"], caption=message, parse_mode="Markdown")
        else:
            bot.send_photo(GROUP_ID, ad["Image Url"], caption=message, parse_mode="Markdown")
        
        print(f"✅ נשלחה מודעה: {ad['Product Desc']}")

        # 🔹 עדכון המודעה כ"נשלחה" ושמירת הקובץ
        ads_df.loc[ads_df["Product Desc"] == ad["Product Desc"], "Sent"] = "Yes"
        ads_df.to_csv(ads_file, index=False)
    
    except Exception as e:
        print(f"❌ שגיאה בשליחת המודעה: {e}")

# 📌 קריאת הנתונים והפעלת הבוט
ads_df = load_ads()

print("✅ הבוט פעיל! שולח מודעה ראשונה...")
send_ad()  # שליחת הודעה ראשונה מיד עם ההפעלה

# 📌 תזמון שליחה כל שעה עגולה
while True:
    now = time.localtime()
    minutes_to_next_hour = 60 - now.tm_min
    time.sleep(minutes_to_next_hour * 60)  # חכה עד השעה העגולה
    send_ad()