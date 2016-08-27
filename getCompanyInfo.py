# -*- coding: utf-8 -*-

import os
import sys
import sqlite3
import urllib2
from bs4 import BeautifulSoup
import time
import socket

socket.setdefaulttimeout(30)

reload(sys)
sys.setdefaultencoding('utf-8')

def getContentOfWebPage(url):
    user_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B137 Safari/601.1'
    headers = {
        'User-Agent': user_agent
    }
    req = urllib2.Request(url=url, headers=headers)
    res = 1
    content = ''
    try:
        response = urllib2.urlopen(req)
        content = response.read().decode('utf-8', 'ignore')
    except:
        res = 0
    return (res, content)


def get_company_id(content):
    res = 1
    memberID = ''
    try:
        subStr = r'"memberId":"'
        headIndex = content.rindex(subStr) + len(subStr)
        tailIndex = content.index(r'"', headIndex)
        memberID = content[headIndex:tailIndex]
    except:
        res = 0
    return (res, memberID)


# 连接搜索历史数据库
historyDBName = 'goodsHistory.db'
if not os.path.exists(historyDBName):
    print('goodsHistory.db is not exist.please run initGoodsHistoryDB.py')
    sys.exit(1)

historyDBConn = sqlite3.connect(historyDBName)
historyDBCursor = historyDBConn.execute(
        "SELECT ID FROM HISTORY WHERE COMPLETED='NO';"
)

