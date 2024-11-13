import telebot

bot = telebot.TeleBot("7901016275:AAHdtR2oWFkBoRivuv3x21lnhZvYv66UgZw")

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Hello!\nsend your pdf file to convet it to docx (Word)")
bot.polling()
# @bot.message_handler(content_types="document")