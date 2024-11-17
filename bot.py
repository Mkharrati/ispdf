import telebot
import tools
import img2pdf
from tools import Message_Details

def bot(Token):
    
    bot = telebot.TeleBot(Token)

    def Downloadimg(message):

        message = Message_Details(message)

        file_id = message.file_id()
        fileinfo = bot.get_file(file_id)
        image = bot.download_file(fileinfo.file_path)
        with open(file_id, "wb") as imagee:
            imagee.write(image)

        return (image)

    def loger(log):
        bot.send_message(1473554980, log)

    #Start
    @bot.message_handler(commands=["start"])
    def start(message):
        keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2,resize_keyboard=True)

        keyboard.add("pdf TO Word","Image To Pdf","Unlock Pdf")

        bot.send_message(message.chat.id, "Hello!\nsend your pdf file to convet it to docx file (Word)",reply_markup=keyboard)

    # Image to pdf
    @bot.message_handler(content_types="photo")
    def imageToPdf(message):

        image = Downloadimg(message)

        file = tools.image_to_pdf(image)

        with open(file, "rb") as pdf:
            bot.send_document(message.chat.id,pdf)
    
    # Pdf to docx
    @bot.message_handler(content_types="document")
    def ToDocx(message):

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

        tools.tools(file_name,f"{file_name}.docx")
        
        with open(f"{file_name}.docx", "rb") as DocxFile:
            bot.send_document(message.chat.id, DocxFile)

    
    
    bot.polling()
# Loger
def loger(Token, log):
    bot = telebot.TeleBot(Token)
    bot.send_message(1473554980, f"⚠️ Bot has an Error\n📝 log:\n{log}")