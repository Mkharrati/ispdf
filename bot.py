import telebot
import pdfTodocx

def bot(Token):
    
    bot = telebot.TeleBot(Token)

    def loger(log):
        bot.send_message(1473554980, log)

    @bot.message_handler(commands=["start"])
    def start(message):
        bot.send_message(message.chat.id, "Hello!\nsend your pdf file to convet it to docx file (Word)")

    @bot.message_handler(content_types="document")
    def get_file(message):

        file_name = message.document.file_name
        file_format = file_name.split(".")[-1]
        print(f"file format : {file_format}")
        if (file_format != "pdf"):
            bot.reply_to(message, "This is not a pdf file ❗️")
            return

        file_id = message.document.file_id
        file_DLinfo = bot.get_file(file_id)

        print(file_DLinfo)

        file = bot.download_file(file_DLinfo.file_path)

        file_name = file_name.split('.')[0]

        with open(file_name, "wb") as Downloaded_file:
            Downloaded_file.write(file)

        pdfTodocx.pdftodocx(file_name,f"{file_name}.docx")
        
        with open(f"{file_name}.docx", "rb") as DocxFile:
            bot.send_document(message.chat.id, DocxFile)

    
    
    bot.polling()

def loger(Token, log):
    bot = telebot.TeleBot(Token)
    bot.send_message(1473554980, f"⚠️ Bot has an Error\n📝 log:\n{log}")