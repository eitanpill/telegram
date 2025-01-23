# שימוש בתמונה בסיסית של Python 3.9
FROM python:3.9-slim

# הגדרת ספריית העבודה
WORKDIR /app

# העתקת קובץ requirements.txt
COPY requirements.txt .

# התקנת התלויות
RUN pip install --no-cache-dir -r requirements.txt

# העתקת שאר הקבצים
COPY . .

# הגדרת פורט 8080
ENV PORT 8080

# הרצת Gunicorn עם Flask
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "main:app"]