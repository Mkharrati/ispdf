import telebot
import tools
import img2pdf

finish_keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
finish_keyboard.add("Finish","Back")

back_keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
back_keyboard.add("Back")

Token = "7901016275:AAGPkMv3JPYHZj7AqjnX95EqP0qAREPwQwU"
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

    # Get PDF from user
    def get_pdf(message):
        Backkeyborad = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        Backkeyborad.add("Back")
        bot.send_message(message.chat.id, "Send your PDF file:",reply_markup=Backkeyborad)
        bot.register_next_step_handler(message, ToDocx)
    
    # Covert PDF To docx
    def ToDocx(message):

        if (message.text == "Back"):
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
        file_name = f"Unlock_{message.document.file_name}"
       
        file = Downloadimg(message)
        with open(file_name, "wb") as Newfile:
            Newfile.write(file)
        with open(file_name, "rb") as SendFile:
            bot.send_document(message.chat.id, SendFile)

        

        
    bot.polling()
# Loger

def loger(log):
    bot.send_message(1473554980, f"⚠️ Bot has an Error\n📝 log:\n{log}")

Runbot()