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



if __name__ == '__main__':
    times, ids, sides, prices, sizes = loadDatas(2)
    OHLC, OHLC_Times, t0, tf, period = data2OHLC(times, prices, 60)

    sma5 = ta.SMA(np.array(prices,dtype='f8'), timeperiod=5)

    quotes = np.vstack((mdates.date2num(OHLC_Times[:]),OHLC[:,0],OHLC[:,1],OHLC[:,2],OHLC[:,3]))
    print(quotes.T)

    fig = plt.figure()
    ax = plt.subplot()
    # mpf.candlestick_ohlc(ax,quotes.T, width=0.0005, colorup='g', colordown='r')
    mpf.candlestick2_ohlc(ax,OHLC[:,0],OHLC[:,1],OHLC[:,2],OHLC[:,3], width=0.7, colorup='g', colordown='r')

    fig2 = plt.figure()
    ax2 = plt.subplot()
    plt.plot(times,sma5,times,prices)    
    plt.show()
