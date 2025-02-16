import pandas as pd
from deep_translator import GoogleTranslator
import re

# נתיב הקובץ המקורי
file_path = "/Users/eitanpelles/Desktop/telegram-bot/ads.csv"

# קריאת הקובץ
df = pd.read_csv(file_path)

# פונקציה לניקוי תרגום ולהפיכת משפטים לקריאים יותר
def clean_translation(text):
    text = text.replace("  ", " ")  # הסרת רווחים כפולים
    text = text.replace(" ​​", " ")  # תיקון רווחים מוזרים
    text = text.replace(" :", ":")  # תיקון רווחים לפני נקודתיים
    text = text.replace(" ,", ",")  # תיקון רווחים לפני פסיקים
    text = text.replace(" ?", "?")  # תיקון רווחים לפני סימני שאלה
    text = text.replace(" !", "!")  # תיקון רווחים לפני סימני קריאה
    text = text.replace(" .", ".")  # תיקון רווחים לפני נקודה
    text = re.sub(r'\b(\w+) \1\b', r'\1', text)  # הסרת מילים כפולות
    return text.strip()  # הסרת רווחים מההתחלה ומהסוף

# בדיקה אם עמודת "Product Desc" קיימת
if "Product Desc" in df.columns:
    # פונקציה לתרגום טקסט ולניקויו
    def translate_text(text):
        try:
            translated = GoogleTranslator(source='auto', target='iw').translate(text)
            cleaned = clean_translation(translated)  # ניקוי הטקסט
            print(f"🔹 תורגם: {text} -> {cleaned}")  # הדפסת השינוי
            return cleaned
        except Exception as e:
            print(f"שגיאה בתרגום: {e}")
            return text  # במקרה של שגיאה, שומר על הטקסט המקורי

    # תרגום העמודה "Product Desc" בלבד עם ניקוי אוטומטי
    df["Product Desc"] = df["Product Desc"].apply(lambda x: translate_text(x) if pd.notna(x) else x)

    # נתיב לקובץ החדש
    translated_file_path = "/Users/eitanpelles/Desktop/telegram-bot/ads_translated_cleaned.csv"

    # שמירת הקובץ החדש
    df.to_csv(translated_file_path, index=False)
    print(f"✅ התרגום והניקוי הסתיימו! קובץ נשמר ב: {translated_file_path}")

else:
    print("❌ עמודת 'Product Desc' לא נמצאה בקובץ!")
