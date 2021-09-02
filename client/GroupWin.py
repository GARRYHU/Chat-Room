import threading
import configure as conf
import Pack
from Pack import *
from tkinter import *
import globalvar as gol
from sock import *
import MainWin


class Group_win:
    def show(self):
        self.win.mainloop()

    def close(self):
        self.win.destroy()

    def __init__(self):
        self.win = Tk()
        self.user = StringVar()
        self.user.set(gol.get_value('groupname'))
        self.pwd = StringVar()
        self.pwd.set(gol.get_value('grouppwd'))

        self.win.geometry("320x240")
        self.win.title("加入或创建群聊")
        self.win.resizable(width=False, height=False)

        self.label1 = Label(self.win)
        self.label1.place(relx=0.055, rely=0.1, height=31, width=89)
        self.label1.configure(text='群名')

        self.entry_groupname = Entry(self.win)
        self.entry_groupname.place(relx=0.28, rely=0.11, height=26, relwidth=0.554)
        self.entry_groupname.configure(textvariable=self.user)

        self.label2 = Label(self.win)
        self.label2.place(relx=0.055, rely=0.27, height=31, width=89)
        self.label2.configure(text='暗号')

        self.entry_grouppwd = Entry(self.win)
        self.entry_grouppwd.place(relx=0.28, rely=0.28, height=26, relwidth=0.554)

        self.entry_grouppwd.configure(textvariable=self.pwd)

        self.btn_login = Button(self.win)
        self.btn_login.place(relx=0.13, rely=0.6, height=32, width=88)
        self.btn_login.configure(text='加入')

        self.btn_reg = Button(self.win)
        self.btn_reg.place(relx=0.6, rely=0.6, height=32, width=88)
        self.btn_reg.configure(text='创建')

        self.login_flag_con = StringVar()
        self.login_flag = Label(self.win, textvariable=self.login_flag_con, fg='red', font=('宋体', 11))
        self.login_flag_con.set('请加入已有群或创建新的群')
        self.login_flag.place(relx=0.1, rely=0.8, relwidth=0.8)

        self.btn_login.configure(command=self.btn_add_clicked)
        self.btn_reg.configure(command=self.btn_create_clicked)

        self.win.protocol("WM_DELETE_WINDOW", self.exit)

    def btn_add_clicked(self):
        groupname = self.entry_groupname.get()
        grouppwd = self.entry_grouppwd.get()
        if not groupname or not grouppwd:
            return
        if len(groupname.encode('utf-8'))>30:
            self.login_flag_con.set('群名称太长')
            return
        ret = self.add_group(groupname, grouppwd)
        if ret is True:
            conf.update()
            self.close()
            main_win = MainWin.Main_win(groupname)
            gol.set_value('mainwin', main_win)
            listen_thread = threading.Thread(target=MainWin.receive_from_server, args=())
            listen_thread.start()

            main_win.root.protocol("WM_DELETE_WINDOW", main_win.__del__)  # 监听主窗口是否关闭
            main_win.root.mainloop()

    def btn_create_clicked(self):
        groupname = self.entry_groupname.get()
        grouppwd = self.entry_grouppwd.get()
        if not groupname or not grouppwd:
            return
        if len(groupname.encode('utf-8'))>30:
            self.login_flag_con.set('群名称太长')
            return
        ret = self.create_group(groupname, grouppwd)

        if ret is True:

            conf.update()
            self.close()
            main_win = MainWin.Main_win(groupname)
            gol.set_value('mainwin', main_win)
            listen_thread = threading.Thread(target=MainWin.receive_from_server, args=())
            listen_thread.start()

            main_win.root.protocol("WM_DELETE_WINDOW", main_win.__del__)  # 监听主窗口是否关闭
            main_win.root.mainloop()

    def __exit__(self, exc_type, exc_val, exc_tb):
        gol.get_value('socket').close()
        sys.exit()  # TODO

    def exit(self):
        sock=gol.get_value('socket')
        sock.shutdown(2)
        sock.close()
        sys.exit()  # TODO

    def create_group(self, name, pwd):

        id = gol.get_value('id')
        pack = Pack.Pack(mode=MODE.Create_Group.value, idsend=id, idrec=name, content=pwd)
        s = gol.get_value('socket')
        sock_send(s, pack.string)
        buffer = gol.get_value('buffer')
        try:
            buffer, reply_pack = sock_recv_pack(s, buffer)
            gol.set_value('buffer',buffer)
            if reply_pack.mode != MODE.Create_Group_Reply.value:
                self.login_flag_con.set('创建失败')
                return False
            else:
                if reply_pack.content == '群创建成功':
                    gol.set_value('groupname', name)
                    gol.set_value('grouppwd', pwd)
                    return True
                elif reply_pack.content == '群名已注册':
                    self.login_flag_con.set('该群名已注册')
                    return False
                else:
                    self.login_flag_con.set('创建失败')
                    return False
        except ConnectionError:
            s.close()
            self.login_flag_con.set('连接已断开')
            return False

    def add_group(self, name, pwd):
        id = gol.get_value('id')
        pack = Pack.Pack(mode=MODE.Add_Group.value, idsend=id, idrec=name, content=pwd)
        s = gol.get_value('socket')
        sock_send(s, pack.string)
        buffer = gol.get_value('buffer')
        try:
            buffer, reply_pack = sock_recv_pack(s, buffer)
            gol.set_value('buffer', buffer)
            if reply_pack.mode != MODE.Add_Group_Reply.value:
                self.login_flag_con.set('加入失败')
                return False
            else:
                if reply_pack.content == '群加入成功':
                    gol.set_value('groupname', name)
                    gol.set_value('grouppwd', pwd)
                    return True
                elif reply_pack.content == '群名未注册':
                    self.login_flag_con.set('该群名未注册')
                    return False
                elif reply_pack.content == '群暗号错误':
                    self.login_flag_con.set('群暗号错误')
                    return False
                elif reply_pack.content == '重复登录':
                    self.login_flag_con.set('不能重复登录该群')
                    return False
                else:
                    self.login_flag_con.set('加入失败')
                    return False
        except ConnectionError:
            s.close()
            self.login_flag_con.set('连接已断开')
            return False
