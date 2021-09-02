from enum import Enum, unique
import datetime


@unique
class ID(Enum):
    SERVER = '-'
    ALL = '+'
    UNKNOWN = ' '


@unique
class MODE(Enum):
    Register = '01'
    Login = '02'
    Login_Reply = '03'
    Message = '04'
    Message_Reply = '05'
    Create_Group='06'
    Create_Group_Reply='07'
    Add_Group='08'
    Add_Group_Reply = '09'
    Group_Message='10'
    Group_Message_Reply = '11'
    BroadCast_in_Group='12'
    Sync_Users_in_Group='13'
    Sync_Group_Message = '14'
    Sync_BroadCast_in_Group='15'
    Sync_Group_Message_END = '16'
    Update='17'

class Pack(object):
    #数据包格式：STX	time DIV Mode DIV id_send DIV id_recieve DIV content DIV ETX
    STX = '\2'  # 数据包开始标记
    ETX = '\3'  # 数据包结束标记
    DIV = '\31'  # 数据包单元分隔符
    TIME_Format = '%Y-%m-%d %H:%M:%S.%f'
    UNITS_NUM = 5  # 数据包单元数（除去STX ETX DIV）

    def __init__(self, mode=MODE.Message.value, idsend=ID.SERVER.value, idrec=ID.ALL.value, content='', string=''):
        if string == '':
            self.mode = mode
            self.idsend = idsend
            self.idrec = idrec
            self.content = content
            self.time = datetime.datetime.now()
            self.string = self.encode()
        else:
            if string[0] != Pack.STX or string[-1] != Pack.ETX:
                raise ValueError('数据块不闭合 STX ETX缺少')
            string_without_TX = string[1:-1]
            lists = string_without_TX.split(Pack.DIV)
            if len(lists)!=Pack.UNITS_NUM:
                raise ValueError('数据块不完整，单元数错误')
            timestr = lists[0]
            mode = lists[1]
            idsend = lists[2]
            idrec = lists[3]
            content = lists[4]
            self.time = datetime.datetime.strptime(timestr, Pack.TIME_Format)
            self.mode = MODE(mode).value  # ValueError
            self.idsend = idsend
            self.idrec = idrec
            self.content = content
            self.string = string

    def encode(self):
        self.string = Pack.STX + self.time.strftime(
            Pack.TIME_Format) + Pack.DIV + self.mode + Pack.DIV + self.idsend + Pack.DIV + self.idrec + Pack.DIV + self.content + self.ETX
        return self.string