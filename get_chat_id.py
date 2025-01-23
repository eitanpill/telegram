import telebot

TELEGRAM_TOKEN = '8144674866:AAE8olkDboxTdVWWFeg-a5wU9r10k1gSEmE'
bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=['start'])
def get_chat_id(message):
    chat_id = message.chat.id
    print(f"Chat ID is: {chat_id}")

bot.polling()