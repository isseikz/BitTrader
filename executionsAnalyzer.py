import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates  as mdates
import mpl_finance as mpf
from datetime import timedelta as td
from datetime import datetime as dt
import talib as ta
from statistics import mean, median, variance, stdev

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

def csv2OHLC(filepath):
    # https://kabuoji3.com/stock/7203/2018/
    dfOHLC = pd.read_csv(filepath,encoding="SHIFT-JIS",header=1, usecols=[1,2,3,4])
    dfVolume = pd.read_csv(filepath,encoding="SHIFT-JIS", header=1,usecols=[5])
    # print(dataframeOHLC)
    return np.array(dfOHLC), np.array(dfVolume)


def data2OHLC(times, values, period, sizes):
    t0 = times[0]
    tf = times[len(times)-1]
    n  = int((tf - t0).total_seconds() / period) +1
    OHLC = np.zeros((n,4), dtype=float)
    OHLC_Times = np.zeros(n,dtype=dt)
    OHLC_Volumes = np.zeros(n,dtype=float)

    k=0
    OHLC[0,:] = values[0]
    OHLC_Times[0] =  t0
    for id,time in enumerate(times):
        nt = (time - t0).total_seconds()//period
        OHLC_Volumes[k] += sizes[id]
        if (k <= nt) & (nt < k+1):
            OHLC[k,3] = values[id]
            OHLC[k,1] = values[id] if (values[id] > OHLC[k,1]) else (OHLC[k,1])
            OHLC[k,2] = values[id] if (values[id] < OHLC[k,2]) else (OHLC[k,2])
        elif k+1 <= nt:
            k += 1
            OHLC[k,:] = values[id]
            OHLC_Times[k] = OHLC_Times[k-1] + td(seconds=period)

    return OHLC, OHLC_Times, t0, tf, period, OHLC_Volumes

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

def risingRateBetween(index_n, index_n1):
    # print(index_n,index_n1)
    return (index_n - index_n1) / index_n1

def alertGoldenCross(index1_n, index1_n1, index2_n, index2_n1):
    alert = 0
    if (index1_n - index2_n)*(index1_n1 - index2_n1) < 0:
        alert = 1
    else:
        alert = 0
    return (index1_n - index2_n)*(index1_n1 - index2_n1), alert

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
    filteredValue[0] = values[0]
    for i,value in enumerate(values[0:len(filteredValue)-1]):
        filteredValue[i+1] = filteredValue[i] * rate + value * (1-rate)
        # print(value, filteredValue[i+1])
    return filteredValue

def labelDealing(executions,future_sample):
    labels = np.zeros(len(executions)-future_sample,dtype=float)
    for i,label in enumerate(labels):
        if executions[i+future_sample] > executions[i]: # 上昇
            labels[i] = 1
        else: # 下降
            labels[i] = 0
    return labels

def filteredValues(OHLC, timeConstant, dt):
    values = np.frompyfunc(midPrice,2,1)(OHLC[:,0],OHLC[:,3])
    values = LowPassFiltered(values, timeConstant, dt)
    return values

def makeLabel(OHLC, timeConstant, dt):
    values = filteredValues(OHLC, 1, 1)
    labels = labelDealing(values,1)
    return labels

def sma_n(value,n):
    s = value.shape
    n_ = s[0] - (n-1)

    sma = np.zeros(n_,dtype=float)
    for i in range(n_):
        sma[i] = mean(value[i:i+n])
    return sma, n_



def inputRayer(OHLC, OHLC_Volumes, timeConstant, dt):
    """NNに与える入力の設計
    + 取引価格の変動率
    + 5秒間平均線の変動率
    + 25秒間平均線の変動率
    # + 取引量
    + ゴールデンクロス判定
    + ボリンジャークロス判定
    """
    s = OHLC.shape
    input = np.zeros((s[0]-25,6),dtype=float)

    OHLC_n  = OHLC[1:s[0]  ,:]
    OHLC_n1 = OHLC[0:s[0]-1,:]

    OHLC_Volumes_n  = OHLC_Volumes[1:s[0]  ]
    OHLC_Volumes_n1 = OHLC_Volumes[0:s[0]-1]

    price = filteredValues(OHLC, timeConstant, dt)
    price_n  = price[25:s[0]  ]
    price_n1 = price[24:s[0]-1]
    input[:,0] = np.frompyfunc(risingRateBetween,2,1)(price_n,price_n1)
    input[:,0] /= stdev(input[:,0])

    sma5,l   = sma_n(price,5) #ta.SMA(price, timeperiod=5)
    sma5_n  = sma5[21:len(sma5)]
    sma5_n1 = sma5[20:len(sma5)-1]
    input[:,1] = np.frompyfunc(risingRateBetween,2,1)(sma5_n,sma5_n1)
    input[:,1] /= stdev(input[:,1])


    sma25,l = sma_n(price,25) #ta.SMA(price, timeperiod=25)
    sma25_n  = sma25[1:len(sma25)]
    sma25_n1 = sma25[0:len(sma25)-1]
    input[:,2] = np.frompyfunc(risingRateBetween,2,1)(sma25_n,sma25_n1)
    input[:,2] /= stdev(input[:,2])

    # input[:,3] = OHLC_Volumes[1:s[0]]
    # input[:,3] /= median(input[:,3])

    input[:,4] = np.frompyfunc(alertGoldenCross,4,2)(sma5_n,sma5_n1,sma25_n,sma25_n1)[1]
    # input[:,4] = sma5_n-sma25_n

    upper, middle, lower = ta.BBANDS(price_n, timeperiod=5)
    input[:,5] = np.frompyfunc(alertBollingerCross,3,1)(upper,lower,price_n)
    return input

