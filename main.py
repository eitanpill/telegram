import os
import time
import random
import telebot
import pandas as pd
import schedule
import requests
from flask import Flask

# קריאת משתנים מהסביבה
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROUP_ID = os.getenv("TELEGRAM_GROUP_ID")

if not TOKEN:
    raise ValueError("❌ TOKEN חסר! יש להגדיר את משתנה הסביבה TELEGRAM_BOT_TOKEN.")
if not GROUP_ID:
    raise ValueError("❌ ID חסר! יש להגדיר את משתנה הסביבה TELEGRAM_GROUP_ID.")

print("✅ TOKEN נטען בהצלחה:", TOKEN[:10] + "...")
print("✅ GROUP ID נטען בהצלחה:", GROUP_ID)

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

ads_file = "ads.csv"
sent_ads_file = "sent_ads.csv"

# פתיחים אקראיים
OPENING_LINES = [
    "📣 הדיל שחיפשתם ממש כאן! אל תפספסו!",
    "🔥 מבצע לוהט שמצאנו לכם – רק לחברי הקבוצה!",
    "🛍 הדיל הכי שווה ברשת – שווה בדיקה!",
    "🎯 המוצר הזה פשוט חובה בכל בית!",
]

def translate_to_hebrew(text):
    try:
        res = requests.post(
            "https://translate.googleapis.com/translate_a/single",
            params={"client": "gtx", "sl": "auto", "tl": "he", "dt": "t", "q": text},
            timeout=10
        )
        if res.status_code == 200:
            return res.json()[0][0][0]
        return text
    except:
        return text

def load_ads():
    df = pd.read_csv(ads_file)
    print(f"✅ נטענו {len(df)} מודעות בהצלחה!")
    return df

def load_sent_ads():
    if not os.path.exists(sent_ads_file):
        return set()
    df = pd.read_csv(sent_ads_file)
    return set(df['Product Id'].astype(str))

def save_sent_ad(product_id):
    mode = 'a' if os.path.exists(sent_ads_file) else 'w'
    header = not os.path.exists(sent_ads_file)
    pd.DataFrame([[product_id]], columns=["Product Id"]).to_csv(sent_ads_file, mode=mode, header=header, index=False)

def create_ad_message(row):
    opening = random.choice(OPENING_LINES)
    title = translate_to_hebrew(row['Title'])
    price = row['Local Price']
    rating = row['Rating']
    sold = row['Sold']
    url = row['Product Url']
    coupon_discount = row['Coupon Discount']
    coupon_min_spend = row['Coupon Min Spend']
    coupon_code = row['Coupon Code']

    message = f"""🛒 *Aliexpress KSP - הדילים הכי שווים:*
{opening}

🚀 *{title}*
✔️ {sold} מכירות
⭐ דירוג: {rating} שביעות רצון

💰 מחיר בלעדי: *{price} ₪*

"""
    if pd.notna(coupon_code):
        message += f"""🎟️ קופון הנחה מיוחד!
💰 הנחה של {coupon_discount} ₪ בקנייה מעל {coupon_min_spend} ₪
🔑 קוד קופון: `{coupon_code}`
⏳ תקף לזמן מוגבל – השתמשו לפני שייגמר!
"""

    message += f"""
🔗 [להזמנה עכשיו]({url})

⏳ המלאי אוזל – הזמינו לפני שייגמר!
📢 רוצים עוד דילים לוהטים? הצטרפו עכשיו!
👉 Hot Deals 24/7

#דיל_חם #מבצע_לוהט #חייב_לקנות
"""
    return message

def send_ad():
    ads_df = load_ads()
    sent_ads = load_sent_ads()
    for _, row in ads_df.iterrows():
        product_id = str(row['Product Id'])
        if product_id not in sent_ads:
            try:
                message = create_ad_message(row)
                bot.send_message(GROUP_ID, message, parse_mode="Markdown", disable_web_page_preview=False)
                save_sent_ad(product_id)
                print(f"📤 נשלחה מודעה: {product_id}")
                break
            except Exception as e:
                print(f"❌ שגיאה בשליחת מודעה {product_id}:", e)
                continue

def schedule_ads():
    schedule.every().day.at("09:00").do(send_ad)
    schedule.every().day.at("12:00").do(send_ad)
    schedule.every().day.at("15:00").do(send_ad)
    schedule.every().day.at("18:00").do(send_ad)

    while True:
        schedule.run_pending()
        time.sleep(10)

@app.route('/')
def index():
    return "Bot is running."

if __name__ == "__main__":
    from threading import Thread
    print("✅ הבוט מוכן ומתחיל לפעול.")
    Thread(target=schedule_ads).start()
    app.run(debug=False, host="0.0.0.0", port=8080)