# Chat-Room

## 基本说明

本项目是基于Python实现的简单群聊软件，支持创建用户账号、创建群，支持历史记录的云同步，使用MySQL数据库存储账号信息和历史记录，源代码包含服务器和客户端两部分。服务器部分在server文件夹，客户端部分在client文件夹。

## 配置说明

1. 首先需要更改配置信息，打开server和client文件夹中的config文件，将文件的每一行替换成对应的内容：

   例如，从\server\config.txt中的内容从

>端口号
>最大连接数

​		更改为服务器的对应实际信息

> 8000
> 100

2. 在服务器端建立数据库，连接参数`host='localhost', user="root", passwd="password"`，

   1. 新建数据库`group`，然后在库中建立表`group_list`

      ```mysql
      create table group_list
      (
          pwd  varchar(255) collate utf8_bin default '' not null,
          Name varchar(255) collate utf8_bin default '' not null
              primary key
      );
      ```

   2. 新建数据库`users`，然后在库中建立表`accounts`

      ```mysql
      create table accounts
      (
          ID       varchar(255) collate utf8_bin default '' not null
              primary key,
          password varchar(255) collate utf8_bin default '' not null
      );
      ```

   3. 新建数据库`ip_list`，然后在库中建立表 `black_ip` 和 `white_ip`

      ```mysql
      create table black_ip
      (
          IP varchar(30) charset utf8 default '' null
      );
      
      create table white_ip
      (
          IP varchar(30) charset utf8 default '' null
      );
      ```

   4. 新建空数据库`group_mem`和`history`

   5. 服务器连接数据库的源代码位于`\server\database.py`，可以自行根据需要修改

3. 在服务端和客户端分别运行`main.py`


