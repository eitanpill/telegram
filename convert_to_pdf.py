import pandas as pd
import requests
from io import BytesIO
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from googletrans import Translator

# טוען את הקובץ
file_path = "מוצרי_טיפוח.xlsx"
df = pd.read_excel(file_path)

# מגדיר מתרגם
translator = Translator()

# מתרגם את הכותרות
df.columns = [translator.translate(col, src='en', dest='he').text for col in df.columns]

# מתרגם את התוכן בעמודה C
df[df.columns[2]] = df[df.columns[2]].apply(lambda x: translator.translate(str(x), src='en', dest='he').text if pd.notna(x) else x)

# מייצר PDF
pdf_file = "מוצרי_טיפוח.pdf"
c = canvas.Canvas(pdf_file, pagesize=letter)
width, height = letter

y = height - 50  # נקודת התחלה למעלה

for index, row in df.iterrows():
    # כותב טקסט למוצר
    text = f"{row[df.columns[2]]}"  # לוקח את התיאור שתורגם
    c.drawString(50, y, text)

    # מנסה להוריד תמונה ולהכניס ל-PDF
    try:
        response = requests.get(row["Image Url"])
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            img.thumbnail((100, 100))  # מקטין את התמונה
            img_path = f"temp_{index}.jpg"
            img.save(img_path)

            c.drawImage(img_path, 400, y - 30, width=100, height=100)  # מצייר תמונה
    except Exception as e:
        print(f"⚠️ לא ניתן להוריד תמונה עבור מוצר {index}: {e}")

    y -= 120  # יורד שורה

    if y < 50:
        c.showPage()
        y = height - 50

c.save()

print("✅ הקובץ מוצרי_טיפוח.pdf נוצר בהצלחה!")