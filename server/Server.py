from Server_Data_Format import *
import os
import threading
from sock import *
from Pack import *
from database import *
import globalvar as glo
import socket

class Server(object):
    def __init__(self):
        try:
            port, max_connection, localip = self.__read_config()
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print('Server Local IP', localip)
            self.socket.bind((localip, port))
            print('Bind TCP on %d...' % port)
            self.socket.listen(max_connection)
            print('Waiting for connection...    max_connection_limit:', max_connection)

            self.user_account_db = users_database()  # 用户账户数据库
            self.black_ip = IP_List('black_ip')  # 白名单IP数据库
            self.white_ip = IP_List('white_ip')  # 黑名单IP数据库
            self.online_client_dict = {}  # 在线用户表
            self.group_list_db = Group_List()  # 群名称数据库
            self.group_user_pool = Group_User_Pool()  # 群在线成员池
            self.history_db = Group_history()  # 群历史记录数据库
            self.group_mem_db = Group_mem()  # 群成员数据库

            self.lock=threading.Lock()
        except Exception as e:
            print('服务器启动失败：')
            print(e)

    # 等待IP连接
    def wait_connetion(self):
        clientSocket, clientAddress = self.socket.accept()
        clientip = clientAddress[0]
        if self.white_ip.check_IP_exist(clientip):  # 白名单IP，安全模式
            t = threading.Thread(target=self.__client_thread_main, args=(clientSocket, clientAddress, LINK_MODE.SAFE))
            t.start()
        else:
            if self.black_ip.check_IP_exist(clientip):  # 黑白名单IP，拦截
                print('Reject Black IP : ', clientAddress)
                return
            # 陌生IP，以非安全模式连接
            t = threading.Thread(target=self.__client_thread_main, args=(clientSocket, clientAddress, LINK_MODE.UNSAFE))
            t.start()

    # 为用户分配的线程的主函数
    def __client_thread_main(self, sock, addr, mode):
        ip = addr[0]
        recv_buffer = ''
        print('Accept new connection from ', addr, '\t', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        try:
            # 安全检查
            self.__Safety_Check(sock, ip, mode)
            # 账号登录
            recv_buffer, client = self.__greet(sock, recv_buffer)

            print('Login ID : %s\t%s' % (client.id, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

        except Exception:
            try_close_socket(sock)
            print('Login Failure from ', addr, '\t', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            return

        try:
            # 登入群
            recv_buffer = self.__grouplogin(sock, client.id, recv_buffer)
            # 向该用户同步群历史
            self.__sync_history(client)
            # 向该群所有用户同步当前在线人数
            self.__sync_group_user_list(client.groupname)

        except Exception:
            try_close_socket(sock)
            self.__client_left(client.id)
            print('ID %s Fail to join a group' % client.id)
            print('EXIT  ID : %s\t%s' % (client.id, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            return

        while True:
            try:
                # 接收用户数据包
                recv_buffer, pack = sock_recv_pack(sock, recv_buffer)
                # 处理用户数据包
                self.__handle_pack(sock, pack)

            except Exception:
                try_close_socket(sock)
                self.__client_left(client.id)
                self.__Broadcast_in_Group(client.groupname, "Bye ID %s!" % client.id)
                self.__sync_group_user_list(client.groupname)
                print('EXIT  ID : %s\t%s' % (client.id, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                return

    # IP安全性检查
    def __Safety_Check(self, sock, ip, mode, ASK=b'chabuduo', REPLY=b'dele'):
        if mode == LINK_MODE.UNSAFE:  # 非白名单IP限制登录时间
            try:
                self.lock.acquire() # 线程同步 上锁 保护glo中的sock_recv_limit_ret
                sock_recv_limit(sock, len(ASK))
                ret_value=glo.get_value('sock_recv_limit_ret')
                self.lock.release() # 线程同步 释放锁
                if ret_value == ASK:
                    sock.send(REPLY)
                    self.white_ip.insert_IP(ip)  # 安全检查成功的客户端IP加入白名单
                else:
                    raise ConnectionError
            except Exception:  # 安全检查失败的IP加入IP黑名单
                print('Add Black IP : ', ip)
                self.black_ip.insert_IP(ip)
                sock.close()
                raise ConnectionError
        else:  # 白名单IP不限制登录时间
            try:
                self.__safety_check_unlimit(sock, ASK, REPLY)
            except:
                sock.close()
                raise ConnectionError

    # 无时间限制的登录安全检查 白名单IP
    def __safety_check_unlimit(self, sock, ASK, REPLY):
        rec = sock.recv(len(ASK))
        if rec == ASK:
            sock.send(REPLY)
        else:
            raise ConnectionError

    # 账号登录流程
    def __greet(self, sock, buffer):
        while True:
            try:
                buffer, pack = sock_recv_pack(sock, buffer)
            except:
                raise ConnectionError
            if pack.mode == MODE.Login.value:  # 登录
                id = pack.idsend
                pwd = pack.idrec
                ret_ = self.__Check_Account(id, pwd)
                if ret_ == CHECK_TYPE.FIND_MATCH:
                    if not self.__Is_online(id):
                        reply_pack = Pack(mode=MODE.Login_Reply.value, idsend=ID.SERVER.value, idrec=id,
                                          content='登录成功')
                        sock_send(sock, reply_pack.string)
                        self.__user_login(id, sock)
                        return buffer, self.online_client_dict[id]
                    else:
                        reply_pack = Pack(mode=MODE.Login_Reply.value, idsend=ID.SERVER.value, idrec=id,
                                          content='重复登录')
                        sock_send(sock, reply_pack.string)
                        sock.close()
                elif ret_ == CHECK_TYPE.FIND_DISMATCH:
                    reply_pack = Pack(mode=MODE.Login_Reply.value, idsend=ID.SERVER.value, idrec=id,
                                      content='密码错误')
                    sock_send(sock, reply_pack.string)
                    sock.close()
                elif ret_ == CHECK_TYPE.NOT_FIND:
                    reply_pack = Pack(mode=MODE.Login_Reply.value, idsend=ID.SERVER.value, idrec=id,
                                      content='未注册')
                    sock_send(sock, reply_pack.string)
                    sock.close()

            if pack.mode == MODE.Register.value:  # 注册
                id = pack.idsend
                pwd = pack.idrec
                ret_ = self.__Check_Account(id, pwd)
                if ret_ != CHECK_TYPE.NOT_FIND:
                    reply_pack = Pack(mode=MODE.Login_Reply.value, idsend=ID.SERVER.value, idrec=id,
                                      content='已注册')
                    sock_send(sock, reply_pack.string)
                    sock.close()
                else:
                    reply_pack = Pack(mode=MODE.Login_Reply.value, idsend=ID.SERVER.value, idrec=id,
                                      content='注册成功')
                    sock_send(sock, reply_pack.string)
                    self.__user_register(id, pwd, sock)
                    return buffer, self.online_client_dict[id]

    # 用户登录账户
    def __user_login(self, id, sock):
        self.__insert_online_client_dict(id, sock)

    # 用户注册账户并登录
    def __user_register(self, id, pwd, sock):
        self.__Add_New_Account_db(id, pwd)
        self.__insert_online_client_dict(id, sock)

    # 群登录流程
    def __grouplogin(self, sock, id, buffer):
        while True:
            try:
                buffer, pack = sock_recv_pack(sock, buffer)
            except:
                raise ConnectionError
            if pack.mode == MODE.Add_Group.value:  # 加入群
                groupname = pack.idrec
                pwd = pack.content
                ret_ = self.__Check_Grouplist(groupname, pwd)
                if ret_ == CHECK_TYPE.FIND_MATCH:  # 群号和群暗号匹配
                    if self.group_user_pool.check_group_exist(groupname) and self.group_user_pool.whether_user_in_group(
                            groupname,
                            id):  # 重复登录检查，该ID是否已经登录该群
                        reply_pack = Pack(mode=MODE.Add_Group_Reply.value, idsend=ID.SERVER.value, idrec=id,
                                          content='重复登录')
                        sock_send(sock, reply_pack.string)
                    else:  # 加入群成功
                        reply_pack = Pack(mode=MODE.Add_Group_Reply.value, idsend=ID.SERVER.value, idrec=id,
                                          content='群加入成功')
                        sock_send(sock, reply_pack.string)
                        self.__join_group(groupname, id)
                        return buffer


                elif ret_ == CHECK_TYPE.FIND_DISMATCH:  # 群号和群暗号不匹配
                    reply_pack = Pack(mode=MODE.Add_Group_Reply.value, idsend=ID.SERVER.value, idrec=id,
                                      content='群暗号错误')
                    sock_send(sock, reply_pack.string)

                elif ret_ == CHECK_TYPE.NOT_FIND:  # 群号不存在
                    reply_pack = Pack(mode=MODE.Add_Group_Reply.value, idsend=ID.SERVER.value, idrec=id,
                                      content='群名未注册')
                    sock_send(sock, reply_pack.string)

            if pack.mode == MODE.Create_Group.value:  # 创建群
                id = pack.idsend
                groupname = pack.idrec
                pwd = pack.content
                ret_ = self.__Check_Grouplist(groupname, pwd)
                if ret_ != CHECK_TYPE.NOT_FIND:
                    reply_pack = Pack(mode=MODE.Create_Group_Reply.value, idsend=ID.SERVER.value, idrec=id,
                                      content='群名已注册')
                    sock_send(sock, reply_pack.string)

                else:  # 群名未注册
                    ret = self.__create_group(groupname, pwd, id)
                    if ret is True:
                        reply_pack = Pack(mode=MODE.Create_Group_Reply.value, idsend=ID.SERVER.value, idrec=id,
                                          content='群创建成功')
                        sock_send(sock, reply_pack.string)
                        return buffer
                    else:
                        reply_pack = Pack(mode=MODE.Create_Group_Reply.value, idsend=ID.SERVER.value, idrec=id,
                                          content='群创建失败')

                        sock_send(sock, reply_pack.string)

    # 用户创建群流程
    def __create_group(self, groupname, pwd, id):
        try:
            ret = self.__Create_New_Group_db(groupname, pwd)  # 创建群时的数据库初始化操作 群列表注册+群历史记录表创建+群成员表创建
            if ret is True:
                self.online_client_dict[id].in_group(groupname)
                self.group_user_pool.insert_group(groupname, Group_entry(groupname))
                self.group_user_pool.group_in_user(groupname, id)
                self.group_mem_db.insert_group_mem(groupname, id)  # 把创建者添加到群成员表
                print('NEW Group    Name : %s ' % (groupname))
                return True
            else:
                return False
        except Exception as e:
            print("__create_group() 创建群时异常：", e)
            return False

    # 创建群的数据库操作
    def __Create_New_Group_db(self, groupname, pwd):
        try:
            ret = self.group_list_db.create_group(groupname, pwd)
            if ret is False:
                return False
            ret = self.history_db.create_group_history(groupname)
            if ret is False:
                return False
            ret = self.group_mem_db.create_group_mem_table(groupname)
            if ret is False:
                return False

            return True
        except Exception as e:
            print('__Create_New_Group_db:', e)
            return False

    # 用户登入群流程
    def __join_group(self, groupname, id):
        self.online_client_dict[id].in_group(groupname)
        if not self.group_mem_db.check_mem_exist(groupname, id):  # 是该群的新成员
            self.group_mem_db.insert_group_mem(groupname, id)
            self.__Broadcast_in_Group(groupname, "Welcome NEW member %s" % id)
        else:
            self.__Broadcast_in_Group(groupname, "Welcome ID %s!" % id)
        if self.group_user_pool.check_group_exist(groupname):  # 群已在线
            self.group_user_pool.group_in_user(groupname, id)
        else:  # 群未在线
            self.group_user_pool.insert_group(groupname, Group_entry(groupname))
            self.group_user_pool.group_in_user(groupname, id)

    # 用户登录完毕后处理用户发来的数据包
    def __handle_pack(self, sock, pack):
        if pack.mode == MODE.Message.value:
            # MESSAGE
            if pack.idrec in self.online_client_dict and self.__Is_online(pack.idrec):
                to_entry = self.online_client_dict[pack.idrec]
                sock_send(to_entry.socket, pack.string)
                reply_pack = Pack(mode=MODE.Message_Reply.value, idsend=ID.SERVER.value, idrec=pack.idsend,
                                  content='Send Success')
                sock_send(sock, reply_pack.string)
            else:
                reply_pack = Pack(mode=MODE.Message_Reply.value, idsend=ID.SERVER.value, idrec=pack.idsend,
                                  content='Send Failure')
                sock_send(sock, reply_pack.string)

        elif pack.mode == MODE.Group_Message.value:
            # Group Message
            sender_id = pack.idsend
            client_entry = self.online_client_dict[sender_id]
            groupname = pack.idrec
            text = pack.content
            if self.group_user_pool.check_group_exist(groupname) \
                    and client_entry.groupname == groupname \
                    and self.group_user_pool.whether_user_in_group(groupname, sender_id):  # ID、群名称合法性检查
                reply_pack = Pack(mode=MODE.Group_Message_Reply.value, idsend=ID.SERVER.value, idrec=sender_id,
                                  content='Send Success')
                sock_send(sock, reply_pack.string)
            else:
                return

            self.history_db.insert_history(groupname, sender_id, self.__get_time(), MODE.Group_Message.value, text)

            allusers_in_group = self.group_user_pool.get_users_in_group(groupname)  # 向所有在该群中的用户发送该条信息
            for it in allusers_in_group:
                if it in self.online_client_dict and self.__Is_online(it):
                    pack = Pack(mode=MODE.Group_Message.value, idsend=sender_id, idrec=it,
                                content=text)
                    recv_sock = self.online_client_dict[it].socket
                    sock_send(recv_sock, pack.string)

    # 用户离开流程 在线用户表中删除+用户退出群在线成员列表
    def __client_left(self, id):
        if id in self.online_client_dict:
            groupname = self.online_client_dict[id].groupname
            self.online_client_dict.pop(id)
            if groupname != '':
                self.group_user_pool.group_out_user(groupname, id)

    # 向所有在群名为groupname的群的在线用户同步当前在线用户列表
    def __sync_online_users_in_group(self, groupname):
        if not self.group_user_pool.check_group_exist(groupname):
            return False
        content = ''
        allusers_in_group = self.group_user_pool.get_users_in_group(groupname)  # 获取群在线用户列表
        for it in allusers_in_group:
            if it in self.online_client_dict and self.__Is_online(it):  # 判断该用户是否在线
                content += it + '\n'
        self.__Broadcast_in_Group(groupname, content, mode=MODE.Sync_Users_in_Group.value)

        return True

    # 向所有在群名为groupname的群的在线用户同步用户列表(在线+离线)
    def __sync_group_user_list(self, groupname):
        if not self.group_user_pool.check_group_exist(groupname):
            return False
        content = ''
        all_online_users_in_group = self.group_user_pool.get_users_in_group(groupname)  # 获取群在线用户列表
        for it in all_online_users_in_group:
            if it in self.online_client_dict and self.__Is_online(it):  # 判断该用户是否在线
                content += it + '\n'
        content += '\n'
        all_users_in_group=self.group_mem_db.get_mem(groupname)
        for it in all_users_in_group:
            content+=it[0]+'\n'
        self.__Broadcast_in_Group(groupname, content, mode=MODE.Sync_Users_in_Group.value)

        return True

    # 向所有在群名为groupname的群的在线用户广播内容(content)
    def __Broadcast_in_Group(self, groupname, content, mode=MODE.BroadCast_in_Group.value):
        if not self.group_user_pool.check_group_exist(groupname):
            return False
        allusers_in_group = self.group_user_pool.get_users_in_group(groupname)
        for it in allusers_in_group:
            if it in self.online_client_dict and self.__Is_online(it):
                pack = Pack(mode=mode, idsend=ID.SERVER.value, idrec=it,
                            content=content)
                recv_sock = self.online_client_dict[it].socket
                sock_send(recv_sock, pack.string)
        return True

    # 发送所在群历史记录
    def __sync_history(self, client_entry):
        sock = client_entry.socket
        groupname = client_entry.groupname
        if not self.group_user_pool.check_group_exist(groupname):  # 判断当前群是否在线
            return False

        history = self.history_db.get_history(groupname)
        if history is None:
            return False

        for it in history:
            mode = it[2]
            if mode == MODE.Group_Message.value:
                mode = MODE.Sync_Group_Message.value
            elif mode == MODE.BroadCast_in_Group.value:
                mode = MODE.Sync_BroadCast_in_Group.value
            pack = Pack(mode=mode, idsend=it[0], content=it[3], idrec=client_entry.id)
            pack.update_time(it[1])
            pack.encode()
            sock_send(sock, pack.string)

        pack = Pack(mode=MODE.Sync_Group_Message_END.value, idsend=ID.SERVER.value, content='', idrec=client_entry.id)
        sock_send(sock, pack.string)

    # 查找用户账户数据库
    def __Check_Account(self, id, pwd):
        if not self.user_account_db.check_ID_exist(id):
            return CHECK_TYPE.NOT_FIND
        if self.user_account_db.check_pwd(id, pwd):
            return CHECK_TYPE.FIND_MATCH
        else:
            return CHECK_TYPE.FIND_DISMATCH  #

    # 查找群列表数据库
    def __Check_Grouplist(self, name, pwd):
        if not self.group_list_db.check_name_exist(name):
            return CHECK_TYPE.NOT_FIND
        if self.group_list_db.check_pwd(name, pwd):
            return CHECK_TYPE.FIND_MATCH
        else:
            return CHECK_TYPE.FIND_DISMATCH

    # 向用户账号数据库添加新用户
    def __Add_New_Account_db(self, id, pwd):
        print('NEW  ID : %s ' % (id))
        self.user_account_db.insert_accounts(id, pwd)

    # 向在线用户列表添加用户
    def __insert_online_client_dict(self, id, socket):
        self.online_client_dict[id] = client_entry(id, socket)

    # 判断用户是否在线
    def __Is_online(self, id):
        entry = self.online_client_dict.get(id)
        if entry is None:
            return False
        if not isinstance(entry.socket, socket.socket):
            return False
        if not getattr(entry.socket, '_closed'):
            return True
        return True

    # 获取当前时间字符串
    def __get_time(self):
        return datetime.datetime.now().strftime(Pack.TIME_Format)

    # 读取服务器配置文件
    def __read_config(self, file_name=r"\config.txt"):
        # 格式:
        #   port
        #   最大连接数
        #   服务器本地IP(可省略)
        cur_dir_path = os.path.abspath(".")
        config_file_path = cur_dir_path + file_name
        config_file = open(config_file_path, "r")
        cont = config_file.read()
        config_file.close()
        cont_list = cont.splitlines(keepends=False)
        port = int(cont_list[0])
        max_connection = int(cont_list[1])
        if len(cont_list) == 3:
            ip = cont_list[2]
        else:  # 获取服务器本地IP
            localhostname = socket.gethostname()
            ip = socket.gethostbyname(localhostname)
        return port, max_connection, ip
