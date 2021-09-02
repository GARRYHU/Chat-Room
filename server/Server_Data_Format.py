from enum import Enum,unique

@unique
# 数据库查找返回类型
class CHECK_TYPE(Enum):
    FIND_MATCH = 1
    FIND_DISMATCH = 2
    NOT_FIND = 3

@unique
# 客户端连接模式   白名单中的为SAFE，不在白名单（且不在黑名单）中的为UNSAFE
class LINK_MODE(Enum):
    SAFE = 1
    UNSAFE = 2

# 在线用户表 表项
class client_entry(object):
    def __init__(self, ID, sock, groupname=''):
        self.id = ID
        self.socket = sock
        self.groupname = groupname

    def in_group(self, groupname):
        self.groupname = groupname

    def __del__(self):
        self.socket.close()

# 群在线成员池
class Group_User_Pool(object):  # 群在线成员池
    def __init__(self):
        self.group_user_pool = {}  # Key:群名 Value: Group_entry

    def check_group_exist(self, name):
        ret = self.group_user_pool.get(name)
        if ret is None:
            return False
        else:
            return True

    def insert_group(self, name, group_entry):
        self.group_user_pool[name] = group_entry

    def del_group(self, name):
        self.group_user_pool.pop(name)

    def group_in_user(self, name, ID):
        self.group_user_pool[name].in_user(ID)

    def group_out_user(self, name, ID):
        if self.check_group_exist(name):
            self.group_user_pool[name].out_user(ID)
            if self.group_user_pool[name].is_empty():
                self.del_group(name)

    def whether_user_in_group(self, name, ID):
        return self.group_user_pool[name].check_user_exist(ID)

    def get_users_in_group(self, name):
        return self.group_user_pool[name].idpool

# 群在线成员列表
class Group_entry(object):
    def __init__(self, groupname):
        self.name = groupname
        self.idpool = set()

    def in_user(self, ID):
        print('ID %s join Group %s' % (ID, self.name))
        self.idpool.add(ID)

    def out_user(self, ID):
        print('ID %s leave Group %s' % (ID, self.name))
        self.idpool.discard(ID)

    def is_empty(self):
        if len(self.idpool) == 0:
            return True
        else:
            return False

    def check_user_exist(self, ID):
        if ID in self.idpool:
            return True
        else:
            return False
