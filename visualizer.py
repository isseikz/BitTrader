from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np

import csv, os
import pandas as pd
from datetime import datetime as dt
import re

from statistics import mean, median, variance, stdev
import matplotlib.animation as animation

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


def CSVListIn(dir_path):
    files = [path for path in os.listdir(dir_path) if path.endswith('.csv')]
    return files

def getSnapshotsBetween(first, final):
    csvList = CSVListIn('./log/snapshot')

    filenames = csvList[first : final]
    snapshots = np.ndarray([len(filenames),600,2])
    for i, fn in enumerate(filenames):
        path = './log/snapshot/' + fn
        snapshots[i] = pd.read_csv(path, header=None).values

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

# TODO: 気配値の曲面をグレースケールの画像に変換する
def snapshots2Gray(snapshots):
    s = snapshots.shape
    # TODO: 全ての値から現在のmidpriceで減じる
    # print(s[1])
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

    # 特定期間の気配値の取得
    # l = getSnapshotsSize()
    # # print(getSnapshotsSize())
    # first = l - 300
    # final = l - 200
    # snapshots = getSnapshotsBetween(first,final)

    # 気配値をグレースケールに変換
    # ssGray = snapshots2Gray(snapshots)
    # print(ssGray)
    # plt.imshow(ssGray, 'gray')
    # plt.show()

    # グラフを動画にして出力
    # fig = plt.figure()
    # ims = []
    # l = getSnapshotsSize()
    # for i in np.arange(l-2,l-1):
    #     print(f'{i} in {l} snapshots')
    #     snapshots = getSnapshotsBetween(i-100,i)
    #     ssGray = snapshots2Gray(snapshots)
    #     im = plt.imshow(ssGray, 'gray')
    #     ims.append([im])
    #
    # ani = animation.ArtistAnimation(fig, ims, interval=100)
    # ani.save('anim.mp4', writer="ffmpeg")

    snapshots = getSnapshotsBetween(4000,4100)
    ssGray = snapshots2Gray(snapshots)
    im = plt.imshow(ssGray, 'gray')
    plt.show()
