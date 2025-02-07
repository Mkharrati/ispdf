from bot import Runbot, loger

while (True):
    try:
        Runbot()
    except Exception as log:
        print(log)
        try:
            loger(log)
        except:
            pass

