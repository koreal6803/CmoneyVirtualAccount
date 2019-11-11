import requests
import json
import re
import time
import pandas as pd
import json
import numpy as np

class VirtualStockAccount():

    def __init__(self, email, password, wait_time=1):

        """
        輸入帳號(email)密碼(password)來登入，並設定每個request的延遲時間是wait_time

        """

        self.ses = requests.Session()
        res = self.ses.get('https://www.cmoney.tw/member/login/')
        self.wait_time = wait_time

        # get view state
        viewstate = re.search( 'VIEWSTATE"\s+value=.*=', res.text )
        viewstate = viewstate.group()

        # get eventvalidation
        eventvalidation = re.search( 'EVENTVALIDATION"\s+value=.*\w', res.text )
        eventvalidation = eventvalidation.group( )

        time.sleep(self.wait_time)

        res = self.ses.post('https://www.cmoney.tw/member/login/', {
                '__VIEWSTATE': viewstate[18:],
            '__EVENTVALIDATION': eventvalidation[24:],
            'ctl00$ContentPlaceHolder1$account': email,
            'ctl00$ContentPlaceHolder1$pw': password,
            'ctl00$ContentPlaceHolder1$loginBtn': '登入',
            'ctl00$ContentPlaceHolder1$check': 'on',
        })

        time.sleep(self.wait_time)

        res = self.ses.get('https://www.cmoney.tw/vt/main-page.aspx')

        aids = re.findall('aid=[\d]*', res.text )
        print(aids)
        aids = [a.split('=')[1] for a in aids]
        aids = [a for a in aids if a.isdigit()]
        self.aids = aids
        if self.aids:
            self.aid = aids[0]
        else:
            raise Exception('Cannot open account due to incorrect account name or password')
        print('accounts', aids)
        print('current account', self.aid)

    def get_price(self, sid):

        """
          輸入sid='1101'，會拿到以下的資料：
           {'StockInfo': {'Commkey': '1101',
          'Name': '台泥',
          'MarketType': 2,
          'RefPrice': 42.9,
          'CeilPrice': 47.15,
          'FloorPrice': 38.65,
          'SalePrice': 43.1,
          'TotalQty': 8665,
          'DecimalPoint': 1,
          'LowPr': 42.6,
          'BuyPr1': 43.05,
          'SellPr1': 43.1,
          'BuyPr2': 43.0,
          'SellPr2': 43.15,
          'BuyPr3': 42.95,
          'SellPr3': 43.2,
          'BuyPr4': 42.9,
          'SellPr4': 43.25,
          'BuyPr5': 42.85,
          'SellPr5': 43.3,
          'BuyQty1': 73.0,
          'SellQty1': 43.0,
          'BuyQty2': 459.0,
          'SellQty2': 42.0,
          'BuyQty3': 111.0,
          'SellQty3': 178.0,
          'BuyQty4': 169.0,
          'SellQty4': 120.0,
          'BuyQty5': 46.0,
          'SellQty5': 230.0,
          'DealTime': '2018-08-22T11:40:53',
          'OrderTime': '2018-08-22T11:40:53'},
         'SalePrice': '43.1',
         'IsWarrant': False}
        """
        res = self.ses.get('https://www.cmoney.tw/vt/ashx/HandlerGetStockPrice.ashx', params={
            'q': sid,
            'accountType': 1,
            'isSDAndSell': 'false',
            })
        return json.loads(res.text)

    def buy(self, sid, quantity, price=None, leverage=False):

        """
        購買兩張台泥股票:
        例如sid='1101', quantity=2
        假如沒有輸入price就是以當前價格買入
        假如輸入了price就是限價買入
        """

        if price is None:
            price = '漲停'
            time.sleep(self.wait_time)
            
        tradekind = 'cd' if leverage else 'c'

        # act: NewEntrust
        # aid: 578325
        # stock: 1101
        # price: 漲停
        # ordqty: 1
        # tradekind: c
        # type: b
        # hasWarrant: true
        # _: 1572344098102
        res = self.ses.get('https://www.cmoney.tw/vt/ashx/userset.ashx', params={
            'act': 'NewEntrust',
            'aid': self.aid,
            'stock': sid,
            'price': price,
            'ordqty': quantity,
            'tradekind': tradekind,
            'type': 'b',
            'hasWarrant': 'true',
        })

    def sell(self, sid, quantity, price=None, leverage=False):

        """
        賣出兩張台泥股票:
        例如sid='1101', quantity=2
        假如沒有輸入price就是以當前價格買入
        假如輸入了price就是限價買入
        """

        if price is None:
            price = '跌停'
            time.sleep(self.wait_time)
            
        tradekind = 'sd' if leverage else 'c'

        res = self.ses.get('https://www.cmoney.tw/vt/ashx/userset.ashx', params={
            'act': 'NewEntrust',
            'aid': self.aid,
            'stock': sid,
            'price': price,
            'ordqty': quantity,
            'tradekind': tradekind,
            'type': 's',
            'hasWarrant': 'true',
        })

    def status(self):

        """
        查看目前account的狀態：
        [{'Id': '1101',
          'Name': '台泥',
          'TkT': '現股',
          'NowPr': '43.05',
          'DeAvgPr': '43.20',
          'IQty': '1',
          'IncomeLoss': '-402',
          'Ratio': '-0.93',
          'Cost': '43,200.00',
          'ShowCost': '43,200.00',
          'TodayQty': '0',
          'BoardLostSize': '1000',
          'IsWarrant': '0'}]
        """

        res = self.ses.get('https://www.cmoney.tw/vt/ashx/accountdata.ashx', params={
            'act': 'InventoryDetail',
            'aid': self.aid,
        })

        return json.loads(res.text)

    def sell_all(self):

        """將所有的股票做即刻賣出的動作"""

        acc = self.status()
        time.sleep(self.wait_time)
        for s in acc:
            print('sell ', s['Id'], s['IQty'])
            self.sell(s['Id'], s['IQty'])
            time.sleep(self.wait_time)

    def buy_list(self, s, leverage=False):

        """
        將清單中的股票即刻買入的動作，其中s為一個dictionary或series，
        例如
        以字典表示：

        s = {
            '1101': 2,
            '2330': 1,
        }

        或是以pandas series表示：

        1101    2
        2330    1
        dtype: int64

        兩種都可以，假如數字為負號，則會進行賣出的動作
        """

        for sid, q in s.items():
            print('buy ', int(sid.split()[0]), q, 'leverage', leverage)
            if q > 0:

                self.buy(sid.split()[0], int(q), leverage=leverage)
            elif q < 0:
                self.sell(sid.split()[0], int(abs(q)), leverage=leverage)
            time.sleep(self.wait_time)

    def get_orders(self):

        """拿到當下的委託"""

        res = self.ses.get('https://www.cmoney.tw/vt/ashx/accountdata.ashx', params={
            'act': 'EntrustQuery',
            'aid': self.aid,
        })

        return json.loads(res.text)

    def cancel_all_orders(self):

        """清空當下的委託"""

        orders = self.get_orders()
        time.sleep(self.wait_time)
        for o in orders:
            print(o['Id'])
            if o['CanDel'] == '1':
                res = self.ses.get('https://www.cmoney.tw/vt/ashx/accountdata.ashx', params={
                    'act': 'DeleteEntrust',
                    'aid': self.aid,
                    'GroupId': 0,
                    'OrdNo': o['CNo'],
                })

                time.sleep(self.wait_time)

    def rebalance(self, newlist, leverage=False):

        """
        將持股更新成newlist，newlist的結構可以參考buy_list的input，是一樣的。
        """

        newlist = pd.Series(newlist)
        status = self.status()
        oldlist = pd.Series({s['Id']:s['IQty'] for s in status}).astype(int)
        newlist = newlist.reindex(oldlist.index | newlist.index).fillna(0)
        oldlist = oldlist.reindex(oldlist.index | newlist.index).fillna(0)

        self.buy_list(newlist - oldlist, leverage)

    def info(self):

        res = self.ses.get('https://www.cmoney.tw/vt/ashx/accountdata.ashx?act=AccountInfo&aid='+self.aid+'&_=1572343162391')


        account_info = json.loads(res.text)
        return account_info

    def calculate_weight(self, position, lowest_fee=20, discount=1, add_cost=10, short=False):

        # get total money
        account_info = self.info()
        money = int(account_info['AllAssets'].replace(',', ''))

        print('total money', money)

        # get price of the stock
        import time
        infos = {}
        if isinstance(position, pd.DataFrame):
            slist = position.iloc[-1][(position.iloc[-1] != 0)].index.tolist()
        elif isinstance(position, pd.Series):
            slist = position[(position != 0)].index.tolist()
        elif isinstance(position, list):
            slist = position
        else:
            raise Exception("type of position should be pd.Series or list")

        for sid in slist:
            print(sid)
            infos[sid] = self.get_price(sid) # RefPrice
            time.sleep(2)

        # format dataframe and series
        price = pd.Series({sid:info['StockInfo']['RefPrice'] for sid, info in infos.items() if info is not None})
        none_stock_ids = [sid for sid, info in infos.items() if info is None]
        if none_stock_ids:
            print('**WARRN: there are stock cannot find info', none_stock_ids)

        stock_list = price.dropna().transpose()

        # rebalance stocks
        while (money / len(stock_list)) < (lowest_fee - add_cost) * 1000 / 1.425 / discount:
            stock_list = stock_list.loc[stock_list != stock_list.max()]

        while True:
            invest_amount = (money / len(stock_list))
            ret = np.floor(invest_amount / stock_list / 1000)

            if (ret == 0).any():
                stock_list = stock_list.loc[stock_list != stock_list.max()]
            else:
                break
                
        if short:
            ret = -ret
            
        ret.to_csv('position' + str(self.aid) + '.csv')
        slist = ret.to_dict()
        return slist

    def sync(self, *arg1, short=False, **arg2):
        slist = self.calculate_weight(*arg1, short=short, **arg2)
        self.rebalance(slist, leverage=short)

