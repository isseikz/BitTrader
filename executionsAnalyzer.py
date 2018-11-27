import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates  as mdates
import mpl_finance as mpf
from datetime import timedelta as td
from datetime import datetime as dt
import talib as ta

import myErrors, myUtils

def side2int(side):
    res = 0
    if side == 'BUY':
        res = 1
    elif side == 'SELL':
        res = 1
    return res

def loadDatas(timeData):
    myErrors.shouldBeSingleInt(timeData)

    pathExe = "/hdd/Projects/BitTrader/log/executions"
    list = myUtils.CSVListIn(pathExe)
    file = pathExe + "/" + list[timeData]

    data = pd.read_csv(file, header=None).values
    print(data)

    times  = np.frompyfunc(dt.strptime, 2, 1)(data[:,0], '%Y%m%d%H%M%S%f')
    ids    = np.frompyfunc(int, 1, 1)(data[:,1])
    sides  = np.frompyfunc(side2int, 1, 1)(data[:,2])
    prices = np.frompyfunc(int, 1, 1)(data[:,3])
    sizes  = np.frompyfunc(float, 1, 1)(data[:,4])

    return times, ids, sides, prices, sizes

def data2OHLC(times, values, period):
    t0 = times[0]
    tf = times[len(times)-1]
    n  = int((tf - t0).total_seconds() / period) +1
    OHLC = np.zeros((n,4), dtype=float)
    OHLC_Times = [t0]*n

    k=0
    OHLC[0,:] = values[0]
    OHLC_Times[0] =  t0
    for id,time in enumerate(times):
        nt = (time - t0).total_seconds()//period
        if (k <= nt) & (nt < k+1):
            OHLC[k,3] = values[id]
            OHLC[k,1] = values[id] if (values[id] > OHLC[k,1]) else (OHLC[k,1])
            OHLC[k,2] = values[id] if (values[id] < OHLC[k,2]) else (OHLC[k,2])
        elif k+1 <= nt:
            k += 1
            OHLC[k,:] = values[id]
            OHLC_Times[k] = OHLC_Times[k-1] + td(seconds=period)

    return OHLC, OHLC_Times, t0, tf, period

def candleChart(period):
    times, ids, sides, prices, sizes = loadDatas(2)
    OHLC, OHLC_Times, t0, tf, period = data2OHLC(times, prices, period)

    quotes = np.vstack((mdates.date2num(OHLC_Times[:]),OHLC[:,0],OHLC[:,1],OHLC[:,2],OHLC[:,3]))

    fig = plt.figure()
    ax = plt.subplot()
    # mpf.candlestick_ohlc(ax,quotes.T, width=0.0005, colorup='g', colordown='r')
    mpf.candlestick2_ohlc(ax,OHLC[:,0],OHLC[:,1],OHLC[:,2],OHLC[:,3], width=0.7, colorup='g', colordown='r')
    plt.show()

def indiceCharts():
    times, ids, sides, prices, sizes = loadDatas(2)

    prices = np.array(prices,dtype='f8')
    sma5 = ta.SMA(prices, timeperiod=5)
    sma25 = ta.SMA(prices, timeperiod=25)
    rsi14 = ta.RSI(prices, timeperiod=14)
    macd, macdsignal, macdhist = ta.MACD(prices,fastperiod=12, slowperiod=26, signalperiod=9)

    fig, (ax1,ax2) = plt.subplots(nrows=2)
    ax1.plot(times,prices,times,sma5,times,sma25,linewidth=0.5)
    ax1.legend(['price','sma5','sma25'])
    ax2.plot(times,rsi14,times,macd,linewidth=0.5)
    ax2.legend(['rsi14','macd'])
    plt.show()

def alertGoldenCross(index1_n, index1_n1, index2_n, index2_n1):
    alert = 0
    if (index1_n - index2_n1)*(index1_n1 - index2_n1) < 0:
        alert = 1
    else:
        alert = 0
    return alert

def alertBollingerCross(upper,lower,price):
    alert = 0
    if (price >= upper) | (price <= lower):
        alert = 1
    else:
        alert = 0
    return 0

def midPrice(Open,Close):
    return (Open+Close)/2

def LowPassFiltered(values, timeConstant, dt):
    rate = timeConstant/(timeConstant + dt)
    filteredValue = np.zeros(len(values),dtype=float)
    for i,value in enumerate(values[0:len(filteredValue)-2]):
        filteredValue[i+1] = filteredValue[i] * rate + value * (1-rate)
    return filteredValue

def labelDealing(executions):
    labels = np.zeros(len(executions)-1,dtype=float)
    for i,label in enumerate(labels):
        if executions[i+1] > executions[i]: # 上昇
            labels[i] = 1
        else: # 下降
            labels[i] = 0
    return labels

def makeLabel():
    times, ids, sides, prices, sizes = loadDatas(2)
    OHLC, OHLC_Times, t0, tf, period = data2OHLC(times, prices, 1)

    values = np.frompyfunc(midPrice,2,1)(OHLC[:,0],OHLC[:,3])
    # print(sum(values))
    filteredValues = LowPassFiltered(values, 10.0, 1.0)
    # print(sum(filteredValues))
    labels = labelDealing(filteredValues)
    # print(labels)
    fig = plt.figure()
    plt.plot(labels)
    plt.show()



if __name__ == '__main__':
    indiceCharts()

    times, ids, sides, prices, sizes = loadDatas(2)
    OHLC, OHLC_Times, t0, tf, period = data2OHLC(times, prices, 1)
    prices = OHLC[:,0]

    sma5 = ta.SMA(prices, timeperiod=5)
    sma25 = ta.SMA(prices, timeperiod=25)

    sma5_n1  = sma5[1:len(sma5)-1]
    sma25_n1 = sma25[1:len(sma5)-1]

    cross =  np.frompyfunc(alertGoldenCross,4,1)(sma5[0:len(sma25)-2],sma5_n1,sma25[0:len(sma25)-2],sma25_n1)
    print(f'{sum(cross)} points in {len(sma5_n1)} executions are the golden cross points')


    upper, middle, lower = ta.BBANDS(prices, timeperiod=5)
    bollingerCross = np.frompyfunc(alertBollingerCross,3,1)(upper,lower,prices)
    print(f'{sum(bollingerCross)} points in {len(prices)} executions are the bollinger cross points')

    makeLabel()
