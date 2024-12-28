import tools
import bot

Token = "7490729977:AAFBlIJp8DeVfkusr4oMptP_bye_ZsxsrDY"
while (True):
    try:
        bot.bot(Token)
    except Exception as log:
        print(log)
        try:
            bot.loger(Token, log)
        except:
            pass


