from Pack import *
from tkinter import *
import globalvar as gol
import GroupWin
from sock import *

class Login_win:
    def show(self):
        self.win.mainloop()

    def close(self):
        self.win.destroy()

    def __init__(self):
        self.win = Tk()
        self.user = StringVar()
        self.user.set(gol.get_value('id'))
        self.pwd = StringVar()
        self.pwd.set(gol.get_value('pwd'))

        self.win.geometry("320x240")
        self.win.title("登录")
        self.win.resizable(width=False, height=False)

        self.label1 = Label(self.win)
        self.label1.place(relx=0.055, rely=0.1, height=31, width=89)
        self.label1.configure(text='账号')

        self.entry_user = Entry(self.win)
        self.entry_user.place(relx=0.28, rely=0.11, height=26, relwidth=0.554)
        self.entry_user.configure(textvariable=self.user)

        self.label2 = Label(self.win)
        self.label2.place(relx=0.055, rely=0.27, height=31, width=89)
        self.label2.configure(text='密码')

        self.entry_pwd = Entry(self.win)
        self.entry_pwd.place(relx=0.28, rely=0.28, height=26, relwidth=0.554)
        self.entry_pwd.configure(textvariable=self.pwd)

        self.btn_login = Button(self.win)
        self.btn_login.place(relx=0.13, rely=0.6, height=32, width=88)
        self.btn_login.configure(text='登录')

        self.btn_reg = Button(self.win)
        self.btn_reg.place(relx=0.6, rely=0.6, height=32, width=88)
        self.btn_reg.configure(text='注册')

        self.login_flag_con=StringVar()
        self.login_flag = Label(self.win, textvariable=self.login_flag_con, fg='red', font=('宋体', 11))
        self.login_flag_con.set('请登录或注册')
        self.login_flag.place(relx=0.3, rely=0.8,  relwidth=0.4)

        self.btn_login.configure(command=self.btn_login_clicked)
        self.btn_reg.configure(command=self.btn_reg_clicked)

    def btn_reg_clicked(self):
        sock = self.register()
        if sock is None:
            return
        gol.set_value('socket', sock)
        self.close()
        group_win =GroupWin.Group_win()
        gol.set_value('groupwin', group_win)
        group_win.show()

    def btn_login_clicked(self):
        sock = self.login()
        if sock is None:
            return
        gol.set_value('socket', sock)
        self.close()
        group_win =GroupWin.Group_win()
        gol.set_value('groupwin', group_win)
        group_win.show()

    def __exit__(self, exc_type, exc_val, exc_tb):
        exit()



    def safety_check(self, sock, ASK=b'chabuduo', REPLY=b'dele'):
        sock.send(ASK)
        rec = sock.recv(len(REPLY))
        if rec != REPLY:
            return False
        return True

    def register(self):
        buffer=gol.get_value('buffer')
        id = self.entry_user.get()
        pwd = self.entry_pwd.get()
        if not id or not pwd:
            return None
        s=connect2server()
        if s is None:
            return None


        login_pack = Pack.Pack(mode=MODE.Register.value,idsend=id, idrec=pwd, content='')
        sock_send(s, login_pack.string)
        try:
            buffer, reply_pack = sock_recv_pack(s, buffer)
            gol.set_value('buffer', buffer)
            if reply_pack.mode != MODE.Login_Reply.value:
                s.close()
                return
            if reply_pack.content == '注册成功':
                gol.set_value('id', id)
                gol.set_value('pwd', pwd)
                return s
            elif reply_pack.content == '已注册':
                self.login_flag_con.set('该ID已被注册')
                s.close()
                return None
            else:
                self.login_flag_con.set('注册失败')
                s.close()
                return None
        except (AttributeError, ConnectionError):
            s.close()
            self.login_flag_con.set('连接已断开')
            return None
            # print('Link Lost!')


    def login(self):
        buffer = gol.get_value('buffer')
        id = self.entry_user.get()
        pwd = self.entry_pwd.get()
        if not id or not pwd:
            return None
        s = connect2server()
        if s is None:
            return None


        login_pack = Pack.Pack(mode=MODE.Login.value, idsend=id, idrec=pwd, content='')
        sock_send(s, login_pack.string)
        try:
            buffer, reply_pack = sock_recv_pack(s, buffer)
            gol.set_value('buffer',buffer)
            if reply_pack.mode != MODE.Login_Reply.value:
                s.close()
                return
            else:
                if reply_pack.content == '登录成功':
                    gol.set_value('id', id)
                    gol.set_value('pwd', pwd)

                    return s
                elif reply_pack.content == '密码错误':
                    self.login_flag_con.set('密码错误')
                    s.close()
                    return None
                elif reply_pack.content == '未注册':
                    self.login_flag_con.set('该ID未注册')
                    s.close()
                    return None
                elif reply_pack.content == '重复登录':
                    self.login_flag_con.set('不能重复登录')
                    s.close()
                    return None
                else:
                    s.close()
                    return None
        except:
            s.close()
            self.login_flag_con.set('连接已断开')
            return None


