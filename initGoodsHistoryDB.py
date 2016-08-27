#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import sqlite3


# 连接商品数据库
goodsDBName = 'goods.db'
if not os.path.exists(goodsDBName):
    print(goodsDBName + ' is not exist.')
    sys.exit(1)
goodsDBConn = sqlite3.connect(goodsDBName)
goodsDBCursor = goodsDBConn.execute("SELECT ID FROM GOODS GROUP BY COMPANY_NAME;")


# 连接商品历史数据库
# 删除原来的db
historyDBName = 'goodsHistory.db'
if os.path.exists(historyDBName):
    os.remove(historyDBName)
# 新建db
historyDBConn = sqlite3.connect(historyDBName)
historyDBCursor = historyDBConn.cursor()
# 建表
historyDBCursor.execute('''CREATE TABLE HISTORY
       (ID TEXT PRIMARY KEY,
        COMPLETED TEXT);''')

# 将从商品表中查询出的商品ID存入商品历史数据库
for row in goodsDBCursor:
    goodsID = row[0]
    try:
        historyDBCursor.execute(
            '''INSERT INTO HISTORY (ID, COMPLETED)
            VALUES (?, ?);''', (goodsID, 'NO')
        )
    except sqlite3.IntegrityError:
         pass  # print("该记录ID已存在")

historyDBConn.commit()

print('完成')

# 关闭连接
historyDBCursor.close()
historyDBConn.close()
goodsDBCursor.close()
goodsDBConn.close()
