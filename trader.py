import websocket
import json
from datetime import datetime as dt
from datetime import timedelta as td
from datetime import timezone as tz
import dateutil.parser
import matplotlib.pyplot as plt
from statistics import mean, median, variance, stdev
import threading

from estimaters import sd_method

# Global variables: start
histId = 0
tradeInfo = {'isExist': False, 'price': 0.0, 'buy': False}
# Global variables: end

def appendData(time, bestAsk, bestBid):
    # history.append([time,bestAsk,bestBid])
    # if len(history) > histSize+1:
    #     history.pop(0)
    #     print(history[histSize][0]-history[0][0])
    # print(mean(row[1] for row in history))
    return history

def on_message_ticker_fx(ws, message):
    global histId
    global tradeInfo

    print("Ticker")

    # ticker = json.loads(message)
    # rpc = ticker['jsonrpc']
    # mtd = ticker['method']
    # msg = ticker['params']['message']
    # timestamp = msg['timestamp']
    # tickId = msg['tick_id']
    # bestBid = msg['best_bid']
    # besdBidSize = msg['best_bid_size']
    # bestAsk = msg['best_ask']
    # bestAskSize = msg['best_ask_size']
    # totalBidDepth = msg['total_bid_depth']
    # totalAskDepth = msg['total_ask_depth']
    # ltp = msg['ltp']
    # volume = msg['volume']
    # volumeByProduct = msg['volume_by_product']
    # tickTime = dateutil.parser.parse(timestamp)
    # spread = int(bestAsk) - int(bestBid)
    # # appendData(tickTime, int(bestAsk), int(bestBid))
    # # print(history[len(history)-1])
    # print(f'timestamp: {tickTime}, best bid: {bestBid}, best ask: {bestAsk}, spread: {spread}')
    # # print(len(history))
    #
    # x.append(tickTime)
    # y1.append(bestBid)
    # y2.append(bestAsk)
    #
    # histId +=1
    # if histId % 10 == 0:
    #     fig.clf()
    #     plt.plot(x, y1, color='b', label='best bid')
    #     plt.plot(x, y2, color='r', label='best ask')
    #     now = dt.now(tz.utc)
    #     before60s=now - td(minutes=1)
    #     plt.xlim([before60s, now])
    #     plt.ylim([bestAsk-300,bestAsk+300])
    #     plt.legend()
    #     # ax.set_xlim((x.min(), x.max()))
    #     plt.pause(.0001)

def on_message_board(ws, message):
    # example of the message
    # {
    # 'jsonrpc': '2.0',
    # 'method': 'channelMessage',
    # 'params': {
    #     'channel': 'lightning_board_snapshot_FX_BTC_JPY',
    #     'message': {
    #         'mid_price': 760896,
    #         'bids': [
    #         {
    #             'price': 760891,
    #             'size': 0.04995
    #         },  ...,
    #         {
    #             'price': 760292,
    #             'size': 0.03
    #         }],
    #
    #         'asks': [
    #         {
    #             'price': 760902, 'size': 0.00055
    #         }, {
    #             'price': 760910, 'size': 0.02185
    #         }, {
    #             'price': 760911, 'size': 0.03
    #         }, {
    #             'price': 760912, 'size': 1.15889019
    #         }, ...,{
    #             'price': 761435, 'size': 0.028
    #         }]
    #     }
    # }}

    print("Board")

    rcv = json.loads(message)
    # print(rcv)

def on_message_board_snapshot(ws, message):
    # example of the message
    # {
    # 'jsonrpc': '2.0',
    # 'method': 'channelMessage',
    # 'params': {
    #     'channel': 'lightning_board_FX_BTC_JPY',
    #     'message': {
    #         'mid_price': 760797,
    #         'bids': [],
    #         'asks': [
    #             {
    #                 'price': 763337,
    #                 'size': 0.1},
    #             {
    #                 'price': 760796,
    #                 'size': 0},
    #             {
    #                 'price': 760799,
    #                 'size': 0},
    #             {
    #                 'price': 760800,
    #                 'size': 8.80153769
    #             }]
    #         }
    #     }
    # }

    print("Snapshot")

    rcv = json.loads(message)
    # print(rcv)

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open_ticker_fx(ws):
    ws.send(json.dumps({"method": "subscribe", "params": {"channel": "lightning_ticker_FX_BTC_JPY"}}))

def on_open_board_snapshot(ws):
    ws.send(json.dumps({"method": "subscribe", "params": {"channel": "lightning_board_snapshot_FX_BTC_JPY"}}))

def on_open_board(ws):
    ws.send(json.dumps({"method": "subscribe", "params": {"channel": "lightning_board_FX_BTC_JPY"}}))

class WebSocketSnapshot(threading.Thread):
    """docstring for WebSocketTicker."""
    def run(self):
        websocket.enableTrace(True)
        ws_board_snapshot = websocket.WebSocketApp("wss://ws.lightstream.bitflyer.com/json-rpc",
                                  on_message = on_message_board_snapshot,
                                  on_error = on_error,
                                  on_close = on_close)
        ws_board_snapshot.on_open = on_open_board_snapshot
        ws_board_snapshot.run_forever()

class WebSocketBoard(threading.Thread):
    """docstring for WebSocketTicker."""
    def run(self):
        websocket.enableTrace(True)
        ws_board = websocket.WebSocketApp("wss://ws.lightstream.bitflyer.com/json-rpc",
                                  on_message = on_message_board,
                                  on_error = on_error,
                                  on_close = on_close)
        ws_board.on_open = on_open_board
        ws_board.run_forever()

class WebSocketTicker(threading.Thread):
    """docstring for WebSocketTicker."""
    def run(self):
        websocket.enableTrace(True)
        ws = websocket.WebSocketApp("wss://ws.lightstream.bitflyer.com/json-rpc",
                                  on_message = on_message_ticker_fx,
                                  on_error = on_error,
                                  on_close = on_close)
        ws.on_open = on_open_ticker_fx
        ws.run_forever()

if __name__ == "__main__":
    histSize = 100
    history = []

    fig, ax = plt.subplots(1,1)
    x= []
    y1 = []
    y2 = []

    ws0 = WebSocketTicker()
    ws0.start()

    ws1 = WebSocketSnapshot()
    ws1.start()

    ws2 = WebSocketBoard()
    ws2.start()
