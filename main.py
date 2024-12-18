import tools
import bot

Token = "7901016275:AAF0gv9Q3K3XuypYnFmSbWze8dHOck3SDXg"
while (True):
    try:
        bot.bot(Token)
    except Exception as log:
        print(log)
        try:
            bot.loger(Token, log)
        except:
            pass


