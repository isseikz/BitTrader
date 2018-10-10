import websocket
import json
from datetime import datetime as dt
from datetime import timedelta as td
from datetime import timezone as tz
import dateutil.parser

import matplotlib.pyplot as plt

from statistics import mean, median, variance, stdev


# Global variables: start
histId = 0
# Global variables: end

def appendData(time, bestAsk, bestBid):
    # history.append([time,bestAsk,bestBid])
    # if len(history) > histSize+1:
    #     history.pop(0)
    #     print(history[histSize][0]-history[0][0])
    # print(mean(row[1] for row in history))
    return history

def on_message(ws, message):
    global histId

    ticker = json.loads(message)
    # rpc = ticker['jsonrpc']
    # mtd = ticker['method']
    msg = ticker['params']['message']
    timestamp = msg['timestamp']
    # tickId = msg['tick_id']
    bestBid = msg['best_bid']
    # besdBidSize = msg['best_bid_size']
    bestAsk = msg['best_ask']
    # bestAskSize = msg['best_ask_size']
    # totalBidDepth = msg['total_bid_depth']
    # totalAskDepth = msg['total_ask_depth']
    # ltp = msg['ltp']
    # volume = msg['volume']
    # volumeByProduct = msg['volume_by_product']
    tickTime = dateutil.parser.parse(timestamp)
    spread = int(bestAsk) - int(bestBid)
    # appendData(tickTime, int(bestAsk), int(bestBid))
    # print(history[len(history)-1])
    # print(f'timestamp: {tickTime}, best bid: {bestBid}, best ask: {bestAsk}, spread: {spread}')
    # print(len(history))

    x.append(tickTime)
    y1.append(bestBid)
    y2.append(bestAsk)

    histId +=1
    if histId % 10 == 0:
        fig.clf()
        plt.plot(x, y1, color='b', label='best bid')
        plt.plot(x, y2, color='r', label='best ask')
        now = dt.now(tz.utc)
        before60s=now - td(minutes=1)
        plt.xlim([before60s, now])
        plt.ylim([bestAsk-300,bestAsk+300])
        plt.legend()
        # ax.set_xlim((x.min(), x.max()))
        plt.pause(.0001)

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    ws.send(json.dumps({"method": "subscribe", "params": {"channel": "lightning_ticker_FX_BTC_JPY"}}))


if __name__ == "__main__":
    histSize = 100
    history = []

    fig, ax = plt.subplots(1,1)
    x= []
    y1 = []
    y2 = []

    websocket.enableTrace(True)
    # ws = websocket.WebSocketApp("ws://echo.websocket.org/",
    ws = websocket.WebSocketApp("wss://ws.lightstream.bitflyer.com/json-rpc",
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()
