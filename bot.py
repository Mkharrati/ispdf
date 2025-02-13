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
        self.main_keyboard.add("PDF to Word", "Image To PDF", "Word to PDF", "Unlock PDF", "Merge PDF")
        
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
    
    def handle_start(self, message):
        """Handler for /start command."""
        file_utils.delete_user_content(message)
        file_utils.check_user_folder(message)
        self.bot.send_message(message.chat.id, "Hello!\nChoose:", reply_markup=self.main_keyboard)
    
    def handle_image_to_pdf(self, message):
        """Handle the Image To PDF conversion process."""
        file_utils.check_user_folder(message)
        content_type = tg_helpers.get_message_content_type(message)
        if content_type == "photo":
            user_folder = file_utils.check_user_folder(message)
            # Download and save the image
            tg_helpers.get_image(self.bot, message, user_folder, file_utils.random_name)
            count = len(file_utils.list_files_by_time(user_folder))
            self.bot.send_message(message.chat.id, f"PDF Page: {count}", reply_markup=self.finish_keyboard)
        elif content_type == "text":
            if message.text == "Finish":
                user_folder = file_utils.check_user_folder(message)
                output_pdf = os.path.join(user_folder, f"{file_utils.random_name()}.pdf")
                pdf_path = converters.convert_images_to_pdf(user_folder, output_pdf)
                tg_helpers.send_document(self.bot, message.chat.id, pdf_path)
                file_utils.delete_user_content(message)
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
        
        if not tg_helpers.check_file_size(message, 10000000):
            self.bot.send_message(message.chat.id, "Please send a file under 10 MB ❗️")
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
        
        output_docx = os.path.join(user_folder, f"{file_utils.random_name()}.docx")
        docx_path = converters.convert_pdf_to_docx(pdf_path, output_docx)
        tg_helpers.send_document(self.bot, message.chat.id, docx_path)
        file_utils.delete_user_content(message)
        self.handle_start(message)
    
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
        
        if not tg_helpers.check_file_size(message, 10000000):
            self.bot.send_message(message.chat.id, "Please send a file under 10 MB ❗️")
            self.handle_start(message)
            return
        
        file_content = tg_helpers.download_file(self.bot, message)
        user_folder = file_utils.check_user_folder(message)
        pdf_path = os.path.join(user_folder, f"{file_utils.random_name()}.pdf")
        file_utils.save_file(file_content, pdf_path)
        
        unlocked_pdf = converters.unlock_pdf(pdf_path)
        if unlocked_pdf:
            tg_helpers.send_document(self.bot, message.chat.id, unlocked_pdf)
        file_utils.delete_user_content(message)
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
        
        if not tg_helpers.check_file_size(message, 10000000):
            self.bot.send_message(message.chat.id, "Please send a file under 10 MB ❗️")
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
        
        output_pdf = os.path.join(user_folder, f"{file_utils.random_name()}.pdf")
        pdf_path = converters.convert_docx_to_pdf(docx_path, output_pdf)
        tg_helpers.send_document(self.bot, message.chat.id, pdf_path)
        file_utils.delete_user_content(message)
        self.handle_start(message)
    
    def handle_merge_pdf(self, message):
        """Handle merging of multiple PDFs."""
        content_type = tg_helpers.get_message_content_type(message)
        if content_type == "text":
            if message.text == "Back":
                self.handle_start(message)
                return
            elif message.text == "Finish":
                user_folder = file_utils.check_user_folder(message)
                pdf_list = file_utils.list_files_by_time(user_folder)
                if pdf_list:
                    output_pdf = os.path.join(user_folder, f"{file_utils.random_name()}.pdf")
                    merged_pdf = converters.merge_pdfs(pdf_list, output_pdf)
                    tg_helpers.send_document(self.bot, message.chat.id, merged_pdf)
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
    
    def run(self):
        """Start polling for messages."""
        self.bot.polling()

# If this module is run directly, start the bot.
if __name__ == "__main__":
    pdf_bot = PDFConverterBot(TELEGRAM_BOT_TOKEN)
    pdf_bot.run()
