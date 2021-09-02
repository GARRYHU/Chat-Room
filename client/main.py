import configure as conf
from LoginWin import *

if __name__ == '__main__':
    gol.init()
    if conf.read() is False:
        pass
    gol.set_value('buffer','')
    gol.set_value('version','1.1')
    login_win = Login_win()
    login_win.show()
