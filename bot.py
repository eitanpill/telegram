import telebot
import pandas as pd
import random
import time
import os

# טוקן ו-ID של הקבוצה
BOT_TOKEN = "הכנס_כאן_את_הטוקן"
GROUP_ID = "הכנס_כאן_את_הקבוצה"

# יצירת חיבור לבוט
bot = telebot.TeleBot(BOT_TOKEN)

# שם קובץ המודעות
ADS_FILE = "ads.csv"

def load_ads():
    """טוען את קובץ המודעות ושומר עמודה 'sent' אם לא קיימת."""
    df = pd.read_csv(ADS_FILE)
    if 'sent' not in df.columns:
        df['sent'] = False
    return df

def save_ads(df):
    """שומר את קובץ המודעות לאחר עדכון."""
    df.to_csv(ADS_FILE, index=False)

def pick_random_product(df):
    """בחירת מוצר רנדומלי שלא נשלח"""
    unsent_ads = df[df["sent"] == False]
    if unsent_ads.empty:
        print("📢 כל המודעות נשלחו! מאפסים את הרשימה...")
        df["sent"] = False
        save_ads(df)
        unsent_ads = df

    return unsent_ads.sample(n=1).iloc[0]

def send_ad():
    """שולח מודעה רנדומלית"""
    df = load_ads()
    product = pick_random_product(df)

    message = f"""
📢 *חדש בחנות!* 🛍️

🔹 *{product['Product Desc']}*
💰 מחיר מקורי: {product['Origin Price']}
🔥 מחיר מבצע: {product['Discount Price']} ({product['Discount']} הנחה!)
📦 {product['Sales180Day']} מכירות | 👍 {product['Positive Feedback']} דירוג חיובי
🔗 [לרכישה]( {product['Product Url']} )

    """
    
    # שליחת ההודעה עם תמונה (אם יש)
    if pd.notna(product['Image Url']):
        bot.send_photo(GROUP_ID, product['Image Url'], caption=message, parse_mode="Markdown")
    else:
        bot.send_message(GROUP_ID, message, parse_mode="Markdown")

    # סימון המוצר כנשלח ושמירה
    df.loc[df.index == product.name, 'sent'] = True
    save_ads(df)

    print(f"✅ נשלחה מודעה: {product['Product Desc']}")

# הפעלה ראשונית
send_ad()