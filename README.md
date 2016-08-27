# 1688
扒取 1688 商家数据

##步骤:<br>
1. 运行 getSearchKeyWords.py, 得到 searchKeyWords.txt 关键字列表<br>
2. 运行 initKeyWordsHistoryDB.py, 得到 keyWordsHistory.db 初始化关键字搜索的历史库<br>
3. 运行 getGoodsList.py, 得到 goods.db 商品库<br>
4. 运行 initGoodsHistory.db 得到 goodsHistory.db 初始化商品搜索历史库<br>
5. 运行 getCompanyInfo.py 得到最终的 company.db 公司信息库<br>

还蛮好玩的，拿到了30万家公司的信息，不足点就是没开多线程，所以第5步太慢了...<br>
