# -*- coding: utf-8 -*-

import privateAPI as private
import publicAPI  as public
import errorLogger as error
import analyze100sec
import emailMessanger as email

import sys
import threading
import time
from datetime import datetime

import os, csv

import emailMessanger as email

# TODO エラーを吐いたら通知
# TODO 外部入力を受けたら場合分けして再起動とか

# TODO 再起動後に，直近じゃないデータで計算をして，誤った偏差値から売買判断する事象対策
# TODO 時々生じる大きな変化で損をしている事象への対策
# TODO プログラム開始日時と実行中のログ
class TimerClass(threading.Thread):
    def __init__(self, analyzer):
        threading.Thread.__init__(self)
        self.event = threading.Event()
        self.count = 10
        self.analyzer = analyzer

    def run(self):
        # 売買に使う変数はじめ
        ordered     = False
        boughtTime  = datetime.now()
        soldPrice   = 0.0
        boughtPrice = 0.0
        spread      = 0.0 #best ask と best bid の差

        # 売買に使う変数終わり

        while not self.event.is_set():
            res = public.getBoard()
            # print('--- New Board is received ---')

            # print(res['asks'])
            bids = res['bids']
            asks = res['asks']
            midPrice = res['mid_price']

            bestAsk = asks[0]
            bestBid = bids[0]
            spread  = bestAsk['price'] - bestBid['price']

            now = datetime.now()
            date = now.strftime('%Y-%m-%d')
            time = now.strftime('%H-%M-%S')
            csvtime = now.strftime('%H:%M:%S')

            if not os.path.isdir('./' + date):
                os.mkdir('./' + date)

            if not os.path.isdir('./'+date+'/boards'):
                os.mkdir('./'+date+'/boards')

            if not os.path.isfile('./' + date + '/'  + 'midprices.csv'):
                csvlist = [res['mid_price']]

                f = open('./' + date + '/midprices.csv','w')
                writer = csv.writer(f, lineterminator='\r\n')
                writer.writerow([csvtime,res['mid_price'],bestAsk['price'],bestBid['price'],spread])
                f.close()
            else:
                f = open('./' + date + '/midprices.csv','a')
                writer = csv.writer(f, lineterminator='\r\n')
                writer.writerow([csvtime,res['mid_price'],bestAsk['price'],bestBid['price'],spread])
                f.close()

            csvlist = []

            type = 'ask'
            for ask in (reversed(asks)):
                csvlist.append([ask['price'],ask['size'],type])

            type = 'bid'
            for bid in bids:
                csvlist.append([bid['price'],bid['size'],type])

            # print(csvlist)

            f = open('./' + date + '/boards/' + time + '.csv', 'w')
            writer = csv.writer(f, lineterminator='\r\n')
            writer.writerow(["price","size",'Type'])
            for data in csvlist:
                writer.writerow(data)
            f.close()

            val = self.analyzer.run(midPrice)

            # 売買ロジックはじめ
            # TODO best ask とbest bid の乖離が激しいときは取引しない方がいいのでは？
            # TODO 損切のさせ方（いかにしてリスクとベネフィットを評価するか）

            if val > 2.0 and not ordered:
                # private.sendChildOrder('FX_BTC_JPY',side='SELL', size=0.01)
                print('order: sell')
                boughtTime = now
                ordered = True
                soldPrice = bestBid['price']

                mail = email.Mailer()
                subject = "BitTrader Trade Info!!"
                body = 'SELL: ' + f'{time} value: {val}, {asks[0]},{midPrice},{bids[0]}'
                to_address = "kuzumaki-issei-sk@ynu.jp"
                mail.send(to_address, subject, body)
            elif bestAsk['price'] < soldPrice and ordered:
                # private.sendChildOrder('FX_BTC_JPY',side='BUY', size=0.01)
                print('order: buy')
                boughtTime  = datetime.now()
                ordered = False

                benefit = soldPrice - bestAsk['price']
                soldPrice = 0.0

                mail = email.Mailer()
                subject = "BitTrader Trade Info!!"
                body = 'BUY: ' f'{time} value: {val}, {asks[0]},{midPrice},{bids[0]}, benefit: {benefit}'
                to_address = "kuzumaki-issei-sk@ynu.jp"
                mail.send(to_address, subject, body)

            elif ordered and (now - boughtTime).total_seconds() > 180:
                print('order: buy')
                # private.sendChildOrder('FX_BTC_JPY',side='BUY', size=0.01)
                boughtTime  = datetime.now()
                ordered = False

                benefit = soldPrice - bestAsk['price']
                soldPrice = 0.0

                mail = email.Mailer()
                subject = "BitTrader Trade Info!!"
                body = 'BUY: ' f'{time} value: {val}, {asks[0]},{midPrice},{bids[0]}, benefit: {benefit}'
                to_address = "kuzumaki-issei-sk@ynu.jp"
                mail.send(to_address, subject, body)

            else:
                duration = (now - boughtTime).total_seconds()
                print(f'status: {ordered}, soldPrice: {soldPrice}, spread: {spread}, duration: {duration}')
                pass
            # 売買ロジックおわり

            askmin = asks[0]
            bidmax = bids[0]
            path = './' + date + '/'  + 'analyze100sec.csv'
            if not os.path.isfile(path):
                f = open(path,'w')
            else:
                f = open(path,'a')
            writer = csv.writer(f, lineterminator='\n')
            writer.writerow([csvtime,askmin['price'],midPrice,bidmax['price'],val])
            f.close()

            print(f'{time} value: {val}, {asks[0]},{midPrice},{bids[0]}')

            self.event.wait(10)

    def stop(self):
        self.event.set()

analyzer = analyze100sec.Analyzer()
thread_obj = TimerClass(analyzer)
thread_obj.start()



# bucket = Queue.Queue()
# thread_obj = TimerClass(bucket)
# thread_obj.start()
#
# while True:
#     try:
#         exc = bucket.get(block=False)
#     except Queue.Empty:
#         pass
#     else:
#         exc_type, exc_obj, exc_trace = exc
#         print(exc_type, exc_obj)
#         print(exc_trace)
#     thread_obj.join(0.1)
