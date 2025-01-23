import telebot

TELEGRAM_TOKEN = '8144674866:AAE8olkDboxTdVWWFeg-a5wU9r10k1gSEmE'
bot = telebot.TeleBot(TELEGRAM_TOKEN)

updates = bot.get_updates()

# מציאת ה chat_id של הקבוצה
if updates:
    update = updates[0]
    chat_id = update.message.chat.id
    print(f"Chat ID: {chat_id}")
else:
    print("No updates found.")