import telebot
import tools
import img2pdf
from tools import Message_Details

back_button = "Back"

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
        global keyboard
        keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2,resize_keyboard=True)

        keyboard.add("PDF to Word","Image To PDF","Unlock PDF")

        bot.send_message(message.chat.id, "Hello!\nChoose:",reply_markup=keyboard)

    # Image to pdf
    @bot.message_handler(func=lambda message : "Image To PDF" in message.text)

    def get_image(message):
        back_keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        back_keyboard.add(back_button)
        bot.send_message(message.chat.id, "send your image:",reply_markup=back_keyboard)
        bot.register_next_step_handler(message, imageToPdf)

    def imageToPdf(message):
        print(message.text)
        if (message.text == back_button):
            bot.send_message(message.chat.id, "Hello!\nChoose:",reply_markup=keyboard)
            return
        
        elif (message.content_type != "photo"):
            bot.send_message(message.chat.id, "Pleas just Send image ‼️",reply_markup=keyboard)

        image = Downloadimg(message)

        file = tools.image_to_pdf(image)

        with open(file, "rb") as pdf:
            bot.send_document(message.chat.id,pdf)

        bot.send_message(message.chat.id, "Hello!\nChoose:",reply_markup=keyboard)
    
    # Pdf to docx
    @bot.message_handler(func=lambda message: "PDF to Word" in message.text)

    # Get PDF from user
    def get_pdf(message):
        Backkeyborad = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        Backkeyborad.add("Back")
        bot.send_message(message.chat.id, "Send your PDF file:",reply_markup=Backkeyborad)
        bot.register_next_step_handler(message, ToDocx)
    
    # Covert PDF To docx
    def ToDocx(message):

        if (message.text == back_button):
            bot.send_message(message.chat.id, "Hello!\nChoose:",reply_markup=keyboard)
            return
        
        elif (message.content_type != "document"):
            bot.reply_to(message, "Pleas just Send PDF file‼️",reply_markup=keyboard)
            return

        file_name = message.document.file_name
        file_format = file_name.split(".")[-1]
        print(f"file format : {file_format}")
        if (file_format != "pdf"):
            bot.reply_to(message, "Pleas just Send PDF file‼️")
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
            bot.send_message(message.chat.id, "Hello!\nChoose:",reply_markup=keyboard)

    # Unlock PDF
    @bot.message_handler(func=lambda message: "Unlock PDF" in message.text)
    def send(message):
        back_keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        back_keyboard.add(back_button)
        bot.send_message(message.chat.id, "Send Your PDF File To Unlock it :")
        bot.register_next_step_handler(message, Unlock)
    
    def Unlock(message):
       file = Downloadimg(message)
       with open("Unlock.pdf", "wb") as Newfile:
           Newfile.write(file)

        
    bot.polling()
# Loger
def loger(Token, log):
    bot = telebot.TeleBot(Token)
    bot.send_message(1473554980, f"⚠️ Bot has an Error\n📝 log:\n{log}")