from bot import Runbot , loger

while(True):
    try:
        Runbot()
    except KeyboardInterrupt:
        break
    except Exception as log:
        loger(log)
