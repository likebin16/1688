# -*- coding: utf-8 -*-

import urllib2
import urllib
from bs4 import BeautifulSoup
import json
import cookielib
import sqlite3
import time
import os
import sys
import socket

socket.setdefaulttimeout(30)

reload(sys)
sys.setdefaultencoding('utf-8')


def get_search_page_url(keyWord):
    res = 1
    pageURL = ''
    try:
        searchBaseURL = rootBaseURL + '/page/search.html?keywords='
        searchKeyWordsURL = searchBaseURL + urllib2.quote(keyWord)
        searchPageContent = getContentOfWebPage(searchKeyWordsURL)
        searchPageSoup = BeautifulSoup(searchPageContent, 'html.parser')
        pageURL = searchPageSoup.head.find('link', attrs={'rel':
                                                              'canonical'}).attrs['href']
    except:
        res = 0
    return (res, pageURL)


def getContentOfWebPage(url):
    user_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B137 Safari/601.1'
    headers = {
        'User-Agent': user_agent
        # 'Connection': 'Keep-Alive'
    }
    req = urllib2.Request(url=url, headers=headers)
    response = urllib2.urlopen(req)
    content = response.read().decode('utf-8', 'ignore')
    return content


def get_goods_list(url, data, opener):
    user_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B137 Safari/601.1'
    url_encode_data = urllib.urlencode(data)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        # 'Connection': 'Keep-Alive',
        'User-Agent': user_agent
    }
    req = urllib2.Request(url=url, data=url_encode_data, headers=headers)
    content = ''
    res = 1
    try:
        content = opener.open(req).read()
    except:
        res = 0
    finally:
        opener.close()
    return (res, content)


def create_url_opener():
    cookie = cookielib.CookieJar()
    handler = urllib2.HTTPCookieProcessor(cookie)
    opener = urllib2.build_opener(handler)
    return opener


def get_csrf(url):
    res = 1
    csrf = ''
    try:
        response = opener.open(url).read()
        subStr = r'"csrf":"'
        headIndex = response.rindex(subStr) + len(subStr)
        tailIndex = response.index(r'"', headIndex)
        csrf = response[headIndex:tailIndex]
    except:
        res = 0
    return (res, csrf)

# 1688
rootBaseURL = 'http://m.1688.com'

# 连接搜索历史数据库
historyDBName = 'keyWordsHistory.db'
if not os.path.exists(historyDBName):
    print('keyWordsHistory.db is not exist.please run initKeyWordsHistoryDB.py')
    sys.exit(1)

historyDBConn = sqlite3.connect('keyWordsHistory.db')
historyDBCursor = historyDBConn.execute(
        "SELECT KEYWORD FROM HISTORY WHERE COMPLETED='NO';"
)

# 连接商品数据库
goodsDBConn = sqlite3.connect('goods.db')
goodsDBCursor = goodsDBConn.cursor()
# 建表
goodsDBCursor.execute('''CREATE TABLE IF NOT EXISTS GOODS
       (ID TEXT PRIMARY KEY  NOT NULL,
       SIMPLE_SUBJECT TEXT  NOT NULL,
       COMPANY_NAME TEXT NOT NULL);''')


for row in historyDBCursor:
    keyWord = row[0].encode('utf-8')
    print('开始搜索关键字: ' + keyWord)
    opener = create_url_opener()
    (res, searchPageURL) = get_search_page_url(keyWord)
    if not res == 1:
        print('有异常,等待10秒')
        time.sleep(10)
        continue

    # 取得CSRF
    (res, csrf) = get_csrf(searchPageURL)
    if not res == 1:
        print('有异常,等待10秒')
        time.sleep(10)
        continue

    beginPage = 1
    pageSize = 100

    while True:
        wing_navigate_options = {
            "data": {
                "type": "offer",
                "keywords": keyWord,
                "beginPage": beginPage,
                "pageSize": pageSize,
                "offset": 1,
                "sortType": "pop"  # 综合:pop 销量:booked 价格:price
            }
        }
        # 请求参数
        requestParam = {
            "_csrf": csrf,
            "__wing_navigate_type": "action",
            "__wing_navigate_url": "search:pages/search/offerresult",
            "__wing_navigate_options": json.dumps(wing_navigate_options)
        }
        # 获得带有商品列表的JSON串
        (res, goodsListJsonStr) = get_goods_list(
            searchPageURL.encode('utf-8'),
            requestParam,
            opener
        )
        if not res == 1:
            print('有异常,等待10秒')
            time.sleep(10)
            continue

        # 解析JSON
        goodsList = json.loads(goodsListJsonStr)

        # JSON中没有offers,说明商品列表已经全请求完了
        if not goodsList['data'].has_key('offers'):
            print('关键字搜索完毕: ' + keyWord)
            break

        for good in goodsList['data']['offers']:
            try:
                goodsDBCursor.execute(
                    '''INSERT INTO GOODS (ID, SIMPLE_SUBJECT, COMPANY_NAME)
                    VALUES (?, ?, ?);''', (
                            good['id'],
                            good['simpleSubject'],
                            good['companyName']
                        )
                )
            except sqlite3.IntegrityError:
                pass  # print("该记录ID已存在: " + good['id'])

        # 提交事务
        goodsDBConn.commit()
        # 页数加1
        beginPage += 1
        print('插入了 ' + str(len(goodsList['data']['offers'])) + ' 条记录')

    # 成功搜索完一个关键字,更新一下history
    historyDBCursor.execute('''UPDATE HISTORY SET COMPLETED='YES'
      WHERE KEYWORD=?;''', (keyWord.decode(),))
    historyDBConn.commit()

# 关闭连接
goodsDBCursor.close()
goodsDBConn.close()
historyDBCursor.close()
historyDBConn.close()