# 连接公司信息数据库
companyDBName = 'company.db'
companyDBConn = sqlite3.connect(companyDBName)
companyDBCursor = companyDBConn.cursor()
# 建表
companyDBCursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS COMPANY (
        ID TEXT PRIMARY KEY  NOT NULL ,
        NAME TEXT ,
        OPERATION_MODE TEXT ,
        DISTRICT TEXT ,
        PRODUCT TEXT ,
        PRODUCT_QUANTITY TEXT ,
        CONTACT TEXT ,
        CONTACT_ADDRESS TEXT ,
        COORDINATE TEXT ,
        PHONE_NUMBER TEXT ,
        OFFICE_NUMBER TEXT ,
        CHENG_XIN_TONG TEXT ,
        AUTH_TYPE TEXT ,
        REGIS_NAME TEXT ,
        REGIS_ADDRESS TEXT ,
        REGIS_TIME TEXT ,
        REGIS_SCOPE TEXT ,
        REGIS_NUMBER TEXT ,
        REGIS_LEGAL_REPRESENTATIVE TEXT ,
        REGIS_TYPE TEXT ,
        REGIS_OPERATION_PERIOD TEXT ,
        REGIS_REGISTRATION_AUTHORITY TEXT
        );'''
)

# 基本信息：基本信息可能没有(奇葩,比如http://m.1688.com/winport/company/b2b-2417604927.html)
#           这时公司名称可以用注册信息里的公司名称
# 	公司名称 NAME
# 	经营模式 OPERATION_MODE
# 	所在地区 DISTRICT
# 	主营产品 PRODUCT
# 	商品数量 PRODUCT_QUANTITY
# 	联系人	CONTACT
# 	联系地址	CONTACT_ADDRESS
# 	坐标	    COORDINATE
# 	手机号	PHONE_NUMBER
# 	座机号	OFFICE_NUMBER
# 认证信息：
# 	诚信通	CHENG_XIN_TONG
# 	AUTH_TYPE	CNA	企业名称认证
# 			    AV	企业身份认证
# 工商注册信息：  只有通过企业身份认证的才有工商注册信息
# 		公司名称	REGIS_NAME
# 		经营地址	REGIS_ADDRESS
# 		成立日期	REGIS_TIME
# 		经营范围	REGIS_SCOPE
# 		注册号	REGIS_NUMBER
# 		法人代表	REGIS_LEGAL_REPRESENTATIVE
# 		企业类型	REGIS_TYPE
# 		营业期限	REGIS_OPERATION_PERIOD
# 		登记机关 REGIS_REGISTRATION_AUTHORITY

# 1688
rootBaseURL = 'http://m.1688.com'

for row in historyDBCursor.fetchall():
    goodID = row[0]
    # 拿到商品详情网页,从中取得公司ID
    goodsDetailURL = rootBaseURL + r'/offer/%s.html' % goodID
    (res, pageContent) = getContentOfWebPage(goodsDetailURL)
    if res is not 1:
        print('ERROR: ' + goodsDetailURL)
        continue
    goodsDetailSoup = BeautifulSoup(pageContent, 'html.parser')
    (res, companyID) = get_company_id(pageContent)
    if res is not 1:
        continue
    # 拿到公司信息网页
    companyURL = rootBaseURL + r'/winport/company/%s.html' % companyID
    (res, companyContent) = getContentOfWebPage(companyURL)
    if res is not 1:
        print('ERROR: ' + companyURL)
        continue
    companySoup = BeautifulSoup(companyContent, 'html.parser')
    # 初始化字段
    NAME = None
    OPERATION_MODE = None
    DISTRICT = None
    PRODUCT = None
    PRODUCT_QUANTITY = None
    CONTACT = None
    CONTACT_ADDRESS = None
    COORDINATE = None
    CHENG_XIN_TONG = None
    AUTH_TYPE = None
    REGIS_NAME = None
    REGIS_ADDRESS = None
    REGIS_TIME = None
    REGIS_SCOPE = None
    REGIS_NUMBER = None
    REGIS_LEGAL_REPRESENTATIVE = None
    REGIS_TYPE = None
    REGIS_OPERATION_PERIOD = None
    REGIS_REGISTRATION_AUTHORITY = None
    PHONE_NUMBER = None
    OFFICE_NUMBER = None

    # 如果有基本信息
    if companySoup.find('div', attrs={'class': 'archive-baseInfo-container'}):
        try:
            # 公司信息
            baseInfoDiv = companySoup.find(
                'div', attrs={'class': 'archive-baseInfo-companyInfo'}
            )
            for div in baseInfoDiv.find_all(attrs={'class': 'info-container'}):
                emString = div.em.get_text().strip()
                if u'公司名称' in emString:
                    NAME = div.span.string
                elif u'经营模式' in emString:
                    OPERATION_MODE = div.span.string
                elif u'所在地区' in emString:
                    DISTRICT = div.span.string
                elif u'主营产品' in emString:
                    PRODUCT = div.span.string
                elif u'商品数量' in emString:
                    PRODUCT_QUANTITY = div.span.string

            # 联系人信息
            contactInfoDiv = companySoup.find(
                'div', attrs={'class': 'archive-baseInfo-contactInfo'}
            )
            if contactInfoDiv is not None:
                for div in contactInfoDiv.find_all(
                        attrs={'class': 'info-container'}
                ):
                    emString = div.em.get_text().strip()
                    if u'联系人' in emString:
                        CONTACT = div.span.string
                    elif u'联系地址' in emString:
                        CONTACT_ADDRESS = div.span.string

            # 坐标
            mapDiv = companySoup.find(
                'div', id='map-content'
            )
            if mapDiv is not None:
                COORDINATE = mapDiv.attrs['data-geoinfo']
        except:
            print('ERROR!!!!!!: ' + companyURL)
            sys.exit(1)

    # 如果有认证信息
    authinfoContainer = companySoup.find(
        'div', attrs={'class': 'archive-authinfo-container'}
    )
    if authinfoContainer is not None:
        try:
            # 诚信通
            cxtDiv = authinfoContainer.find(
                'div', attrs={'class': 'auto-summary-div tp-logo'}
            )
            if cxtDiv is not None:
                CHENG_XIN_TONG = cxtDiv.em.string.strip()

            # 认证类型
            avAuthTypeDiv = authinfoContainer.find(
                'div', attrs={'class': 'auto-summary-div auth-type av'}
            )
            if avAuthTypeDiv is not None:
                AUTH_TYPE = 'AV'
            cnaAuthTypeDiv = authinfoContainer.find(
                'div', attrs={'class': 'auto-summary-div auth-type cna'}
            )
            if cnaAuthTypeDiv is not None:
                AUTH_TYPE = 'CNA'

            # 工商注册信息
            authinfoModDiv = authinfoContainer.find(
                'div', attrs={'class': 'archive-authinfo-mod'}
            )
            if authinfoModDiv is not None:
                for div in authinfoContainer.find_all(
                        attrs={'class': 'info-container'}
                ):
                    emString = div.em.get_text().strip()
                    if u'公司名称' in emString:
                        REGIS_NAME = div.span.string
                    elif u'经营地址' in emString:
                        REGIS_ADDRESS = div.span.string
                    elif u'成立日期' in emString:
                        REGIS_TIME = div.span.string
                    elif u'经营范围' in emString:
                        REGIS_SCOPE = div.span.string
                    elif u'注册号' in emString:
                        REGIS_NUMBER = div.span.string
                    elif u'法人代表' in emString:
                        REGIS_LEGAL_REPRESENTATIVE = div.span.string
                    elif u'企业类型' in emString:
                        REGIS_TYPE = div.span.string
                    elif u'营业期限' in emString:
                        REGIS_OPERATION_PERIOD = div.span.string
                    elif u'登记机关' in emString:
                        REGIS_REGISTRATION_AUTHORITY = div.span.string
        except:
            print('ERROR!!!!!!: ' + companyURL)
            sys.exit(1)

    # 手机号 办公电话号码
    archiveSheetDiv = companySoup.find(
        'div', attrs={'class': 'archive-sheet'}
    )
    if archiveSheetDiv is not None:
        i = 0
        for phoneDiv in archiveSheetDiv.findAll(
            'div', attrs={'class': 'archive-sheet-item phone'}
        ):
            if i == 0:
                PHONE_NUMBER = phoneDiv.string.strip()
                i += 1
            elif i == 1:
                OFFICE_NUMBER = phoneDiv.string.strip()

    # 写入数据库
    try:
        companyDBCursor.execute(
        '''INSERT INTO COMPANY (
          ID ,
          NAME ,
          OPERATION_MODE ,
          DISTRICT ,
          PRODUCT ,
          PRODUCT_QUANTITY ,
          CONTACT ,
          CONTACT_ADDRESS ,
          COORDINATE ,
          PHONE_NUMBER ,
          OFFICE_NUMBER ,
          CHENG_XIN_TONG ,
          AUTH_TYPE ,
          REGIS_NAME ,
          REGIS_ADDRESS ,
          REGIS_TIME ,
          REGIS_SCOPE ,
          REGIS_NUMBER ,
          REGIS_LEGAL_REPRESENTATIVE ,
          REGIS_TYPE ,
          REGIS_OPERATION_PERIOD ,
          REGIS_REGISTRATION_AUTHORITY
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);''', (
            companyID,
            NAME,
            OPERATION_MODE,
            DISTRICT,
            PRODUCT,
            PRODUCT_QUANTITY,
            CONTACT,
            CONTACT_ADDRESS,
            COORDINATE,
            PHONE_NUMBER,
            OFFICE_NUMBER,
            CHENG_XIN_TONG,
            AUTH_TYPE,
            REGIS_NAME,
            REGIS_ADDRESS,
            REGIS_TIME,
            REGIS_SCOPE,
            REGIS_NUMBER,
            REGIS_LEGAL_REPRESENTATIVE,
            REGIS_TYPE,
            REGIS_OPERATION_PERIOD,
            REGIS_REGISTRATION_AUTHORITY
            )
        )
    except sqlite3.IntegrityError:
        pass  # 该记录ID已存在

    # 提交
    companyDBConn.commit()
    print('完成: ' + companyID)

    # 成功搜索完一个公司,更新一下history
    historyDBCursor.execute('''UPDATE HISTORY SET COMPLETED='YES'
      WHERE ID=?;''', (goodID,))
    historyDBConn.commit()

    # print(NAME)
    # print(OPERATION_MODE)
    # print(DISTRICT)
    # print(PRODUCT)
    # print(PRODUCT_QUANTITY)
    # print(CONTACT)
    # print(CONTACT_ADDRESS)
    # print(COORDINATE)
    # print(CHENG_XIN_TONG)
    # print(AUTH_TYPE)
    # print(REGIS_NAME)
    # print(REGIS_ADDRESS)
    # print(REGIS_TIME)
    # print(REGIS_SCOPE)
    # print(REGIS_NUMBER)
    # print(REGIS_LEGAL_REPRESENTATIVE)
    # print(REGIS_TYPE)
    # print(REGIS_OPERATION_PERIOD)
    # print(REGIS_REGISTRATION_AUTHORITY)
    # print(PHONE_NUMBER)
    # print(OFFICE_NUMBER)

# 关闭数据库连接
historyDBCursor.close()
historyDBConn.close()
companyDBCursor.close()
companyDBConn.close()

