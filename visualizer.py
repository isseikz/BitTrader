from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np

import csv, os
import pandas as pd
from datetime import datetime as dt
import re

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

def CSVListIn(dir_path):
    files = [path for path in os.listdir(dir_path) if path.endswith('.csv')]
    return files

def getRecentSnapshots(quantity):
    csvList = CSVListIn('./log/snapshot')
    nFiles = len(csvList)
    filenames = quantity if nFiles >= quantity else len(csvList)
    if nFiles >= quantity:
        filenames = csvList[nFiles - quantity -1:nFiles-1]
    else:
        filenames = csvList

    snapshots = np.ndarray([len(filenames),600,2])
    for i, fn in enumerate(filenames):
        path = './log/snapshot/' + fn
        snapshots[i] = pd.read_csv(path, header=None).values
        print(snapshots[i])
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
    print(deltas)
    return deltas

if __name__ == '__main__':
    # snapshots = np.array([
    #     [
    #         [1,0.1],
    #         [2,0.3],
    #         [3,0.2]
    #     ],
    #     [
    #         [0,0.4],
    #         [1,0.2],
    #         [2,0.1]
    #     ],
    #     [
    #         [3,0.9],
    #         [4,0.1],
    #         [5,0.7]
    #     ]
    # ])
    # timestamps = np.linspace(0,2,3)
    # outputSeriesOf(snapshots, timestamps)

    snapshots = getRecentSnapshots(60)
    timestamps = getRecentTimestamps(60)
    outputSeriesOf(snapshots, getTimestampDiff(timestamps))
