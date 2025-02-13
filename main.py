import os
import logging
from dotenv import load_dotenv
from bot import PDFConverterBot


def main():
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN is missing. Please check your .env file.")

    pdf_bot = PDFConverterBot(token)
    try:
        pdf_bot.run()
    except Exception as e:
        logging.exception("An error occurred during bot operation")


if __name__ == "__main__":
    main()
