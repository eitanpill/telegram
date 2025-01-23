from flask import Flask
from threading import Thread
<<<<<<< HEAD
from os import system

# יצירת Flask App
=======

>>>>>>> 743a9e31a4cade7228b3c6be77045a6715ab4b32
app = Flask('')

@app.route('/')
def home():
    return "Bot is running and accessible!"

<<<<<<< HEAD
# פונקציה להרצת Flask עם Gunicorn
def run():
    system("gunicorn -w 4 -b 0.0.0.0:8080 keep_alive:app")

# פונקציה לשמירה על חיי השרת
def keep_alive():
    t = Thread(target=run)
    t.start()
=======
def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
>>>>>>> 743a9e31a4cade7228b3c6be77045a6715ab4b32
