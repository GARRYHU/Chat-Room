import Server
import globalvar as glo

__author__ = 'GARRYHu'

# 防火墙设置:https://blog.csdn.net/qq_32740675/article/details/79561707?ops_request_misc=%257B%2522request%255Fid%2522%253A%2522162858150516780262537732%2522%252C%2522scm%2522%253A%252220140713.130102334.pc%255Fall.%2522%257D&request_id=162858150516780262537732&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~first_rank_v2~rank_v29-5-79561707.first_rank_v2_pc_rank_v29&utm_term=python+socket%E8%BF%9E%E6%8E%A5%E5%88%B0%E5%B1%80%E5%9F%9F%E7%BD%91&spm=1018.2226.3001.4187

if __name__ == '__main__':
    glo.init()
    server = Server.Server()
    while True:
        server.wait_connetion()
