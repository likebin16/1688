# -*- coding: utf-8 -*-

import urllib2
from bs4 import BeautifulSoup
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


def getContentOfWebPage(url):
    user_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B137 Safari/601.1'
    headers = {'User-Agent': user_agent}
    req = urllib2.Request(url=url, headers=headers)
    response = urllib2.urlopen(req)
    content = response.read().decode('utf-8', 'ignore')
    return content

# 1688
rootBaseURL = 'http://m.1688.com'

# 所有类目
pageContent = getContentOfWebPage(rootBaseURL + '/page/cateList')
soup = BeautifulSoup(pageContent, 'html.parser')

# 将所有一级类目的URL存入数组
indexCateArray = []
buList = soup.find(attrs='bu-list')
for aTag in buList.findAll('a'):
    indexCateArray.append(aTag.attrs['href'])

print('找到 '+str(len(indexCateArray))+' 项一级类目')

# 取得二级类目
subCateArray = []
for indexCateURL in indexCateArray:
    indexCateContent = getContentOfWebPage(rootBaseURL+indexCateURL)
    indexCateSoup = BeautifulSoup(indexCateContent, 'html.parser')
    subCateList = indexCateSoup.find(attrs='sub-cate-list')
    for aTag in subCateList.findAll('a'):
        subCateArray.append(aTag.attrs['href'])

print('找到 '+str(len(subCateArray))+' 项二级类目')

# 取得三级类目
keyWordsArray = []
for subCateURL in subCateArray:
    subCateContent = getContentOfWebPage(rootBaseURL+subCateURL)
    subCateSoup = BeautifulSoup(subCateContent, 'html.parser')
    thirdCateList = subCateSoup.find(attrs='third-cate-list')
    for aTag in thirdCateList.findAll('a'):
        keyWordsArray.append(aTag.get_text())

print('找到 '+str(len(keyWordsArray))+' 项三级类目')

try:
    filePath = r'searchKeyWords.txt'
    fp = open(filePath, "w+")
    for item in keyWordsArray[:-1]:
        fp.write(item+'\n')
    fp.write(keyWordsArray[-1])  # 写最后一行,不换行
    fp.close()
    print('写入文件成功')
except IOError:
    print("fail to open file")


