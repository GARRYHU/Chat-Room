from Pack import *
from tkinter import *
import globalvar as gol
from sock import *
import threading
import winsound


def group_message_sound():
    winsound.Beep(2222, 300)


def group_broadcast_sound():
    winsound.Beep(3333, 100)


def line(win):
    win.message_box_insert('-----------------------------------------------------------\n')


def handle_pack(pack):
    myid = gol.get_value('id')
    main_win = gol.get_value('mainwin')
    send_flag = main_win.send_flag_con
    if pack.mode == MODE.Message_Reply.value:
        if pack.content == 'Send Success':
            send_flag.set('发送成功')
            main_win.inp_cont.delete('0.0', 'end')  # 发送成功后清空输入框文本内容
        else:
            send_flag.set('发送失败')

    elif pack.mode == MODE.Message.value:
        main_win.message_box_insert(pack.idsend + ' : ' + pack.content)


    elif pack.mode == MODE.Group_Message_Reply.value:
        if pack.content == 'Send Success':
            send_flag.set('发送成功')
            main_win.inp_cont.delete('0.0', 'end')  # 发送成功后清空输入框文本内容
        else:
            send_flag.set('发送失败')

    elif pack.mode == MODE.Group_Message.value:
        main_win.message_box_insert(pack.idsend + ' :\n' + pack.content)
        if pack.idsend != myid:
            group_message_sound()
        line(main_win)
        main_win.message_box.see(END)  # 文本框自动滚动


    elif pack.mode == MODE.BroadCast_in_Group.value:
        main_win.message_box_insert('*** ' + pack.content + ' ***\n')
        group_broadcast_sound()
        line(main_win)
        main_win.message_box.see(END)  # 文本框自动滚动

    elif pack.mode == MODE.Sync_Users_in_Group.value:
        users_list = pack.content.splitlines(keepends=False)

        # 分离出在线用户列表和离线用户列表
        pos = users_list.index('')
        online_list = users_list[:pos]
        all_list = users_list[pos + 1:]

        main_win.group_user_list.delete(0, END)
        myid = gol.get_value('id')
        main_win.group_user_list.insert(END, '在线')
        main_win.group_user_list.insert(END, '')
        for it in online_list:
            if it == myid:
                main_win.group_user_list.insert(END, it + "  (ME)") # 第一行显示本账号
        for it in online_list:
            if it != myid:
                main_win.group_user_list.insert(END, it)

        main_win.group_user_list.insert(END, '')
        main_win.group_user_list.insert(END, '——————————————————————————————')
        main_win.group_user_list.insert(END, '')
        main_win.group_user_list.insert(END, '离线')
        main_win.group_user_list.insert(END, '')
        for it in all_list:
            if it not in online_list:
                main_win.group_user_list.insert(END, it)

    elif pack.mode == MODE.Sync_BroadCast_in_Group.value:
        main_win.message_box_insert('*** ' + pack.content + ' ***\n')
        line(main_win)
        main_win.message_box.see(END)  # 文本框自动滚动

    elif pack.mode == MODE.Sync_Group_Message.value:
        main_win.message_box_insert(pack.idsend + ' :\n' + pack.content)
        line(main_win)


    elif pack.mode == MODE.Sync_Group_Message_END.value:
        main_win.message_box_insert('\n以上是历史消息\n\n')
        line(main_win)
        main_win.message_box.see(END)  # 文本框自动滚动

    elif pack.mode==MODE.Update.value:
        if pack.content!=gol.get_value('version'):
            main_win.message_box_insert('**有新的版本**\n')
            line(main_win)
            main_win.message_box.see(END)


    else:
        main_win.message_box_insert('**不支持的消息类型，可能需要更新**\n')
        line(main_win)
        main_win.message_box.see(END)

def receive_from_server():
    recv_buffer = gol.get_value('buffer')
    sock = gol.get_value('socket')
    while True:
        try:
            recv_buffer, pack = sock_recv_pack(sock, recv_buffer)
            gol.set_value('buffer', recv_buffer)
            handle_pack(pack)
        except ConnectionError:
            print('与服务器连接中断')
            return


class Main_win:
    def __init__(self, win_name):
        self.root = Tk()
        self.root.title(win_name)
        self.root.geometry('1000x720')  # 这里的乘号不是 * ，而是小写英文字母 x
        self.root.resizable(width=False, height=True)

        self.message_box = Text(self.root, fg='black', font=('宋体', 15))
        self.message_box.place(relx=0.02, rely=0.05, relheight=0.9, relwidth=0.6)
        self.message_box.configure(state='disabled')
        self.inp_cont = Text(self.root, font=('宋体', 15))
        self.inp_cont.place(relx=0.65, rely=0.57, relwidth=0.3, relheight=0.28)
        self.btn_send = Button(self.root, text='发送', command=self.on_btn_send)
        self.btn_send.place(relx=0.7, rely=0.9, relwidth=0.04, relheight=0.04)
        self.btn_reset = Button(self.root, text='清空', command=self.on_btn_rst)
        self.btn_reset.place(relx=0.86, rely=0.9, relwidth=0.04, relheight=0.04)
        self.send_flag_con = StringVar()
        self.send_flag = Label(self.root, textvariable=self.send_flag_con, fg='red', font=('宋体', 10))
        self.send_flag_con.set('')
        self.send_flag.place(relx=0.76, rely=0.9, relwidth=0.08, relheight=0.04)

        self.scroll_mess = Scrollbar(self.root)  # 关联滚动条与消息框
        self.scroll_mess.place(relx=0.62, rely=0.05, relheight=0.9)
        self.scroll_mess.config(command=self.message_box.yview)
        self.message_box.configure(yscrollcommand=self.scroll_mess.set)

        self.scroll_inp = Scrollbar(self.root)  # 关联滚动条与消息框
        self.scroll_inp.place(relx=0.95, rely=0.57, relheight=0.28)
        self.scroll_inp.config(command=self.inp_cont.yview)
        self.inp_cont.configure(yscrollcommand=self.scroll_inp.set)

        self.group_user_list = Listbox(self.root, fg='black', font=('宋体', 15))
        self.group_user_list.place(relx=0.65, rely=0.05, relwidth=0.3, relheight=0.45)
        self.scroll_list = Scrollbar(self.root)  # 关联滚动条与列表框
        self.scroll_list.place(relx=0.95, rely=0.05, relheight=0.45)
        self.scroll_list.config(command=self.group_user_list.yview)
        self.group_user_list.configure(yscrollcommand=self.scroll_list.set)

    def on_btn_send(self):
        sock = gol.get_value('socket')
        myid = gol.get_value('id')
        groupname = gol.get_value('groupname')
        content = self.inp_cont.get('0.0', 'end')
        if content == '\n':
            return
        if len(content) >3000:
            self.send_flag_con.set('内容过长')

        pack = Pack.Pack(MODE.Group_Message.value, idsend=myid, idrec=groupname, content=content)
        sock_send(sock, pack.string)

    def on_btn_rst(self):
        self.inp_cont.delete('0.0', 'end')

    def message_box_insert(self, str_):
        self.message_box.configure(state='normal')
        self.message_box.insert(END, str_)
        self.message_box.configure(state='disabled')

    def __del__(self):
        gol.get_value('socket').close()
        sys.exit()

    def __exit__(self, exc_type, exc_val, exc_tb):
        gol.get_value('socket').close()
        sys.exit()
