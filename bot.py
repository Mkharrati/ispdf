import telebot
import tools
import img2pdf

finish_keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
finish_keyboard.add("Finish","Back")

back_keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
back_keyboard.add("Back")

Token = "7566162751:AAF6EyNbs0XSVBvb-0jhd9Bq514qMLffjhA"
bot = telebot.TeleBot(Token)

def Runbot():
    tools.create_Folder("Content")

    #Start
    @bot.message_handler(commands=["start"])
    def start(message):
        tools.Chech_User_folder(message)
        global keyboard
        keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2,resize_keyboard=True)

        keyboard.add("PDF to Word","Image To PDF","Unlock PDF")

        bot.send_message(message.chat.id, "Hello!\nChoose:",reply_markup=keyboard)
    
    # Image to pdf
    @bot.message_handler(func=lambda message : "Image To PDF" in message.text)
    def ImageTopdf(message):
        tools.Chech_User_folder(message)
        
        if tools.message_content_type(message) == "photo":
            tools.get_images(message)
            bot.send_message(message.chat.id, f"PDF Page : {len(tools.slistdir(message=message))}", reply_markup=finish_keyboard)
        elif tools.message_content_type(message) == "text":
            if message.text == "Finish":
                waite_message = bot.send_message(message.chat.id, "Please waite ⏳.")
                tools.send_document(message, tools.Convert_imageToPdf(message))
                bot.delete_message(message.chat.id, message_id=waite_message.message_id)
                tools.delete_user_Content(message)
                start(message)
                return
            elif message.text == "Back":
                start(message)
                tools.delete_user_Content(message)
                return
            elif message.text == "Image To PDF":
                    if len(tools.slistdir(message=message)) == 0:
                        bot.send_message(message.chat.id, "Send Your photos :", reply_markup=back_keyboard)
        
            else:
                wrangfile_message = bot.send_message(message.chat.id, "Please Just Send <b>Photo</b>" ,parse_mode="html", reply_markup=finish_keyboard)
                bot.delete_message(message.chat.id, message_id=message.message_id)
        else:
            wrangfile_message = bot.send_message(message.chat.id, "Please Just Send <b>Photo</b>" ,parse_mode="html", reply_markup=finish_keyboard)

        #def do(message):
       
        bot.register_next_step_handler(message, ImageTopdf)

    # Pdf to docx
    @bot.message_handler(func=lambda message: "PDF to Word" in message.text)
    def pdf_to_Word_handler(message):
        tools.Chech_User_folder(message)
        bot.send_message(message.chat.id, "Please Send your pdf File : ")
        bot.register_next_step_handler(message, pdf_to_Word)
    def pdf_to_Word(message):
        if  message.content_type == "text" and message.text == "back":
            start(message)
            tools.delete_user_Content(message)
            return
        if tools.check_content_type(message,"document",".pdf"):
            pdf_path = tools.saveFile(file=tools.DownloadFile(message),path=f"./Content/{message.chat.id}/{tools.random_name()}.pdf")
            tools.send_document(message, tools.convert_pdf_to_docx(pdf_path))
        else:
            bot.send_message(message.chat.id, "Please send only pdf file.")
            tools.delete_user_Content(message)
            start(message)
            tools.delete_user_Content(message)
            return


    # Unlock PDF
    @bot.message_handler(func=lambda message: "Unlock PDF" in message.text)
    def send(message):
        back_keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        #back_keyboard.add(back_button)
        bot.send_message(message.chat.id, "Send Your PDF File To Unlock it :")
        bot.register_next_step_handler(message, Unlock)
    
    def Unlock(message):
        file_name = f"Unlock_{message.document.file_name}"
       
        #file = Downloadimg(message)
        with open(file_name, "wb") as Newfile:
            Newfile.write(file)
        with open(file_name, "rb") as SendFile:
            bot.send_document(message.chat.id, SendFile)

        

        
    bot.polling()
# Loger

def loger(log):
    bot.send_message(1473554980, f"⚠️ Bot has an Error\n📝 log:\n{log}")