def makeModelXY(OHLC, OHLC_Volumes,data_id=2, label="", fig=False):
    # times, ids, sides, prices, sizes = loadDatas(data_id)
    # OHLC, OHLC_Times, t0, tf, period, OHLC_Volumes = data2OHLC(times, prices, 1, sizes)

    labels = makeLabel(OHLC, timeConstant=1, dt=1)
    input = inputRayer(OHLC,OHLC_Volumes,timeConstant=1, dt=1)

    x = input[0:input.shape[0]-1]
    y = labels[labels.shape[0]-x.shape[0]:labels.shape[0]]

    print(x.shape,y.shape)
    np.save(label + 'x.npy',x)
    np.save(label + 'y.npy',y)

    real = filteredValues(OHLC, 1, 1)[labels.shape[0]-x.shape[0]:labels.shape[0]]
    oh   = OHLC[labels.shape[0]-x.shape[0]:labels.shape[0],0]
    if fig:
        fig = plt.figure()
        plt.plot(x)
        plt.plot(y)
        plt.plot((real-real[0])/100)
        plt.plot((oh-oh[0])/100)
        plt.legend(('price rate','sma5 rate','sma25 rat','volume','golden','bollingeer','y','price (10sec LPF)', 'real price'))
        plt.xlabel('time[s]')
        plt.show()
#
    return x,y

def OHLC_7203(firstYear, lastYear):
    OHLC = np.empty((0,4),int)
    dOHLC, dVolume = csv2OHLC('log/stock_7203/7203_' + str(2018) + '.csv')
    Volume = np.empty((0),int)
    for year in range(firstYear,lastYear):
        dOHLC, dVolume = csv2OHLC('log/stock_7203/7203_' + str(year) + '.csv')
        OHLC = np.vstack((OHLC,dOHLC))
        Volume = np.append(Volume,dVolume)
    print(OHLC.shape,Volume.shape)
    return OHLC, Volume

if __name__ == '__main__':
    # indiceCharts()

    # times, ids, sides, prices, sizes = loadDatas(2)
    # OHLC, OHLC_Times, t0, tf, period, OHLC_Volumes = data2OHLC(times, prices, 1, sizes)
    # prices = OHLC[:,0]

    # sma5 = ta.SMA(prices, timeperiod=5)
    # sma25 = ta.SMA(prices, timeperiod=25)
    #
    # sma5_n1  = sma5[1:len(sma5)-1]
    # sma25_n1 = sma25[1:len(sma5)-1]
    #
    # cross =  np.frompyfunc(alertGoldenCross,4,1)(sma5[0:len(sma25)-2],sma5_n1,sma25[0:len(sma25)-2],sma25_n1)
    # print(f'{sum(cross)} points in {len(sma5_n1)} executions are the golden cross points')
    #
    #
    # upper, middle, lower = ta.BBANDS(prices, timeperiod=5)
    # bollingerCross = np.frompyfunc(alertBollingerCross,3,1)(upper,lower,prices)
    # print(f'{sum(bollingerCross)} points in {len(prices)} executions are the bollinger cross points')
    #

    OHLC, OHLC_Volumes = OHLC_7203(2010,2018)
    makeModelXY(OHLC, OHLC_Volumes,data_id=2, label="test_7203_", fig=True)

    OHLC, OHLC_Volumes = OHLC_7203(2018,2019)
    makeModelXY(OHLC, OHLC_Volumes,data_id=1, label="train_7203_", fig=False)
