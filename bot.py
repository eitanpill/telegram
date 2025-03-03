import telebot
import pandas as pd
import random
import os
import time

# טוקן הבוט וה-ID של הקבוצה
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROUP_ID = os.getenv("TELEGRAM_GROUP_ID")

if not BOT_TOKEN:
    raise ValueError("⚠️ TOKEN חסר! יש להגדיר את משתנה הסביבה TELEGRAM_TOKEN.")
if not GROUP_ID:
    raise ValueError("⚠️ GROUP ID חסר! יש להגדיר את משתנה הסביבה TELEGRAM_GROUP_ID.")

bot = telebot.TeleBot(BOT_TOKEN)

# טען את רשימת המודעות
ads_file = "ads.csv"

# קריאת קובץ המודעות
def load_ads():
    return pd.read_csv(ads_file)

# בחירת מודעה רנדומלית שלא נשלחה
def pick_random_ad(ads):
    available_ads = ads[ads["Sent"] != "Yes"]  # בחירת מודעות שטרם נשלחו
    if available_ads.empty:
        print("📢 כל המודעות נשלחו! מאפסים רשימה...")
        ads["Sent"] = "No"
        ads.to_csv(ads_file, index=False)
        available_ads = ads  # עכשיו יש מודעות לבחור מהן

    return available_ads.sample(n=1).iloc[0]

# שליחת מודעה
def send_ad():
    ads = load_ads()
    ad = pick_random_ad(ads)

    message = f"""
📢 *מבצע מיוחד!*
🛍️ {ad["Product Desc"]}
💲 מחיר מקורי: {ad["Origin Price"]}
🔥 מחיר אחרי הנחה: {ad["Discount Price"]} ({ad["Discount"]} הנחה!)
👍 ביקורות חיוביות: {ad["Positive Feedback"]}
🔗 [לרכישה]({ad["Promotion Url"]})
    """

    if not pd.isna(ad["Image Url"]):
        bot.send_photo(GROUP_ID, ad["Image Url"], caption=message, parse_mode="Markdown")
    else:
        bot.send_message(GROUP_ID, message, parse_mode="Markdown")

    # סימון המודעה כנשלחה
    ads.loc[ads["Promotion Url"] == ad["Promotion Url"], "Sent"] = "Yes"
    ads.to_csv(ads_file, index=False)
    print(f"✅ נשלחה מודעה: {ad['Product Desc']}")

# רוץ כל שעה וחצי בין 08:00 ל-23:00
while True:
    current_hour = time.localtime().tm_hour
    if 8 <= current_hour <= 23:
        send_ad()
    time.sleep(90 * 60)  # המתנה של שעה וחצי