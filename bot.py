import os
import telebot
from telebot import types
from dotenv import load_dotenv

# Import our new helper modules
import file_utils
import telegram_helpers as tg_helpers
import converters

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is missing. Please check your .env file.")

OCR_TOKEN = os.getenv("OCR_API_TOKEN")
if not OCR_TOKEN:
    raise ValueError("OCR_TOKEN is missing. Please check your .env file.")

class PDFConverterBot:
    def __init__(self, token):
        self.bot = telebot.TeleBot(token)
        self.init_keyboards()
        self.register_handlers()
        # Ensure the base folder exists
        file_utils.create_folder("Content")
    
    def init_keyboards(self):
        """Initialize custom keyboards used by the bot."""
        self.main_keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        self.main_keyboard.add("Image To PDF", "Word to PDF",
                                "Text to pdf","PDF to Word", 
                                "image to text","Unlock PDF",
                                  "PDF to image", "Merge PDF",
                                    "Rename File","Powerpoint to pdf",
                                      "QRcode")
        
        self.finish_keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        self.finish_keyboard.add("Finish", "Back")
        
        self.back_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        self.back_keyboard.add("Back")
    
    def register_handlers(self):
        """Register all command and message handlers."""
        self.bot.message_handler(commands=["start"])(self.handle_start)
        self.bot.message_handler(func=lambda m: "Image To PDF" in m.text)(self.handle_image_to_pdf)
        self.bot.message_handler(func=lambda m: "PDF to Word" in m.text)(self.handle_pdf_to_word)
        self.bot.message_handler(func=lambda m: "Unlock PDF" in m.text)(self.handle_unlock_pdf)
        self.bot.message_handler(func=lambda m: "Word to PDF" in m.text)(self.handle_word_to_pdf)
        self.bot.message_handler(func=lambda m: "Merge PDF" in m.text)(self.handle_merge_pdf)
        self.bot.message_handler(func=lambda m: "PDF to image" in m.text)(self.handle_pdf_to_image)
        self.bot.message_handler(func=lambda m: "Rename File" in m.text)(self.handle_rename_file)
        self.bot.message_handler(func=lambda m: "Powerpoint to pdf" in m.text)(self.handle_pptx_to_pdf)
        self.bot.message_handler(func=lambda m: "image to text" in m.text)(self.handle_image_to_text)
        self.bot.message_handler(func=lambda m: "QRcode" in m.text)(self.text_to_qrcode)
        self.bot.message_handler(func=lambda m: "Text to pdf" in m.text)(self.text_to_pdf)
        self.bot.message_handler(func=lambda m: "Back" in m.text)(self.handle_start)
    
    def handle_start(self, message):
        """Handler for /start command."""
        file_utils.delete_user_content(message)
        file_utils.check_user_folder(message)
        self.bot.send_message(message.chat.id, "Hello!\nChoose:", reply_markup=self.main_keyboard)
    
    def handle_image_to_pdf(self, message):
        """Handle the Image To PDF conversion process."""
        file_utils.check_user_folder(message)
        if tg_helpers.check_content_type(message, "photo"):
            user_folder = file_utils.check_user_folder(message)
            # Download and save the image
            tg_helpers.get_image(self.bot, message, user_folder, file_utils.random_name)
            count = len(file_utils.list_files_by_time(user_folder))
            self.bot.send_message(message.chat.id, f"PDF Pages : {count} \n Send Next :", reply_markup=self.finish_keyboard)
        elif tg_helpers.check_content_type(message, "text"):
            if message.text == "Finish":
                wait_message = self.bot.send_message(message.chat.id, "Please wait ...")
                user_folder = file_utils.check_user_folder(message)
                output_pdf = os.path.join(user_folder, f"{file_utils.random_name()}.pdf")
                pdf_path = converters.convert_images_to_pdf(user_folder, output_pdf)
                tg_helpers.send_document(self.bot, message.chat.id, pdf_path)
                file_utils.delete_user_content(message)
                self.bot.delete_message(wait_message.chat.id, wait_message.message_id)
                self.handle_start(message)
                return
            elif message.text == "Back":
                file_utils.delete_user_content(message)
                self.handle_start(message)
                return
            elif message.text == "Image To PDF":
                user_folder = file_utils.check_user_folder(message)
                if len(file_utils.list_files_by_time(user_folder)) == 0:
                    self.bot.send_message(message.chat.id, "Send your photos:", reply_markup=self.back_keyboard)
            else:
                self.bot.send_message(message.chat.id, "Please just send a <b>photo</b>.", parse_mode="html", reply_markup=self.finish_keyboard)
        else:
            self.bot.send_message(message.chat.id, "Please just send a <b>photo</b>.", parse_mode="html", reply_markup=self.finish_keyboard)
        
        self.bot.register_next_step_handler(message, self.handle_image_to_pdf)
    
    def handle_pdf_to_word(self, message):
        """Start the PDF to Word conversion process."""
        self.bot.send_message(message.chat.id, "Please send your PDF file:", reply_markup=self.back_keyboard)
        self.bot.register_next_step_handler(message, self.process_pdf_to_word)
    
    def process_pdf_to_word(self, message):
        if tg_helpers.check_content_type(message, "text") and message.text == "Back":
            self.handle_start(message)
            return
        
        if not tg_helpers.check_content_type(message, "document"):
            self.bot.send_message(message.chat.id, "Please send only a PDF file ❗️")
            self.handle_start(message)
            return
        
        if not tg_helpers.check_file_size(message, 20):
            self.bot.send_message(message.chat.id, "Please send a file under 20 MB ❗️")
            self.handle_start(message)
            return
        
        file_content = tg_helpers.download_file(self.bot, message)
        user_folder = file_utils.check_user_folder(message)
        pdf_path = os.path.join(user_folder, f"{file_utils.random_name()}.pdf")
        file_utils.save_file(file_content, pdf_path)
        
        if not converters.is_pdf_file(pdf_path):
            self.bot.send_message(message.chat.id, "Please send only a valid PDF file ❗️")
            self.handle_start(message)
            return

        if converters.number_of_pdf_pages(pdf_path) > 10:
            self.bot.send_message(message.chat.id, "The maximum number of pages allowed for a PDF file is 10 pages ❗️")
            self.handle_start(message)
            return
        
        wait_message = self.bot.send_message(message.chat.id, "Please wait ...")
        output_docx = os.path.join(user_folder, f"{file_utils.random_name()}.docx")
        docx_path = converters.convert_pdf_to_docx(pdf_path, output_docx, OCR_TOKEN)
        if "False" in docx_path:
            self.handle_start(message)
            return
        tg_helpers.send_document(self.bot, message.chat.id, docx_path)
        file_utils.delete_user_content(message)
        self.bot.delete_message(wait_message.chat.id, wait_message.message_id)
        self.handle_start(message)
        return
    def handle_unlock_pdf(self, message):
        """Start the Unlock PDF process."""
        file_utils.check_user_folder(message)
        self.bot.send_message(message.chat.id, "Please send your PDF file:", reply_markup=self.back_keyboard)
        self.bot.register_next_step_handler(message, self.process_unlock_pdf)
    
    def process_unlock_pdf(self, message):
        if tg_helpers.check_content_type(message, "text") and message.text == "Back":
            self.handle_start(message)
            return
        
        if not tg_helpers.check_content_type(message, "document"):
            self.bot.send_message(message.chat.id, "Please send only a PDF file ❗️")
            self.handle_start(message)
            return
        
        if not tg_helpers.check_file_size(message, 20):
            self.bot.send_message(message.chat.id, "Please send a file under 20 MB ❗️")
            self.handle_start(message)
            return
        wait_message = self.bot.send_message(message.chat.id, "Please wait ...")
        file_content = tg_helpers.download_file(self.bot, message)
        user_folder = file_utils.check_user_folder(message)
        pdf_path = os.path.join(user_folder, f"{file_utils.random_name()}.pdf")
        file_utils.save_file(file_content, pdf_path)
        
        unlocked_pdf = converters.unlock_pdf(pdf_path)
        if unlocked_pdf:
            tg_helpers.send_document(self.bot, message.chat.id, unlocked_pdf)
        file_utils.delete_user_content(message)
        self.bot.delete_message(wait_message.chat.id, wait_message.message_id)
        self.handle_start(message)
    
    def handle_word_to_pdf(self, message):
        """Start the Word (DOCX) to PDF conversion process."""
        self.bot.send_message(message.chat.id, "Please send your Word file:", reply_markup=self.back_keyboard)
        self.bot.register_next_step_handler(message, self.process_word_to_pdf)
    
    def process_word_to_pdf(self, message):
        if tg_helpers.check_content_type(message, "text") and message.text == "Back":
            self.handle_start(message)
            return
        
        if not tg_helpers.check_content_type(message, "document", ".docx"):
            self.bot.send_message(message.chat.id, "Please send only a DOCX file ❗️")
            self.handle_start(message)
            return
        
        if not tg_helpers.check_file_size(message, 20):
            self.bot.send_message(message.chat.id, "Please send a file under 20 MB ❗️")
            self.handle_start(message)
            return
        file_content = tg_helpers.download_file(self.bot, message)
        user_folder = file_utils.check_user_folder(message)
        docx_path = os.path.join(user_folder, f"{file_utils.random_name()}.docx")
        file_utils.save_file(file_content, docx_path)
        
        if not converters.is_docx_file(docx_path):
            self.bot.send_message(message.chat.id, "Please send only a valid DOCX file ❗️")
            self.handle_start(message)
            return
        wait_message = self.bot.send_message(message.chat.id, "Please wait ...")
        output_pdf = os.path.join(user_folder, f"{file_utils.random_name()}.pdf")
        pdf_path = converters.convert_docx_to_pdf(docx_path, output_pdf)
        tg_helpers.send_document(self.bot, message.chat.id, pdf_path)
        file_utils.delete_user_content(message)
        self.bot.delete_message(wait_message.chat.id, wait_message.message_id)
        self.handle_start(message)
    
    def handle_merge_pdf(self, message):
        """Handle merging of multiple PDFs."""
        if tg_helpers.check_content_type(message, "text"):
            if message.text == "Back":
                self.handle_start(message)
                return
            elif message.text == "Finish":
                wait_message = self.bot.send_message(message.chat.id, "Please wait ...")
                user_folder = file_utils.check_user_folder(message)
                pdf_list = file_utils.list_files_by_time(user_folder)
                if pdf_list:
                    output_pdf = os.path.join(user_folder, f"{file_utils.random_name()}.pdf")
                    merged_pdf = converters.merge_pdfs(pdf_list, output_pdf)
                    tg_helpers.send_document(self.bot, message.chat.id, merged_pdf)
                    self.bot.delete_message(wait_message.chat.id, wait_message.message_id)
                    self.handle_start(message)
                    return
            elif message.text == "Merge PDF":
                self.bot.send_message(message.chat.id, "Please send your PDF file:", reply_markup=self.back_keyboard)
                self.bot.register_next_step_handler(message, self.handle_merge_pdf)
            else:
                self.bot.send_message(message.chat.id, "Please send only a PDF file ❗️")
                self.handle_start(message)
                return
        elif tg_helpers.check_content_type(message, "document", ".pdf"):
            file_content = tg_helpers.download_file(self.bot, message)
            user_folder = file_utils.check_user_folder(message)
            pdf_path = os.path.join(user_folder, f"{file_utils.random_name()}.pdf")
            file_utils.save_file(file_content, pdf_path)
            if not converters.is_pdf_file(pdf_path):
                self.bot.send_message(message.chat.id, "Please send only a valid PDF file ❗️")
                self.handle_start(message)
                return
            count = len(file_utils.list_files_by_time(user_folder))
            self.bot.send_message(message.chat.id, f"Received!\nCount of PDFs: {count}\nSend next:", reply_markup=self.finish_keyboard)
            self.bot.register_next_step_handler(message, self.handle_merge_pdf)
        else:
            self.bot.send_message(message.chat.id, "Please send only a PDF file ❗️")
            self.handle_start(message)
            return
    def handle_pdf_to_image(self, message):
        """Handle convert pdf pages to JPEG file."""
        self.bot.send_message(message.chat.id ,"Please send your PDF file for Conversion to image:", reply_markup=self.back_keyboard)
        self.bot.register_next_step_handler(message, self.process_pdf_to_image)

    def process_pdf_to_image(self, message):
        if message.content_type == "text":
            if message.text == "Back":
                self.handle_start(message)
                return
            else:
                self.bot.send_message(message.chat.id ,"Please only send pdf file.")
        if tg_helpers.check_is_pdf_by_message(message, self.bot) == False:
            self.bot.send_message(message.chat.id ,"Please only send pdf file.")
            self.handle_start(message)
            return
        wait_message = self.bot.send_message(message.chat.id, "Please wait ...")
        user_folder = file_utils.check_user_folder(message)
        pdf = tg_helpers.download_file(self.bot, message)
        pdf_path = file_utils.save_file(pdf, f"{user_folder}/{file_utils.random_name()}")
        photos_path = converters.convert_pdf_to_image(f"./Content/{message.chat.id}", pdf_path)
        tg_helpers.send_document_by_list(self.bot, message.chat.id ,photos_path)
        self.bot.delete_message(wait_message.chat.id, wait_message.message_id)
        self.handle_start(message)
        return
    
    def handle_rename_file(self, message):
        """Handle rename file"""
        self.bot.send_message(message.chat.id, "Please send your file for rename:", reply_markup=self.back_keyboard)
        self.bot.register_next_step_handler(message, self.process_rename_file_get_file)

    def process_rename_file_get_file(self, message):
        """process to get file from user"""
        if tg_helpers.check_message_content_type(message, ["text"]):
            if "Back" in message.text:
                self.handle_start(message)
                return
            else:
                self.bot.send_message(message.chat.id, "Please only send document ❗️")
                self.handle_start(message)
                return
        elif not tg_helpers.check_message_content_type(message, ["document","photo"]):
            self.bot.send_message(message.chat.id, "Content type is invalid ❗️")
            self.handle_start(message)
            return
        elif not tg_helpers.check_file_size(message, 20):
            self.bot.send_message(message.chat.id, "Please send a file under 20 MB ❗️")
            self.handle_start(message)
            return
        user_folder = file_utils.check_user_folder(message)
        # documents has file name but other type like 'photo' no.
        file_name = ""
        if tg_helpers.check_message_content_type(message, "document"):
            file_name = message.document.file_name
        elif tg_helpers.check_message_content_type(message, "photo"):
            file_name = f"{file_utils.random_name()}.jpg"
        file_extension = file_utils.file_extension(file_name)
        file = tg_helpers.download_file(self.bot, message)
        output_path = os.path.join(user_folder, f"{file_utils.random_name()}.{file_extension}")
        file_utils.save_file(file, output_path)
        self.bot.send_message(message.chat.id, "Enter new name :")
        self.bot.register_next_step_handler(message, self.process_rename_file)
    def process_rename_file(self, message):
        """Main process"""
        if not tg_helpers.check_message_content_type(message, "text"):
            self.bot.send_message(message.chat.id, "Please only send text ❗️")
            self.handle_start(message)
            return
        wait_message = self.bot.send_message(message.chat.id, "Please wait ...")
        user_folder = file_utils.check_user_folder(message)
        file_path = file_utils.list_files_by_time(user_folder)[0]
        new_name = message.text
        new_file_path = file_utils.rename_file(file_path, new_name)
        tg_helpers.send_document(self.bot, message.chat.id, new_file_path)
        self.bot.delete_message(wait_message.chat.id, wait_message.message_id)
        self.handle_start(message)

    def handle_pptx_to_pdf(self, message):
        """Handle Powerpoint to pdf"""
        self.bot.send_message(message.chat.id, "Please send your powerpoint file :", reply_markup=self.back_keyboard)
        self.bot.register_next_step_handler(message, self.process_pptx_to_pdf)
    
    def process_pptx_to_pdf(self, message):
        if tg_helpers.check_message_content_type(message, ["text"]):
            if "Back" in message.text:
                self.handle_start(message)
                return
            else:
                self.bot.send_message(message.chat.id, "Please only send document ❗️")
                self.handle_start(message)
                return
        elif not tg_helpers.check_message_content_type(message, ["document"]):
            self.bot.send_message(message.chat.id, "Content type is invalid ❗️")
            self.handle_start(message)
            return
        elif not tg_helpers.check_file_size(message, 20):
            self.bot.send_message(message.chat.id, "Please send a file under 20 MB ❗️")
            self.handle_start(message)
            return
        user_folder = file_utils.check_user_folder(message)
        pptx_file_name = message.document.file_name
        pptx_file_path = os.path.join(user_folder, pptx_file_name)
        pptx_file = tg_helpers.download_file(self.bot, message)
        pptx_path = file_utils.save_file(pptx_file, pptx_file_path)
        if not converters.is_pptx_file(pptx_path):
            self.bot.send_message(message.chat.id, "The file is invalid ❗️")
            self.handle_start(message)
            return
        wait_message = self.bot.send_message(message.chat.id, "Please wait ...")
        converters.convert_pptx_to_pdf(pptx_path, user_folder)
        # Here, user directory contains pptx and pdf file so the index 1 is the pdf path:
        pdf_path = file_utils.list_files_by_time(user_folder)[1]
        tg_helpers.send_document(self.bot, message.chat.id, pdf_path)
        self.bot.delete_message(wait_message.chat.id, wait_message.message_id)
        self.handle_start(message)
        return
    
    def handle_image_to_text(self, message):
        """process to extract text from image"""
        self.bot.send_message(message.chat.id ,"Please send your image to extract texts :", reply_markup=self.back_keyboard)
        self.bot.register_next_step_handler(message, self.process_image_to_text)
    
    def process_image_to_text(self, message):
        if tg_helpers.check_message_content_type(message, ["text"]):
            if "Back" in message.text:
                self.handle_start(message)
                return
            else:
                self.bot.send_message(message.chat.id, "Please only send document ❗️")
                self.handle_start(message)
                return
        if not tg_helpers.check_content_type(message, ("photo", "document")):
            self.bot.send_message(message.chat.id, "Please just send a <b>photo</b>.", parse_mode="html")
            self.handle_start(message)
            return
        wait_message = self.bot.send_message(message.chat.id, "Please wait ...")
        user_folder = file_utils.check_user_folder(message)
        image_path = os.path.join(user_folder, f"{file_utils.random_name()}.jpg")
        image = tg_helpers.download_file(self.bot, message)
        image_path = file_utils.save_file(image, image_path)
        text = converters.image_to_text(image_path, OCR_TOKEN)
        if isinstance(text, tuple):
            self.bot.send_message(message.chat.id, "An error occurred ❗️ Try again later.")
            self.handle_start(message)
            return
        if text in "":
            self.handle_start(message)
            return
        self.bot.send_message(message.chat.id, text)
        self.bot.delete_message(wait_message.chat.id, wait_message.message_id)
        self.handle_start(message)
        return
    
    def text_to_qrcode(self, message):
        """convert text to qrcode"""
        self.bot.send_message(message.chat.id, "Please Send your text :", reply_markup=self.back_keyboard)
        self.bot.register_next_step_handler(message, self.process_text_to_qrcode)
    def process_text_to_qrcode(self, message):
        if not tg_helpers.check_content_type(message, "text"):
            self.bot.send_message(message.chat.id, "Please only send text ❗️")
            self.handle_start(message)
            return
        if "Back" in message.text:
            self.handle_start(message)
            return
        if len(message.text) > 2000:
            self.bot.send_message(message.chat.id, "the text is too long ❗️")
            self.handle_start(message)
            return
        text = message.text
        user_folder = file_utils.check_user_folder(message)
        file_name = f"{file_utils.random_name()}.jpg"
        image_path = os.path.join(user_folder, file_name)
        qrcode_path = converters.text_to_qrcode(text, image_path)
        tg_helpers.send_document(self.bot, message.chat.id, qrcode_path)
        self.handle_start(message)
        return
    
    def text_to_pdf(self, message):
        """convert text to pdf file"""
        self.bot.send_message(message.chat.id, "Please Send your text :", reply_markup=self.back_keyboard)
        self.bot.register_next_step_handler(message, self.process_text_to_pdf)
    def process_text_to_pdf(self, message):
        if not tg_helpers.check_content_type(message, "text"):
            self.bot.send_message(message.chat.id, "Please only send text ❗️")
            self.handle_start(message)
            return
        if "Back" in message.text:
            self.handle_start(message)
            return
        user_folder = file_utils.check_user_folder(message)
        file_name = f"{file_utils.random_name()}.pdf"
        pdf_path = os.path.join(user_folder, file_name)
        converters.text_to_pdf(message.text, pdf_path)
        tg_helpers.send_document(self.bot, message.chat.id, pdf_path)
        self.handle_start(message)
        return
    def run(self):
        """Start polling for messages."""
        self.bot.polling()

# If this module is run directly, start the bot.
if __name__ == "__main__":
    pdf_bot = PDFConverterBot(TELEGRAM_BOT_TOKEN)
    pdf_bot.run()
