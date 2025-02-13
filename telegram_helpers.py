import telebot

def get_file_id(message):
    """
    Retrieve file id from a message.
    Works for both photo and document messages.
    """
    msg_json = message.json
    if "photo" in msg_json:
        # Return the highest resolution photo id
        return msg_json["photo"][-1]["file_id"]
    elif "document" in msg_json:
        return msg_json["document"]["file_id"]
    else:
        raise ValueError("No valid file found in message.")

def download_file(bot, message):
    """
    Download file from a Telegram message.
    Returns the file content.
    """
    file_id = get_file_id(message)
    file_info = bot.get_file(file_id)
    file_content = bot.download_file(file_info.file_path)
    return file_content

def send_document(bot, chat_id, file_path):
    """Send a document to a chat."""
    with open(file_path, "rb") as f:
        bot.send_document(chat_id, f)

def check_content_type(message, expected_type, extension=""):
    """
    Check if the message has the expected content type and, if a file, optionally the correct extension.
    """
    if message.content_type != expected_type:
        return False
    if extension and hasattr(message, "document"):
        return message.document.file_name.endswith(extension)
    return True

def check_file_size(message, size_limit):
    """
    Check if the file in the message is under size_limit (in bytes).
    """
    if message.content_type == "document":
        return message.document.file_size <= size_limit
    elif message.content_type == "photo":
        # Telegram sends photos as a list; check the largest size.
        return message.photo[-1].file_size <= size_limit
    return False

def get_message_content_type(message):
    """Return the content type of the message."""
    return message.content_type

def get_image(bot, message, user_folder, random_name_func):
    """
    Download an image from a message and save it to the user's folder.
    Returns the saved file path.
    """
    file_content = download_file(bot, message)
    file_name = f"{random_name_func()}.jpg"
    file_path = f"{user_folder}/{file_name}"
    with open(file_path, "wb") as f:
        f.write(file_content)
    return file_path

class MessageDetails:
    """
    Helper class to extract details from a Telegram message.
    """
    def __init__(self, message):
        self.message = message

    def file_id(self):
        return get_file_id(self.message)
