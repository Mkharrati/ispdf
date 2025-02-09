import telebot
import tools
import img2pdf
import os
from dotenv import load_dotenv

# loading the env file
load_dotenv()


keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2,resize_keyboard=True)
keyboard.add("PDF to Word", "Image To PDF", "Word to PDF", "Unlock PDF", "Merge PDF")

finish_keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
finish_keyboard.add("Finish","Back")

back_keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
back_keyboard.add("Back")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is missing. Please add your token in your environment file. Check the `.env` file.")
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
def Runbot():
    tools.create_Folder("Content")

    #Start
    @bot.message_handler(commands=["start"])
    def start(message):
        tools.delete_user_Content(message)
        tools.Chech_User_folder(message)
        global keyboard

        bot.send_message(message.chat.id, "Hello!\nChoose:",reply_markup=keyboard)
    
    # Image to pdf
    @bot.message_handler(func=lambda message : "Image To PDF" in message.text)
    def ImageTopdf(message):
        tools.Chech_User_folder(message)
        if tools.message_content_type(message) == "photo":            
            # check image size
            #
            tools.get_images(message)
            bot.send_message(message.chat.id, f"PDF Page : {len(tools.list_file_by_time_added(message=message))}", reply_markup=finish_keyboard)
        elif tools.message_content_type(message) == "text":
            if message.text == "Finish":
                tools.send_document(message, tools.Convert_imageToPdf(message))
                tools.delete_user_Content(message)
                start(message)
                return
            elif message.text == "Back":
                start(message)
                tools.delete_user_Content(message)
                return
            elif message.text == "Image To PDF":
                if len(tools.list_file_by_time_added(message=message)) == 0:
                    bot.send_message(message.chat.id, "Send Your photos :", reply_markup=back_keyboard)
        
            else:
                bot.send_message(message.chat.id, "Please Just Send <b>Photo</b>" ,parse_mode="html", reply_markup=finish_keyboard)
        else:
            bot.send_message(message.chat.id, "Please Just Send <b>Photo</b>" ,parse_mode="html", reply_markup=finish_keyboard)

        #def do(message):
       
        bot.register_next_step_handler(message, ImageTopdf)

    # Pdf to docx
    @bot.message_handler(func=lambda message: "PDF to Word" in message.text)
    def get_pdf(message):
        bot.send_message(message.chat.id, "Please send your PDF file : ", reply_markup=back_keyboard)
        bot.register_next_step_handler(message, send_docx_file)

    def send_docx_file(message):
        print(tools.check_content_type(message, "document"))
        if tools.check_content_type(message, "text") and message.text == "Back":
            start(message)
            return
        elif tools.check_content_type(message, "document") == False:
            bot.send_message(message.chat.id, "Plese send only pdf file ❗️")
            start(message)
            return
        if tools.check_file_size(message, size=10000000) == False:
            bot.send_message(message.chat.id, "Please send a file under 10 MB ❗️")
            start(message)
            return
        pdf_file = tools.DownloadFile(message)
        pdf_file = tools.saveFile(pdf_file, f"./Content/{message.chat.id}/{tools.random_name()}.pdf")

        # check pdf file that is really a pdf file or no.
        if tools.is_pdf_file(pdf_file) == False:
            bot.send_message(message.chat.id, "Plese send only pdf file ❗️")
            start(message)
            return

        docx_file = tools.convert_pdf_to_docx(message, pdf_file)
        tools.send_document(message, docx_file)
        tools.delete_user_Content(message)
        start(message)



    # Unlock PDF
    @bot.message_handler(func=lambda message: "Unlock PDF" in message.text)
    def get_pdf(message):
        tools.Chech_User_folder(message)
        bot.send_message(message.chat.id, "Please send your pdf file : ", reply_markup=back_keyboard)
        bot.register_next_step_handler(message, UnlockPdf_and_send)
    def UnlockPdf_and_send(message):
        if tools.check_content_type(message, "document") and tools.check_file_size(message, size=10000000) == False:
            bot.send_message(message.chat.id, "Please send a file under 10 MB ❗️")
            start(message)
            return
        elif tools.check_content_type(message, "text") and message.text == "Back":
            start(message)
            return
        elif tools.check_content_type(message, "document") == False:
            bot.send_message(message.chat.id, "Please only send pdf file ❗️")
            start(message)
            return
        pdf_path = tools.saveFile(tools.DownloadFile(message),path=f"./Content/{message.chat.id}/{tools.random_name()}.pdf")
        tools.Unlock(pdf_path)
        tools.send_document(message, pdf_path)
        tools.delete_user_Content(message)
        start(message)
        return

    # Docx to PDF
    @bot.message_handler(func=lambda message: "Word to PDF" in message.text)
    def get_docx(message):
        bot.send_message(message.chat.id, "Please send your Word file :", reply_markup=back_keyboard)
        bot.register_next_step_handler(message, send_pdf)
    def send_pdf(message):
        if tools.check_content_type(message, "document") and tools.check_file_size(message, size=10000000) == False:
            bot.send_message(message.chat.id, "Please send a file under 10 MB ❗️")
            start(message)
            return
        elif tools.check_content_type(message, "text") and message.text == "Back":
            start(message)
            return
        # extension=".docx"
        elif tools.check_content_type(message, "document", extension=".docx") == False:
            bot.send_message(message.chat.id, "Please only send docx file ❗️")
            start(message)
            return
        docx_file_path = tools.DownloadFile(message)
        docx_file_path = tools.saveFile(docx_file_path, f"./Content/{message.chat.id}/{tools.random_name()}.docx")

        # check docx file that is really a docx file or no.
        if tools.is_docx_file(docx_file_path) == False:
            bot.send_message(message.chat.id, "Please only send docx file ❗️")
            start(message)
            return
        
        pdf_path = tools.convert_docx_to_pdf(message ,docx_file_path)
        tools.send_document(message, pdf_path)
        tools.delete_file(pdf_path)
        start(message)
    
    # Merge PDF
    @bot.message_handler(func=lambda message: "Merge PDF" in message.text)
    def get_pdf(message):
        print(message.id)
        if tools.check_content_type(message, "text"):
            if message.text == "Back":
                start(message)
                return
            elif message.text == "Finish":
                if len(tools.list_file_by_time_added(message=message)) > 0 :
                    merged_pdf = tools.merge_pdf(message, tools.list_file_by_time_added(message=message))
                    tools.send_document(message, merged_pdf)
                    start(message)
                    return
            elif message.text == "Merge PDF":
                global send_your_pdf_file_message
                send_your_pdf_file_message = bot.send_message(message.chat.id, "Please send your pdf file :", reply_markup=back_keyboard)
                bot.register_next_step_handler(message, get_pdf)
            else:
                bot.send_message(message.chat.id, "Please only send pdf file ❗️")
                start(message)
                return
        elif tools.check_content_type(message, "document", ".pdf"):
            pdf = tools.DownloadFile(message)
            pdf = tools.saveFile(pdf, path=f"./Content/{message.chat.id}/{tools.random_name()}.pdf")
            if tools.is_pdf_file(pdf) == False:
                bot.send_message(message.chat.id, "Please only send pdf file ❗️")
                start(message)
                return
            else:
                bot.send_message(message.chat.id, f"recived!\ncount of pdfs is : {len(tools.list_file_by_time_added(message=message))}\nSend next :",reply_markup=finish_keyboard)
                bot.register_next_step_handler(message, get_pdf)
        else:
            bot.send_message(message.chat.id, "Please only send pdf file ❗️")
            start(message)
            return   

            
        
    bot.polling()
# Loger

def loger(log):
    bot.send_message(1473554980, f"⚠️ Bot has an Error\n📝 log:\n{log}")

