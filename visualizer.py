from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np

import csv, os
import pandas as pd
from datetime import datetime as dt
import re

from statistics import mean, median, variance, stdev
import matplotlib.animation as animation

import myErrors
from myUtils import CSVListIn

def bars3d_demo(arg):
    fig = plt.figure()
    ax  = fig.add_subplot(111, projection='3d')
    for c,z in zip(['r', 'g', 'b', 'y'], [60, 20, 10, 0]):
        xs = np.arange(20)
        ys = np.random.rand(20)

        cs = [c] * len(xs)
        cs[0] = 'c'
        ax.bar(xs, ys, zs=z, zdir='y', color=cs, alpha=0.8)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    plt.show()

def outputSeriesOf(snapshots, timestamps):

    fig = plt.figure(figsize=(15,15))
    ax = fig.add_subplot(111, projection='3d')
    for ss, ts in zip(snapshots, timestamps):
        xs = ss[:,0]
        ys = ss[:,1]
        zs = ts

        ax.bar(xs, ys, zs, zdir='y',color='b', alpha=0.8, width=1)

        # ax.set_zlim([0,1])
        # ax.set_xlim([734100,734300])

        ax.set_xlabel('price')
        ax.set_ylabel('time')
        ax.set_zlabel('size')

    plt.show()

def getSnapshotsSize():
    csvList = CSVListIn('./log/snapshot')
    return len(csvList)

def getSnapshotsBetween(first, final):
    csvList = CSVListIn('./log/snapshot')

    filenames = csvList[first : final]
    snapshots = np.ndarray([len(filenames),600,2])
    for i, fn in enumerate(filenames):
        path = './log/snapshot/' + fn
        snapshots[i] = pd.read_csv(path, header=None).values
        # print(snapshots[i,:])

    return snapshots

def getRecentSnapshots(quantity):
    csvList = CSVListIn('./log/snapshot')
    nFiles = len(csvList)
    filenames = quantity if nFiles >= quantity else len(csvList)
    if nFiles >= quantity:
        filenames = csvList[nFiles - quantity :nFiles]
    else:
        filenames = csvList
    # print(filenames)

    snapshots = np.ndarray([len(filenames),600,2])
    for i, fn in enumerate(filenames):
        path = './log/snapshot/' + fn
        snapshots[i] = pd.read_csv(path, header=None).values
        # print(snapshots[i])
    # print(snapshots)

    return snapshots

def getRecentTimestamps(quantity):
    csvList = CSVListIn('./log/snapshot')
    nFiles = len(csvList)
    filenames = quantity if nFiles >= quantity else len(csvList)
    if nFiles >= quantity:
        filenames = csvList[nFiles - quantity -1:nFiles-1]
    else:
        filenames = csvList

    regex = r'\d{20}'
    pattern = re.compile(regex)

    timestamps = np.ndarray(len(filenames),dtype=dt)
    for i, fn in enumerate(filenames):
        matchObj = pattern.match(fn)
        strTimestamp = matchObj.group()
        timestamp = dt.strptime(strTimestamp, '%Y%m%d%H%M%S%f')

        timestamps[i] = timestamp

    return timestamps

def getTimestampDiff(timestamps):
    deltas = [(timestamp - timestamps[0]).total_seconds() for timestamp in timestamps ]
    # print(deltas)
    return deltas

def reshape(x,min,max):
    y = 0
    if (x <= max) & (x >= min):
        y = x
    elif x < min:
        y = min
    elif x > max:
        y = max
    else:
        y = x
    return y

def change0within(x,min,max):
    y = 0
    if (x <= max) & (x >= min):
        y = 0
    elif x < min:
        y = x
    elif x > max:
        y = x
    else:
        y = x
    return y

