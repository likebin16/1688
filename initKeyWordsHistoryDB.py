# -*- coding: utf-8 -*-

import os
import sqlite3

# 读取关键字列表
keyWordsArray = []
try:
    for line in open('searchKeyWords.txt'):
        keyWordsArray.append(line)
    print('读取文件成功')
except IOError:
    print("fail to open file")

# 删除原来的db
dbName = 'keyWordsHistory.db'
if os.path.exists(dbName):
    os.remove(dbName)

# 新建db
sqliteConn = sqlite3.connect(dbName)
sqliteCursor = sqliteConn.cursor()

# 建表
sqliteCursor.execute('''CREATE TABLE HISTORY
       (KEYWORD TEXT PRIMARY KEY,
        COMPLETED TEXT);''')

# 插入数据
for keyWord in keyWordsArray:
    try:
        sqliteCursor.execute(
            '''INSERT INTO HISTORY (KEYWORD, COMPLETED)
            VALUES ('%s', '%s');''' % (keyWord, 'NO')
        )
    except sqlite3.IntegrityError:
         pass  # print("该记录ID已存在")

# 提交事务
sqliteConn.commit()

# 关闭游标和连接
sqliteCursor.close()
sqliteConn.close()
