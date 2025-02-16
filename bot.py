import time
import random
import logging
from datetime import datetime, timedelta
import pandas as pd
import telebot
import pytz

# טוקן של הבוט
BOT_TOKEN = "8130275609:AAFTV972VTD0Ym1xjSoxuBM99d8z4ipdSLo"

# מזהה הקבוצה
GROUP_ID = "-1002423906987"

# הגדרת לוגים
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

# יצירת אובייקט בוט
bot = telebot.TeleBot(BOT_TOKEN)

# שעון ישראל
ISRAEL_TZ = pytz.timezone("Asia/Jerusalem")

# נתיבים לקבצים
ADS_FILE = "ads.csv"  # קובץ המודעות
SENT_ADS_FILE = "sent-ads.txt"  # קובץ למודעות שכבר נשלחו

def load_products():
    """טוען את המודעות מקובץ ads.csv"""
    return pd.read_csv(ADS_FILE)

def load_sent_products():
    """טוען את המודעות שכבר נשלחו"""
    try:
        with open(SENT_ADS_FILE, "r") as f:
            return f.read().splitlines()
    except FileNotFoundError:
        return []

def save_sent_product(product_id):
    """שומר את המודעה שנשלחה"""
    with open(SENT_ADS_FILE, "a") as f:
        f.write(f"{product_id}\n")

def pick_random_product(products):
    """בחירת מוצר רנדומלי שלא נשלח"""
    sent_products = load_sent_products()
    available_products = products[~products["ID"].astype(str).isin(sent_products)]
    if available_products.empty:
        logging.info("🎉 כל המודעות נשלחו! מאפסים רשימה.")
        open(SENT_ADS_FILE, "w").close()  # איפוס הקובץ
        available_products = products
    return available_products.sample().iloc[0]

def format_message(product):
    """מכין את הודעת המוצר"""
    message = (
        f"✨ *{product['Product Desc']}*\n\n"
        f"💵 מחיר מקורי: {product['Origin Price']}\n"
        f"🏷️ מחיר לאחר הנחה: {product['Discount Price']} ({product['Discount']} הנחה!)\n\n"
        f"🌟 {product['Positive Feedback']} פידבק חיובי\n"
        f"📦 נמכרו: {product['Sales180Day']} ב-180 הימים האחרונים\n\n"
        f"[🔗 למידע נוסף ולרכישה]({product['Product Url']})"
    )
    return message

def send_ad():
    """שולח מודעה בקבוצה"""
    now = datetime.now(ISRAEL_TZ)
    if not (8 <= now.hour < 23):
        logging.info("⏳ השעה מחוץ לטווח, ממתינים...")
        return

    logging.info(f"⌛️ השעה {now.strftime('%H:%M')} - שולחים הודעה...")
    products = load_products()
    product = pick_random_product(products)
    message = format_message(product)

    try:
        if pd.notna(product["Image Url"]):  # אם יש תמונה
            bot.send_photo(GROUP_ID, product["Image Url"], caption=message, parse_mode="Markdown")
        elif pd.notna(product["Video Url"]):  # אם יש וידאו
            bot.send_video(GROUP_ID, product["Video Url"], caption=message, parse_mode="Markdown")
        else:  # הודעה טקסטואלית בלבד
            bot.send_message(GROUP_ID, message, parse_mode="Markdown")
        save_sent_product(product["ID"])
    except Exception as e:
        logging.error(f"⚠️ שגיאה בשליחת הודעה: {e}")

def run_scheduler():
    """מבצע תזמון לשליחת ההודעות בכל שעה עגולה"""
    send_ad()  # שליחת הודעה מיד בהפעלה
    while True:
        now = datetime.now(ISRAEL_TZ)
        next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        sleep_time = (next_hour - now).total_seconds()
        logging.info(f"🕒 ממתינים לשעה העגולה הבאה ({next_hour.strftime('%H:%M')})...")
        time.sleep(sleep_time)
        send_ad()

if __name__ == "__main__":
    logging.info("🚀 הבוט התחיל לפעול!")
    run_scheduler()