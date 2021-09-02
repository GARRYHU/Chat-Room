import os
import globalvar as gol


def read(file_name=r"\config.txt"):
    try:
        cur_dir_path = os.path.abspath(".")
        config_file_path = cur_dir_path + file_name
        gol.set_value('config_file_path',config_file_path)
        config_file = open(config_file_path, "r")
        cont = config_file.read()
        config_file.close()
        cont_list = cont.splitlines(keepends=False)
        ser_ip = cont_list[0]
        port = int(cont_list[1])
        id = cont_list[2]
        pwd = cont_list[3]
        groupname = cont_list[4]
        grouppwd = cont_list[5]
        gol.set_value('server_ip', ser_ip)
        gol.set_value('port', port)
        gol.set_value('id', id)
        gol.set_value('pwd', pwd)
        gol.set_value('groupname', groupname)
        gol.set_value('grouppwd', grouppwd)
        return True
    except:
        return False


def update():
    file = open(gol.get_value('config_file_path'), "w")
    cont = gol.get_value('server_ip') + '\n' + str(gol.get_value('port')) + '\n' + gol.get_value(
        'id') + '\n' + gol.get_value('pwd') + '\n' + gol.get_value('groupname') + '\n' + gol.get_value('grouppwd')
    file.truncate(0)
    file.seek(0)
    file.write(cont)
    file.close()
