import os
import telebot
from telebot import types
from dotenv import load_dotenv

# Import our new helper modules
import file_utils
import messages.messages
import telegram_helpers as tg_helpers
import converters
import messages

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is missing. Please check your .env file.")

OCR_TOKEN = os.getenv("OCR_API_TOKEN")
if not OCR_TOKEN:
    raise ValueError("OCR_TOKEN is missing. Please check your .env file.")

Messages = messages.messages.EnglishMessages

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
        self.main_keyboard.add(
            Messages._IMAGE_PDF, Messages._WORD_PDF,
            Messages._TEXT_PDF, Messages._PDF_WORD,
            Messages._IMAGE_TEXT, Messages._UNLOCK_PDF,
            Messages._PDF_IMAGE, Messages._MERGE_PDF,
            Messages._RENAME_FILE, Messages._PPT_PDF,
            Messages._QRCODE
        )
        
        self.finish_keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        self.finish_keyboard.add(Messages._FINISH, Messages._BACK)
        
        self.back_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        self.back_keyboard.add(Messages._BACK)
    
    def register_handlers(self):
        """Register all command and message handlers."""
        self.bot.message_handler(func=lambda m: Messages._IMAGE_PDF in m.text)(self.handle_image_to_pdf)
        self.bot.message_handler(func=lambda m: Messages._PDF_WORD in m.text)(self.handle_pdf_to_word)
        self.bot.message_handler(func=lambda m: Messages._UNLOCK_PDF in m.text)(self.handle_unlock_pdf)
        self.bot.message_handler(func=lambda m: Messages._WORD_PDF in m.text)(self.handle_word_to_pdf)
        self.bot.message_handler(func=lambda m: Messages._MERGE_PDF in m.text)(self.handle_merge_pdf)
        self.bot.message_handler(func=lambda m: Messages._PDF_IMAGE in m.text)(self.handle_pdf_to_image)
        self.bot.message_handler(func=lambda m: Messages._RENAME_FILE in m.text)(self.handle_rename_file)
        self.bot.message_handler(func=lambda m: Messages._PPT_PDF in m.text)(self.handle_pptx_to_pdf)
        self.bot.message_handler(func=lambda m: Messages._IMAGE_TEXT in m.text)(self.handle_image_to_text)
        self.bot.message_handler(func=lambda m: Messages._QRCODE in m.text)(self.text_to_qrcode)
        self.bot.message_handler(func=lambda m: Messages._TEXT_PDF in m.text)(self.text_to_pdf)
        self.bot.message_handler(func=lambda m: Messages._BACK in m.text)(self.handle_start)
    
    def handle_start(self, message):
        """Handler for /start command."""
        file_utils.delete_user_content(message)
        file_utils.check_user_folder(message)
        self.bot.send_message(message.chat.id, Messages.START, reply_markup=self.main_keyboard)
    
    def handle_image_to_pdf(self, message):
        """Handle the Image To PDF conversion process."""
        file_utils.check_user_folder(message)
        if tg_helpers.check_content_type(message, "photo"):
            user_folder = file_utils.check_user_folder(message)
            # Download and save the image
            tg_helpers.get_image(self.bot, message, user_folder, file_utils.random_name)
            count = len(file_utils.list_files_by_time(user_folder))
            self.bot.send_message(message.chat.id, Messages.PDF_COUNT(count), reply_markup=self.finish_keyboard)
        elif tg_helpers.check_content_type(message, "text"):
            if message.text == "Finish":
                wait_message = self.bot.send_message(message.chat.id, Messages.PLEASE_WAIT)
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
                    self.bot.send_message(message.chat.id, Messages.REQ_PHOTO, reply_markup=self.back_keyboard)
            else:
                self.bot.send_message(message.chat.id, Messages.PHOTO_ONLY, parse_mode="html", reply_markup=self.finish_keyboard)
        else:
            self.bot.send_message(message.chat.id, Messages.PHOTO_ONLY, parse_mode="html", reply_markup=self.finish_keyboard)
        
        self.bot.register_next_step_handler(message, self.handle_image_to_pdf)
    
    def handle_pdf_to_word(self, message):
        """Start the PDF to Word conversion process."""
        self.bot.send_message(message.chat.id, Messages.REQ_PDF ,reply_markup=self.back_keyboard)
        self.bot.register_next_step_handler(message, self.process_pdf_to_word)
    
    def process_pdf_to_word(self, message):
        if tg_helpers.check_content_type(message, "text") and message.text == "Back":
            self.handle_start(message)
            return
        
        if not tg_helpers.check_content_type(message, "document"):
            self.bot.send_message(message.chat.id, Messages.PDF_ONLY)
            self.handle_start(message)
            return
        
        if not tg_helpers.check_file_size(message, 20):
            self.bot.send_message(message.chat.id, Messages.FILE_SIZE_ERROR_20MB)
            self.handle_start(message)
            return
        
        file_content = tg_helpers.download_file(self.bot, message)
        user_folder = file_utils.check_user_folder(message)
        pdf_path = os.path.join(user_folder, f"{file_utils.random_name()}.pdf")
        file_utils.save_file(file_content, pdf_path)
        
        if not converters.is_pdf_file(pdf_path):
            self.bot.send_message(message.chat.id, Messages.INVALID_PDF)
            self.handle_start(message)
            return

        if converters.number_of_pdf_pages(pdf_path) > 10:
            self.bot.send_message(message.chat.id, Messages.MAX_PAGE_ERROR_10)
            self.handle_start(message)
            return
        
        wait_message = self.bot.send_message(message.chat.id, Messages.PLEASE_WAIT)
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
        self.bot.send_message(message.chat.id, Messages.REQ_PHOTO, reply_markup=self.back_keyboard)
        self.bot.register_next_step_handler(message, self.process_unlock_pdf)
    
    def process_unlock_pdf(self, message):
        if tg_helpers.check_content_type(message, "text") and message.text == "Back":
            self.handle_start(message)
            return
        
        if not tg_helpers.check_content_type(message, "document"):
            self.bot.send_message(message.chat.id, Messages.PDF_ONLY)
            self.handle_start(message)
            return
        
        if not tg_helpers.check_file_size(message, 20):
            self.bot.send_message(message.chat.id, Messages.FILE_SIZE_ERROR_20MB)
            self.handle_start(message)
            return
        wait_message = self.bot.send_message(message.chat.id, Messages.PLEASE_WAIT)
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
        self.bot.send_message(message.chat.id, Messages.REQ_WORD, reply_markup=self.back_keyboard)
        self.bot.register_next_step_handler(message, self.process_word_to_pdf)
    
    def process_word_to_pdf(self, message):
        if tg_helpers.check_content_type(message, "text") and message.text == "Back":
            self.handle_start(message)
            return
        
        if not tg_helpers.check_content_type(message, "document", ".docx"):
            self.bot.send_message(message.chat.id, Messages.WORD_ONLY)
            self.handle_start(message)
            return
        
        if not tg_helpers.check_file_size(message, 20):
            self.bot.send_message(message.chat.id, Messages.FILE_SIZE_ERROR_20MB)
            self.handle_start(message)
            return
        file_content = tg_helpers.download_file(self.bot, message)
        user_folder = file_utils.check_user_folder(message)
        docx_path = os.path.join(user_folder, f"{file_utils.random_name()}.docx")
        file_utils.save_file(file_content, docx_path)
        
        if not converters.is_docx_file(docx_path):
            self.bot.send_message(message.chat.id, Messages.WORD_ONLY)
            self.handle_start(message)
            return
        wait_message = self.bot.send_message(message.chat.id, Messages.PLEASE_WAIT)
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
                wait_message = self.bot.send_message(message.chat.id, Messages.PLEASE_WAIT)
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
                self.bot.send_message(message.chat.id, Messages.REQ_PDF, reply_markup=self.back_keyboard)
                self.bot.register_next_step_handler(message, self.handle_merge_pdf)
            else:
                self.bot.send_message(message.chat.id, Messages.PDF_ONLY)
                self.handle_start(message)
                return
        elif tg_helpers.check_content_type(message, "document", ".pdf"):
            file_content = tg_helpers.download_file(self.bot, message)
            user_folder = file_utils.check_user_folder(message)
            pdf_path = os.path.join(user_folder, f"{file_utils.random_name()}.pdf")
            file_utils.save_file(file_content, pdf_path)
            if not converters.is_pdf_file(pdf_path):
                self.bot.send_message(message.chat.id, Messages.INVALID_PDF)
                self.handle_start(message)
                return
            count = len(file_utils.list_files_by_time(user_folder))
            self.bot.send_message(message.chat.id, Messages.MERG_PDF_COUNT(count), reply_markup=self.finish_keyboard)
            self.bot.register_next_step_handler(message, self.handle_merge_pdf)
        else:
            self.bot.send_message(message.chat.id, Messages.PDF_ONLY)
            self.handle_start(message)
            return
    def handle_pdf_to_image(self, message):
        """Handle convert pdf pages to JPEG file."""
        self.bot.send_message(message.chat.id , Messages.REQ_PDF, reply_markup=self.back_keyboard)
        self.bot.register_next_step_handler(message, self.process_pdf_to_image)

    def process_pdf_to_image(self, message):
        if message.content_type == "text":
            if message.text == "Back":
                self.handle_start(message)
                return
            else:
                self.bot.send_message(message.chat.id ,Messages.PDF_ONLY)
        if tg_helpers.check_is_pdf_by_message(message, self.bot) == False:
            self.bot.send_message(message.chat.id , Messages.PDF_ONLY)
            self.handle_start(message)
            return
        wait_message = self.bot.send_message(message.chat.id, Messages.PLEASE_WAIT)
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
        self.bot.send_message(message.chat.id, Messages.REQ_FILE, reply_markup=self.back_keyboard)
        self.bot.register_next_step_handler(message, self.process_rename_file_get_file)

    def process_rename_file_get_file(self, message):
        """process to get file from user"""
        if tg_helpers.check_message_content_type(message, ["text"]):
            if "Back" in message.text:
                self.handle_start(message)
                return
            else:
                self.bot.send_message(message.chat.id, Messages.DOC_ONLY)
                self.handle_start(message)
                return
        elif not tg_helpers.check_message_content_type(message, ["document","photo"]):
            self.bot.send_message(message.chat.id, Messages.INVALID_CONTENT)
            self.handle_start(message)
            return
        elif not tg_helpers.check_file_size(message, 20):
            self.bot.send_message(message.chat.id, Messages.FILE_SIZE_ERROR_20MB)
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
        self.bot.send_message(message.chat.id, Messages.REQ_NEWNAME)
        self.bot.register_next_step_handler(message, self.process_rename_file)
    def process_rename_file(self, message):
        """Main process"""
        if not tg_helpers.check_message_content_type(message, "text"):
            self.bot.send_message(message.chat.id, Messages.TEXT_ONLY)
            self.handle_start(message)
            return
        wait_message = self.bot.send_message(message.chat.id, Messages.PLEASE_WAIT)
        user_folder = file_utils.check_user_folder(message)
        file_path = file_utils.list_files_by_time(user_folder)[0]
        new_name = message.text
        new_file_path = file_utils.rename_file(file_path, new_name)
        tg_helpers.send_document(self.bot, message.chat.id, new_file_path)
        self.bot.delete_message(wait_message.chat.id, wait_message.message_id)
        self.handle_start(message)

    def handle_pptx_to_pdf(self, message):
        """Handle Powerpoint to pdf"""
        self.bot.send_message(message.chat.id, Messages.REQ_PPTX, reply_markup=self.back_keyboard)
        self.bot.register_next_step_handler(message, self.process_pptx_to_pdf)
    
    def process_pptx_to_pdf(self, message):
        if tg_helpers.check_message_content_type(message, ["text"]):
            if "Back" in message.text:
                self.handle_start(message)
                return
            else:
                self.bot.send_message(message.chat.id, Messages.PPTX_ONLY)
                self.handle_start(message)
                return
        elif not tg_helpers.check_message_content_type(message, ["document"]):
            self.bot.send_message(message.chat.id, Messages.INVALID_CONTENT)
            self.handle_start(message)
            return
        elif not tg_helpers.check_file_size(message, 20):
            self.bot.send_message(message.chat.id, Messages.FILE_SIZE_ERROR_20MB)
            self.handle_start(message)
            return
        user_folder = file_utils.check_user_folder(message)
        pptx_file_name = message.document.file_name
        pptx_file_path = os.path.join(user_folder, pptx_file_name)
        pptx_file = tg_helpers.download_file(self.bot, message)
        pptx_path = file_utils.save_file(pptx_file, pptx_file_path)
        if not converters.is_pptx_file(pptx_path):
            self.bot.send_message(message.chat.id, Messages.INVALIDE_FILE)
            self.handle_start(message)
            return
        wait_message = self.bot.send_message(message.chat.id, Messages.PLEASE_WAIT)
        converters.convert_pptx_to_pdf(pptx_path, user_folder)
        # Here, user directory contains pptx and pdf file so the index 1 is the pdf path:
        pdf_path = file_utils.list_files_by_time(user_folder)[1]
        tg_helpers.send_document(self.bot, message.chat.id, pdf_path)
        self.bot.delete_message(wait_message.chat.id, wait_message.message_id)
        self.handle_start(message)
        return
    
    def handle_image_to_text(self, message):
        """process to extract text from image"""
        self.bot.send_message(message.chat.id , Messages.REQ_PHOTO, reply_markup=self.back_keyboard)
        self.bot.register_next_step_handler(message, self.process_image_to_text)
    
    def process_image_to_text(self, message):
        if tg_helpers.check_message_content_type(message, ["text"]):
            if "Back" in message.text:
                self.handle_start(message)
                return
            else:
                self.bot.send_message(message.chat.id, Messages.PHOTO_ONLY)
                self.handle_start(message)
                return
        if not tg_helpers.check_content_type(message, ("photo", "document")):
            self.bot.send_message(message.chat.id, Messages.PHOTO_ONLY, parse_mode="html")
            self.handle_start(message)
            return
        wait_message = self.bot.send_message(message.chat.id, Messages.PLEASE_WAIT)
        user_folder = file_utils.check_user_folder(message)
        image_path = os.path.join(user_folder, f"{file_utils.random_name()}.jpg")
        image = tg_helpers.download_file(self.bot, message)
        image_path = file_utils.save_file(image, image_path)
        text = converters.image_to_text(image_path, OCR_TOKEN)
        if isinstance(text, tuple):
            self.bot.send_message(message.chat.id, Messages.OCCURRED_ERROR)
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
        self.bot.send_message(message.chat.id, Messages.REQ_TEXT, reply_markup=self.back_keyboard)
        self.bot.register_next_step_handler(message, self.process_text_to_qrcode)
    def process_text_to_qrcode(self, message):
        if not tg_helpers.check_content_type(message, "text"):
            self.bot.send_message(message.chat.id, Messages.TEXT_ONLY)
            self.handle_start(message)
            return
        if "Back" in message.text:
            self.handle_start(message)
            return
        if len(message.text) > 1000:
            self.bot.send_message(message.chat.id, Messages.TEXT_TOO_LONG)
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
        self.bot.send_message(message.chat.id, Messages.REQ_TEXT, reply_markup=self.back_keyboard)
        self.bot.register_next_step_handler(message, self.process_text_to_pdf)
    def process_text_to_pdf(self, message):
        if not tg_helpers.check_content_type(message, "text"):
            self.bot.send_message(message.chat.id, Messages.TEXT_ONLY)
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