def sortSnapshots(snapshots):
    """ 気配値表をaskbidの降順に並べ替える"""
    s = snapshots.shape
    # TODO: 全ての値から現在のmidpriceで減じる
    # print(s)

    snapshots_sorted = np.zeros(s)
    snapshots_des    = np.zeros(s)
    for i in range(0,s[0]):
        arg = np.argsort(snapshots[i,:,0])
        snapshots_des[i,:,:] = snapshots[i,arg[-1::-1],:]

    # snapshots_bak = snapshots
    # snapshots_sorted[:, 0      :s[1]//2, :] = snapshots_des[:, 0:s[1]//2, :]
    # snapshots_sorted[:, s[1]//2:s[1]   , :] = snapshots_bak[:, 0:s[1]//2, :]
    snapshots_sorted = snapshots_des
    myErrors.checkSnapshotOrder(snapshots_sorted)
    return snapshots_sorted, s


# 気配値の曲面をグレースケールの画像に変換する
## 現在の気配値の最大を基準価格として，基準価格以上の価格を切り捨て
def snapshots2Gray(snapshots):
    s = snapshots.shape
    # TODO: 全ての値から現在のmidpriceで減じる
    # print(s)
    currentBestBid = snapshots[s[0]-1,s[1]//2-1,0]
    currentBestAsk = snapshots[s[0]-1,s[1]//2,0]
    currentMidPrice = (currentBestBid + currentBestAsk )/2
    snapshots[:,:,0] -= currentMidPrice
    # print(snapshots)

    # TODO: 現在の気配値の値の絶対値の最大値を基準価格とする
    currentWorstBid = snapshots[s[0]-1,0,0]
    currentWorstAsk = snapshots[s[0]-1,s[1]-1,0]
    if (abs(currentWorstBid) > abs(currentWorstAsk)):
        refPrice = currentWorstBid
    else:
        refPrice = currentWorstAsk

    # refPrice = currentMidPrice


    # TODO: 全ての値を基準価格*2で割る．
    snapshots[:,:,0] /= (refPrice * 2)
    # print(snapshots)

    # TODO: [-0.5,0.5]外の価格は+-0.5とする
    reshaped = snapshots
    reshaped[:,:,0] = np.frompyfunc(reshape, 3, 1)(snapshots[:,:,0],-0.5,0.5)
    # print(reshaped)

    # TODO: 全ての値を0.5加算する
    reshaped[:,:,0] += 0.5


    # TODO: [0,1]をn分割して，時間ごとのヒストグラムを生成する
    n = s[0]
    nSeq = s[1]
    nTime= s[0]
    arr = np.arange(0,1+1/n,1/n)
    histSequence = np.zeros((nTime,n))
    for i in range(nTime): # ある時刻で
        snapshot = reshaped[i,:,:]
        # print(snapshot)
        for j in range(nSeq):
            for k in range(n):
                # print(snapshot[j,0])
                # print(arr[k+1])
                if (snapshot[j,0] <= arr[k+1]) &( snapshot[j,0] >= arr[k]):
                    histSequence[i,k] += snapshot[j,1]
                    break
                else:
                    pass
    # plt.imshow(histSequence, 'gray')
    # plt.show()

    # histSequence[:,:] = np.frompyfunc(reshape, 3, 1)(histSequence[:,:],0.0,1.0)

    for i in range(nTime):
        m = mean(histSequence[i,:])
        med = median(histSequence[i,:])
        sd = stdev(histSequence[i,:])
        histSequence[i,:] = np.frompyfunc(reshape, 3, 1)(histSequence[i,:],med-sd,med+sd)
        s = histSequence[i,:].sum()
        histSequence[i,:] /= s
        # print(med-sd,med+sd)

    # histSequence[:,0] = np.frompyfunc(reshape, 3, 1)(histSequence[:,0],0.0,1.0)
    # histSequence[:,n-1] = np.frompyfunc(reshape, 3, 1)(histSequence[:,n-1],0.0,1.0)
    # print(histSequence.T)
    return histSequence.T

# 気配値の曲面をグレースケールの画像に変換する
## 最新の気配値の標準偏差を基準価格として，1σ以上の値を切り捨て
def snapshots2Gray2(snapshots):
    s = snapshots.shape
    # TODO: 全ての値から現在のmidpriceで減じる
    # print(s)
    currentBestBid = snapshots[s[0]-1,s[1]//2-1,0]
    currentBestAsk = snapshots[s[0]-1,s[1]//2,0]
    currentMidPrice = (currentBestBid + currentBestAsk )/2
    snapshots[:,:,0] -= currentMidPrice
    # print(snapshots)

    # TODO: 最新の気配値の標準偏差を基準価格とする
    sd = stdev(snapshots[s[0]-1,:,0])
    refPrice = sd

    # TODO: 全ての値を基準価格で割る．
    snapshots[:,:,0] /= (refPrice)
    # print(snapshots)

    # TODO: [-0.5,0.5]外の価格は+-0.5とする
    reshaped = snapshots
    reshaped[:,:,0] = np.frompyfunc(reshape, 3, 1)(snapshots[:,:,0],-0.5,0.5)
    # print(reshaped)

    # TODO: 全ての値を0.5加算する
    reshaped[:,:,0] += 0.5


    # TODO: [0,1]をn分割して，時間ごとのヒストグラムを生成する
    n = s[0]
    nSeq = s[1]
    nTime= s[0]
    arr = np.arange(0,1+1/n,1/n)
    histSequence = np.zeros((nTime,n))
    for i in range(nTime): # ある時刻で
        snapshot = reshaped[i,:,:]
        # print(snapshot)
        for j in range(nSeq):
            for k in range(n):
                # print(snapshot[j,0])
                # print(arr[k+1])
                if (snapshot[j,0] <= arr[k+1]) &( snapshot[j,0] >= arr[k]):
                    histSequence[i,k] += snapshot[j,1]
                    break
                else:
                    pass
    # plt.imshow(histSequence, 'gray')
    # plt.show()

    # histSequence[:,:] = np.frompyfunc(reshape, 3, 1)(histSequence[:,:],0.0,1.0)

    for i in range(nTime):
        m = mean(histSequence[i,:])
        med = median(histSequence[i,:])
        sd = stdev(histSequence[i,:])
        histSequence[i,:] = np.frompyfunc(reshape, 3, 1)(histSequence[i,:],med-sd,med+sd)
        s = histSequence[i,:].sum()
        histSequence[i,:] /= s
        # print(med-sd,med+sd)

    # histSequence[:,0] = np.frompyfunc(reshape, 3, 1)(histSequence[:,0],0.0,1.0)
    # histSequence[:,n-1] = np.frompyfunc(reshape, 3, 1)(histSequence[:,n-1],0.0,1.0)
    # print(histSequence.T)
    return histSequence.T

# 気配値の曲面をグレースケールの画像に変換する
## 最新の気配値の標準偏差を基準価格と
def snapshots2Gray3(snapshots):
    s = snapshots.shape
    # TODO: 全ての値から現在のmidpriceで減じる
    # print(s)
    currentBestBid = snapshots[s[0]-1,s[1]//2-1,0]
    currentBestAsk = snapshots[s[0]-1,s[1]//2,0]
    currentMidPrice = (currentBestBid + currentBestAsk )/2
    snapshots[:,:,0] -= currentMidPrice
    # print(snapshots)

    # # TODO: 現在の気配値の値の絶対値の最大値を基準価格とする
    # currentWorstBid = snapshots[s[0]-1,0,0]
    # currentWorstAsk = snapshots[s[0]-1,s[1]-1,0]
    # if (abs(currentWorstBid) > abs(currentWorstAsk)):
    #     refPrice = currentWorstBid
    # else:
    #     refPrice = currentWorstAsk



    # TODO: 現在の気配値の標準偏差を基準価格とする
    print(snapshots[s[0]-1,:,0])
    refPrice = stdev(snapshots[s[0]-1,:,0])

    # TODO: 全ての値を基準価格*2で割る．
    snapshots[:,:,0] /= (refPrice * 2)
    # print(snapshots)


    reshaped = snapshots
    # reshaped[:,:,0] = np.frompyfunc(reshape, 3, 1)(snapshots[:,:,0],-0.5,0.5)
    # print(reshaped)

    # TODO: 全ての値を0.5加算する
    reshaped[:,:,0] += 0.5


    # TODO: [0,1]をn分割して，時間ごとのヒストグラムを生成する
    n = s[0]
    nSeq = s[1]
    nTime= s[0]
    arr = np.arange(0,1+1/n,1/n)
    histSequence = np.zeros((nTime,n))
    for i in range(nTime): # ある時刻で
        snapshot = reshaped[i,:,:]
        # print(snapshot)
        for j in range(nSeq):
            for k in range(n):
                # print(snapshot[j,0])
                # print(arr[k+1])
                if (snapshot[j,0] <= arr[k+1]) &( snapshot[j,0] >= arr[k]):
                    histSequence[i,k] += snapshot[j,1]
                    break
                else:
                    pass
    # plt.imshow(histSequence, 'gray')
    # plt.show()

    # histSequence[:,:] = np.frompyfunc(reshape, 3, 1)(histSequence[:,:],0.0,1.0)

    # for i in range(nTime):
    #     m = mean(histSequence[i,:])
    #     med = median(histSequence[i,:])
    #     sd = stdev(histSequence[i,:])
    #     histSequence[i,:] = np.frompyfunc(reshape, 3, 1)(histSequence[i,:],med-sd,med+sd)
    #     s = histSequence[i,:].sum()
    #     histSequence[i,:] /= s
    #     # print(med-sd,med+sd)

    for i in range(nTime):
        m = mean(histSequence[i,:])
        med = median(histSequence[i,:])
        sd = stdev(histSequence[i,:])
        histSequence[i,:] = np.frompyfunc(change0within, 3, 1)(histSequence[i,:],med-sd*2,med+sd*2)
        s = histSequence[i,:].sum()
        if s != 0:
            histSequence[i,:] /= s
        # print(med-sd,med+sd)

    # histSequence[:,0] = np.frompyfunc(reshape, 3, 1)(histSequence[:,0],0.0,1.0)
    # histSequence[:,n-1] = np.frompyfunc(reshape, 3, 1)(histSequence[:,n-1],0.0,1.0)
    # print(histSequence.T)
    return histSequence.T

# 気配値の曲面をグレースケールの画像に変換する
## 現在の気配値の標準偏差を基準価格として，2σ以上の価格を切り捨て
def snapshots2Gray4(snapshots):
    snapshots, s = sortSnapshots(snapshots)

    currentBestBid = snapshots[s[0]-1,s[1]//2,0]
    currentBestAsk = snapshots[s[0]-1,s[1]//2+1,0]
    currentMidPrice = (currentBestBid + currentBestAsk )/2
    snapshots[:,:,0] -= currentMidPrice
    # print(snapshots)

    # TODO: 現在の気配値の標準偏差を基準価格とする
    refPrice = stdev(snapshots[s[0]-1,:,0])

    # TODO: 全ての値を基準価格*2で割る．
    snapshots[:,:,0] /= (refPrice * 2)
    # print(snapshots)


    reshaped = snapshots
    # reshaped[:,:,0] = np.frompyfunc(reshape, 3, 1)(snapshots[:,:,0],-0.5,0.5)

    # TODO: 全ての値を0.5加算する
    reshaped[:,:,0] += 0.5


    # TODO: [0,1]をn分割して，時間ごとのヒストグラムを生成する
    n = s[0]
    nSeq = s[1]
    nTime= s[0]
    arr = np.arange(0,1+1/n,1/n)
    histSequence = np.zeros((nTime,n))
    for i in range(nTime): # ある時刻で
        snapshot = reshaped[i,:,:]
        # print(snapshot)
        for j in range(nSeq):
            for k in range(n):
                # print(snapshot[j,0])
                # print(arr[k+1])
                if ( arr[k] < snapshot[j,0]) & (snapshot[j,0] <= arr[k+1]):
                    histSequence[i,k] += snapshot[j,1]
                    break
                else:
                    pass
    # plt.imshow(histSequence, 'gray')
    # plt.show()

    # histSequence[:,:] = np.frompyfunc(reshape, 3, 1)(histSequence[:,:],0.0,1.0)

    for i in range(nTime):
        m = mean(histSequence[i,:])
        med = median(histSequence[i,:])
        sd = stdev(histSequence[i,:])
        histSequence[i,:] = np.frompyfunc(change0within, 3, 1)(histSequence[i,:],med-1*sd,med+1*sd)
        s = histSequence[i,:].sum()
        histSequence[i,:] /= s
        # print(med-sd,med+sd)

    # histSequence[:,0] = np.frompyfunc(reshape, 3, 1)(histSequence[:,0],0.0,1.0)
    # histSequence[:,n-1] = np.frompyfunc(reshape, 3, 1)(histSequence[:,n-1],0.0,1.0)
    # print(histSequence.T)
    return histSequence.T


if __name__ == '__main__':
    # テスト用気配値
    # snapshots = np.array([
    #     [
    #         [736236.0,0.1],
    #         [736234.0,0.06],
    #         [736874.0,0.02930897],
    #         [736875.0,0.04]
    #     ],
    #     [
    #         [736253.0,0.16],
    #         [736252.0,0.5],
    #         [736865.0,0.01],
    #         [736871.0,0.0284677]
    #     ],
    #     [
    #         [736250.0,2.42],
    #         [736249.0,0.01],
    #         [736877.0,0.08744157],
    #         [736878.0,0.592]
    #     ],
    #     [
    #         [736236.0,0.1],
    #         [736234.0,0.06],
    #         [736862.0,0.05],
    #         [736869.0,0.06]
    #     ]
    # ])

    # snapshots = getRecentSnapshots(100)
    # timestamps = getRecentTimestamps(100)
    # outputSeriesOf(snapshots, getTimestampDiff(timestamps))

    # # 特定期間の気配値の取得
    # l = getSnapshotsSize()
    # # print(getSnapshotsSize())
    # first = l - 300
    # final = l - 200
    # snapshots = getSnapshotsBetween(first,final)
    #
    # # 気配値をグレースケールに変換
    # ssGray = snapshots2Gray2(snapshots)
    # print(ssGray)
    # plt.imshow(ssGray, 'gray')
    # plt.show()

    # n個の気配値からグラフを動画にして出力
    n = 500
    fig = plt.figure()
    ims = []
    l = getSnapshotsSize()
    for i in np.arange(l-n-100,l-100):
        print(f'{(i-(l-n-100))/n*100}% finished')
        snapshots = getSnapshotsBetween(i-100,i)
        ssGray = snapshots2Gray4(snapshots)
        im = plt.imshow(ssGray, 'gray')
        ims.append([im])

    ani = animation.ArtistAnimation(fig, ims, interval=100)
    ani.save('anim.mp4', writer="ffmpeg")

    # snapshots = getSnapshotsBetween(1500,1600)
    # ssGray1 = snapshots2Gray(snapshots)
    # im = plt.imshow(ssGray1, 'gray')
    # plt.show()

    # n = 100
    # fig = plt.figure()
    # ims = []
    # l = getSnapshotsSize()
    # print(l,n)
    # snapshots = getSnapshotsBetween(l-n-100-300,l-n-300)
    # ssGray3 = snapshots2Gray4(snapshots)
    # im2 = plt.imshow(ssGray3, 'gray')
    # plt.show()
