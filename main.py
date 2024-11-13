import pdfTodocx
import bot

Token = "7901016275:AAHdtR2oWFkBoRivuv3x21lnhZvYv66UgZw"
while (True):
    try:
        bot.bot(Token)
    except Exception as log:
        bot.loger(Token, log)