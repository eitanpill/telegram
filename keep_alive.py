from flask import Flask
from threading import Thread
from os import system

# יצירת Flask App
app = Flask('')

@app.route('/')
def home():
    return "Bot is running and accessible!"

# פונקציה להרצת Flask עם Gunicorn
def run():
    system("gunicorn -w 4 -b 0.0.0.0:8080 keep_alive:app")

# פונקציה לשמירה על חיי השרת
def keep_alive():
    t = Thread(target=run)
    t.start()