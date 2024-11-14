import tools
import bot

Token = "7278448230:AAGlXRBFOLDm_BpNYziML36zypKZWc5soCQ"
while (True):
    try:
        bot.bot(Token)
    except Exception as log:
        print(log)
        try:
            bot.loger(Token, log)
        except:
            pass

