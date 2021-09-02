import pymysql

# 用户账户数据库
class users_database(object):

    def __init__(self, host='localhost', user="root", passwd="password"):
        self.conn = pymysql.connect(host=host, user=user, passwd=passwd, db='users')

    def __del__(self):
        self.conn.close()

    def insert_accounts(self, ID, password):  # 注册账户
        try:
            self.conn.ping(reconnect=True)
            cur = self.conn.cursor()
            inst = 'insert into users.accounts values(\"%s\",\"%s\")' % (ID, password)
            cur.execute(inst)
            cur.close()
            self.conn.commit()
            return True
        except:
            return False

    def check_ID_exist(self, ID):
        try:
            self.conn.ping(reconnect=True)
            cur = self.conn.cursor()
            sqli = 'select * from users.accounts WHERE ID=\"%s\"' %ID
            cur.execute(sqli)
            entry = cur.fetchone()  # 获取单条数据
            cur.close()
            if entry is None:
                return False
            else:
                return True
        except:
            return False

    def check_pwd(self,ID,pwd):
        try:
            self.conn.ping(reconnect=True)
            cur = self.conn.cursor()
            sqli = 'select * from users.accounts WHERE ID=\"%s\"' % ID
            cur.execute(sqli)
            entry = cur.fetchone()  # 获取单条数据
            cur.close()
            if entry is not None and entry[1]==pwd:
                return True
            else:
                return False
        except:
            return False

# IP列表数据库
class IP_List(object):
    def __init__(self,tablename,host='localhost', user="root", passwd="password"):
        self.conn = pymysql.connect(host=host, user=user, passwd=passwd, db='ip_list')
        self.table_name=tablename

    def __del__(self):
        self.conn.close()

    def insert_IP(self, ip):  # 注册账户
        try:

            # ping校验连接是否异常
            self.conn.ping(reconnect=True)
            cur = self.conn.cursor()
            inst = 'insert into ip_list.%s values(\"%s\")' % (self.table_name, ip)
            cur.execute(inst)
            cur.close()
            self.conn.commit()
            return True
        except:
            return False

    def check_IP_exist(self, ip):
        try:
            self.conn.ping(reconnect=True)
            cur = self.conn.cursor()
            sqli = 'select * from ip_list.%s WHERE IP=\"%s\"' % (self.table_name, ip)
            cur.execute(sqli)
            entry = cur.fetchone()  # 获取单条数据
            cur.close()
            if entry is None:
                return False
            else:
                return True
        except:
            return False

# 群列表数据库
class Group_List(object):

    def __init__(self, host='localhost', user="root", passwd="password"):
        self.conn = pymysql.connect(host=host, user=user, passwd=passwd, db='group')

    def __del__(self):
        self.conn.close()

    def create_group(self, name, password):  # 注册账户
        try:
            self.conn.ping(reconnect=True)
            cur = self.conn.cursor()
            inst = 'insert into group.group_list values(\"%s\",\"%s\")' % (name, password)
            cur.execute(inst)
            cur.close()
            self.conn.commit()
            return True
        except:
            return False

    def check_name_exist(self, name):
        try:
            self.conn.ping(reconnect=True)
            cur = self.conn.cursor()
            sqli = 'select * from group.group_list WHERE Name=\"%s\"' % name
            cur.execute(sqli)
            entry = cur.fetchone()  # 获取单条数据
            cur.close()
            if entry is None:
                return False
            else:
                return True
        except:
            return False

    def check_pwd(self, name, pwd):
        try:
            self.conn.ping(reconnect=True)
            cur = self.conn.cursor()
            sqli = 'select * from group.group_list WHERE Name=\"%s\"' % name
            cur.execute(sqli)
            entry = cur.fetchone()  # 获取单条数据
            cur.close()
            if entry is not None and entry[1]==pwd:
                return True
            else:
                return False
        except:
            return False

# 群历史数据库
class Group_history(object):
    def __init__(self, host='localhost', user="root", passwd="password"):
        self.conn = pymysql.connect(host=host, user=user, passwd=passwd, db='history')

    def __del__(self):
        self.conn.close()

    def __str2tablename(self,s):
        return 'T'+s.encode('utf-8').hex()

    def create_group_history(self,groupname):
        try:
            tablename=self.__str2tablename(groupname)
            self.conn.ping(reconnect=True)
            cur=self.conn.cursor()
            sql="CREATE TABLE %s (`sender_id`  varchar(255) BINARY CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT '' ,`time`  varchar(50) BINARY CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT '' ,`mode`  char(2) BINARY CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT '' ,`content`  varchar(10000) BINARY CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT '' )"%tablename
            cur.execute(sql)
            cur.close()
            self.conn.commit()
            return True
        except Exception as e:
            return False

    def insert_history(self,groupname,id,time,mode,content):
        try:
            tablename = self.__str2tablename(groupname)
            self.conn.ping(reconnect=True)
            cur = self.conn.cursor()
            inst = 'insert into history.%s values(\"%s\",\"%s\",\"%s\",\"%s\")' % (tablename,id,time,mode,content)
            cur.execute(inst)
            cur.close()
            self.conn.commit()
        except:
            return False

    def get_history(self,groupname):
        try:
            tablename = self.__str2tablename(groupname)
            self.conn.ping(reconnect=True)
            cur = self.conn.cursor()
            sql = "select * from %s" % tablename
            cur.execute(sql)
            ret=cur.fetchall()
            cur.close()
            return ret
        except:
            return None

# 群成员数据库
class Group_mem(object):
    def __init__(self, host='localhost', user="root", passwd="password"):
        self.conn = pymysql.connect(host=host, user=user, passwd=passwd, db='group_mem')

    def __del__(self):
        self.conn.close()

    def __str2tablename(self,s):
        return 'T'+s.encode('utf-8').hex()

    def create_group_mem_table(self,groupname):
        try:
            tablename = self.__str2tablename(groupname)
            self.conn.ping(reconnect=True)
            cur=self.conn.cursor()
            sql="CREATE TABLE %s (id  varchar(255) BINARY CHARACTER SET utf8 COLLATE utf8_bin NOT NULL DEFAULT '' ,PRIMARY KEY (id))" % tablename
            cur.execute(sql)
            cur.close()
            self.conn.commit()
            return True
        except Exception as e:
            return False

    def insert_group_mem(self,groupname,id):
        try:
            tablename = self.__str2tablename(groupname)
            self.conn.ping(reconnect=True)
            cur = self.conn.cursor()
            inst = 'insert into group_mem.%s values(\"%s\")' % (tablename,id)
            cur.execute(inst)
            cur.close()
            self.conn.commit()
        except:
            return False

    def get_mem(self,groupname):
        try:
            tablename = self.__str2tablename(groupname)
            self.conn.ping(reconnect=True)
            cur = self.conn.cursor()
            sql = "select * from %s" % tablename
            cur.execute(sql)
            ret=cur.fetchall()
            cur.close()
            return ret
        except:
            return None

    def check_mem_exist(self, groupname,id):
        try:
            tablename = self.__str2tablename(groupname)
            self.conn.ping(reconnect=True)
            cur = self.conn.cursor()
            sqli = 'select * from group_mem.%s WHERE id=\"%s\"' % (tablename,id)
            cur.execute(sqli)
            entry = cur.fetchone()  # 获取单条数据
            cur.close()
            if entry is None:
                return False
            else:
                return True
        except:
            return False
