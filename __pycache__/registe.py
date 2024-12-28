import telebot

bot = telebot.TeleBot("7901016275:AAF0gv9Q3K3XuypYnFmSbWze8dHOck3SDXg")


@bot.message_handler(func=lambda message: "p" in message.text)

def reg(message):
    bot.send_message(message.chat.id, "Send Your Photos:")
    bot.register_next_step_handler(message, File_id)

def File_id(message):
    if (message.text == "f"):
        bot.send_message(message.chat.id,"Ok. By :)")
        return
    if (message.content_type == "photo"):
        file_id = message.photo[-1].file_id
        bot.send_message(message.chat.id, file_id)
        bot.register_next_step_handler(message, File_id)



bot.polling()