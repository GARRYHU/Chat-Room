from Pack import *
import ser_decorator
import globalvar as glo


#socket端口 发送字符串
def sock_send(sock, pack_utf_str, form='utf-8'):
    uni_str = pack_utf_str.encode(form)
    try:
        sock.send(uni_str)
        return True
    except:
        return False

#socket端口 接收数据包
def sock_recv_pack(sock, buffer, End=Pack.ETX, form='utf-8', max_recv_length=None):
    if End in buffer:
        End_pos = buffer.find(End)
        total_data = buffer[:End_pos + 1]
        try:
            pack = Pack(string=total_data)
        except:
            raise ConnectionError
        return buffer[End_pos + 1:], pack

    total_data = buffer
    recv_length = 0
    while True:
        data = sock.recv(8192).decode(form)
        if data == '':
            raise ConnectionError
        if End in data:
            End_pos = data.find(End)
            total_data += data[:End_pos + 1]
            try:
                pack = Pack(string=total_data)
            except:
                raise ConnectionError
            return data[End_pos + 1:], pack

        if max_recv_length is not None:
            recv_length += len(data)
            if recv_length >= max_recv_length:
                raise ConnectionError

        total_data += data

# 有时间限制的socket数据接收
@ser_decorator.time_limited(3)  # 时间限制 3s
def sock_recv_limit(sock, len):
    rec = sock.recv(len)
    glo.set_value('sock_recv_limit_ret', rec) # 此处是通过全局变量进行数据传递

# 尝试关闭socket
def try_close_socket(sock):
    if not getattr(sock, '_closed'):
        return True