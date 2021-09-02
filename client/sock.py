import Pack
import socket
import globalvar as gol


def safety_check(sock, ASK=b'chabuduo', REPLY=b'dele'):
    sock.send(ASK)
    rec = sock.recv(len(REPLY))
    if rec != REPLY:
        return False
    return True

def connect2server():
    port = gol.get_value('port')
    server_public_ip = gol.get_value('server_ip')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server_public_ip, port))
    if safety_check(s) is False:
        s.close()
        return None
    else:
        return s

def sock_send(sock,pack_utf_str,form='utf-8'):
    uni_str=pack_utf_str.encode(form)
    try:
        sock.send(uni_str)
        return True
    except ConnectionError:
        return False



def sock_recv_pack(sock,buffer,End=Pack.Pack.ETX,form='utf-8'):
    if End in buffer:
        End_pos=buffer.find(End)
        total_data=buffer[:End_pos+1]
        try:
            pack=Pack.Pack(string=total_data)
        except ValueError:
            raise ConnectionError
        return buffer[End_pos+1:],pack

    total_data=buffer
    while True:
        data = sock.recv(8192).decode(form)
        if End in data:
            End_pos = data.find(End)
            total_data+=data[:End_pos+1]
            try:
                pack = Pack.Pack(string=total_data)
            except ValueError:
                raise ConnectionError
            return data[End_pos+1:],pack
        total_data+=data

