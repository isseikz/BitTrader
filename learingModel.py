from pathlib import Path
import csv, os
import pandas as pd
import numpy as np
from datetime import datetime as dt
from pytz import timezone
import re

import visualizer as v

# TODO: リストアップ
def snapshot_list():
    p = Path("./log/snapshot/")
    l = sorted(list(p.glob("*.csv")))
    # print(l)
    return l

# TODO: n 番目から n+ 10番目までのスナップショットのリストを取得
def snapshots_10(l, n):
    s = l[n:n+10]
    # print(s)
    return s

# TODO: n 番目から n+ q番目までのスナップショットのリストを取得
def snapshots_between(l, first, last):
    s = l[first : last]
    return np.array(s)

def str2float(str_list):
    return list(map(float, str_list))

# TODO: 10個のスナップショットから平面を作成
def snapshots_traj(l):
    s = l.shape
    traj = np.zeros((s[0],600,2), dtype=float)
    for i, snapshot_path in enumerate(l):
        with open(snapshot_path) as file:
            reader = csv.reader(file)
            lf = [row for row in list(reader) if row != []]
            s = np.array(lf)
            sf = s.astype(np.float)
            traj[i,:,:] = sf
            # print(s)
            # print(len(sf))

    # print(traj.astype(np.float))
    return traj.astype(np.float)

# TODO: n番目のスナップショットを取得
def nth_snapshot(l,n):
    with open(l[n]) as file:
        # print(l[n])
        reader = csv.reader(file)
        # print(list(reader))
        lf = [row for row in list(reader) if row != []]
        s = np.array(lf)
        # print(lf)
        sf = s.astype(np.float)
        # print(sf)
    return sf

# TODO: 学習モデルの大きさ定義
def modelArr(foldername):
    thisDir = os.path.dirname(os.path.abspath(__file__))
    print(thisDir)

    path = './model/' + foldername + '/'

    modelName = ["train","test"]
    labels     = ["should_buy","should_sell","both","neither"]

    modelSize = np.zeros((len(modelName),len(labels)),dtype=int)

    pathLabel = modelName
    pathModel = modelName
    # todo: listModelの大きさを調べて，空行列を設ける
    # TODO:

    for id, name in enumerate(modelName):
        print(name)
        pathLabel[id] = list(Path(path + name).glob(".csv"))

        for j, label in enumerate(labels):
            pathModel = Path( path + name + "/" + label + "/")
            print(pathModel)
            listModel = list(pathModel.glob("*.csv"))
            modelSize[id,j] = len(listModel)

    print(modelSize)
    return listModel, modelName, labels, modelSize

'''
    既存の学習モデルを読み出す
    入力：モデル名
    出力：訓練データ・テストデータ・それぞれのラベル
'''
def loadModel(foldername, nSnapshots):
    listModel, modelName, labels, modelSize = modelArr(foldername)
    print(listModel, modelName, labels, modelSize)

    dataSize_train = modelSize[0,:].sum()
    dataSize_test  = modelSize[1,:].sum()
    allModels = np.zeros((nSnapshots,600,2), dtype=float)
    for id, name in enumerate(modelName):
        for j, label in enumerate(labels):
            for k, modelData in enumerate(listModel):
                with open(modelData) as file:
                    reader = csv.reader(file)
                    data = [row for row in list(reader) if row != []]

                    model = np.zeros((nSnapshots,600,2), dtype=float)
                    for l, order in enumerate(data):
                        arr = np.array(order)
                        for m, strValue in enumerate(arr):
                            # print(strValue)
                            regx1 = r'(\d+\.\d+e[\+|\-]\d+)+'
                            regx2 = r'(\d+)+'
                            # regx1 = r'[(\d+\.\d+e[\+|\-]\d+)+]|[\d+\.]'
                            valsize = re.findall(regx1, strValue)

                            if len(valsize) == 0:
                                valsize = re.findall(regx2, strValue)
                                # print(valsize)

                            s = np.array(valsize)
                            sf = s.astype(np.float)
                            # print(sf)
                            model[l,m,:] = sf

                    models[k] = model
                    print(models)
                    allModels.append(models)
    print(allModels)
    return allModels, dataSize_train, dataSize_test


'''
    リファレンスファイルからパスを読み取り，モデルにする
    入力: foldername: モデル用データの入っているフォルダ
    出力: datasArr_test, labelArr_test, datasArr_train, labelArr_train: リファレンスから得られるデータとラベル
'''
def loadDatas(foldername):
    dataType = ["test","train"]
    regx1 = r'(\d+\.\d+e[\+|\-]\d+)+'
    regx2 = r'(\d+)+'

    path_model = './model/' + foldername + '/'

    path_modelDir = [""] * 2
    path_refFile = [""] * 2

    for id in range(2):
        path_modelDir[id] = path_model + dataType[id] + "/"
        path_refFile[id]  = path_modelDir[id]  + "reference.csv"

    dataSize = [0] * 2 # テスト(0), 学習(1)データの要素数

    datasArr_test  = []
    datasArr_train = []

    labelArr_test  = []
    labelArr_train = []

    # datas = np.ndarray()
    for i,path in enumerate(path_refFile):
        with open(Path(path)) as refFile:
            reader = csv.reader(refFile)
            dataList = np.array([row for row in list(reader) if row != []])
            dataSize[i] = len(dataList)
            print(dataSize[i])

            # 各データを読み出して，学習用データにする
            # for j,data in enumerate(dataList):
            #     if j % 100 == 0:
            #         print(f'{dataType[i]}, {(j+100)/dataSize[i]*100}%')
            #
            #     snapshots = pd.read_csv(data[1], header=None).values
            #
            #     should_buy  = 1 if data[2] == "True" else 0
            #     should_sell = 1 if data[3] == "True" else 0
            #     if i == 0:
            #         datasArr_test.append(snapshots)
            #         labelArr_test.append(int(should_buy*2+should_sell))
            #     else:
            #         datasArr_train.append(snapshots)
            #         labelArr_train.append(int(should_buy*2+should_sell))

            for j,data in enumerate(dataList):
                if j % 100 == 0:
                    print(f'{dataType[i]}, {(j+100)/dataSize[i]*100}%')

                with open(Path(data[1])) as pathData:
                    csvData = csv.reader(pathData)
                    strSnapshots = np.array([row for row in list(csvData) if row != []])
                    # print(strSnapshots.shape)

                    snapshots = np.ndarray((strSnapshots.shape[0],600,2),dtype=float)
                    for l,strSnapshot in enumerate(strSnapshots):
                        # print(len(strSnapshot))
                        snapshot = np.ndarray((600,2),dtype=float)
                        for k,strValue in enumerate(strSnapshot):
                            valsize = re.findall(regx1, strValue)

                            if len(valsize) == 0:
                                valsize = re.findall(regx2, strValue)
                                # print(valsize)

                            s = np.array(valsize)
                            sf = s.astype(np.float)
                            snapshot[k,:] = sf

                        snapshots[l,:,:] = snapshot

                    should_buy  = 1 if data[2] == "True" else 0
                    should_sell = 1 if data[3] == "True" else 0
                    if i == 0:
                        datasArr_test.append(snapshots)
                        labelArr_test.append(int(should_buy*2+should_sell))
                    else:
                        datasArr_train.append(snapshots)
                        labelArr_train.append(int(should_buy*2+should_sell))

    print(datasArr_train)
    print(labelArr_train)
    return datasArr_test, labelArr_test, datasArr_train, labelArr_train

'''
    # データから学習用データを作る
    ## 入力
    + datasSise: 1つのデータに用いる気配値の数量
    + n_train:   学習用データの数量
    + n_test:    テスト用データの数量
    ## 出力: なし
'''
def makeModelData(datasSize, n_train, n_test):
    # 学習用データ
    l = snapshot_list()
    n_max = len(l) - datasSize - n_test -1

    timestamp = dt.now(timezone('UTC')).strftime('%Y%m%d%H%M')
    os.makedirs(f'./model/{timestamp}/train/both', exist_ok=True)
    os.makedirs(f'./model/{timestamp}/train/neither', exist_ok=True)
    os.makedirs(f'./model/{timestamp}/train/should_buy', exist_ok=True)
    os.makedirs(f'./model/{timestamp}/train/should_sell', exist_ok=True)


    for n in range(0,n_max):
        print(n)

        t = snapshots_traj(s)

        s_current = nth_snapshot(l, n + 10)     # 現在の気配値
        s_future  = nth_snapshot(l, n + 10 +10) # 10サンプル後の気配値

        should_buy  = s_current[300][0] - s_future[301][0] < 0
        should_sell = s_current[301][0] - s_future[300][0] > 0

        det_class = 'neither'
        if should_buy & should_sell:
            det_class = 'both'
        elif should_buy & (not should_sell):
            det_class = 'should_buy'
        elif should_sell & (not should_buy):
            det_class = 'should_sell'
        else:
            det_class = 'neither'

        path = f'./model/{timestamp}/train/{det_class}/model{n}.csv'
        with open(path, 'w') as file:
            w = csv.writer(file)
            w.writerows(t)

        with open(f'./model/{timestamp}/train/reference.csv', 'a') as file:
            w = csv.writer(file)
            w.writerow([n, path, should_buy, should_sell])

'''
    # データから学習用データ・テスト用データを作る
    ## 入力
    + datasSise: 1つのデータに用いる気配値の数量
    + n_train:   学習用データの数量
    + n_test:    テスト用データの数量
    ## 出力: なし
'''
def createModel(datasSize, n_train, n_test):
    future_sample = 1
    # 学習用データ
    l = snapshot_list()
    n_max = len(l) - datasSize - future_sample - n_test -1

    timestamp = dt.now(timezone('UTC')).strftime('%Y%m%d%H%M')
    os.makedirs(f'./model/{timestamp}/train/both', exist_ok=True)
    os.makedirs(f'./model/{timestamp}/train/neither', exist_ok=True)
    os.makedirs(f'./model/{timestamp}/train/should_buy', exist_ok=True)
    os.makedirs(f'./model/{timestamp}/train/should_sell', exist_ok=True)


    for n in range(0,n_max):
        print(n)

        # s = snapshots_10(l, n)
        s = snapshots_between(l, n, n+datasSize)
        t = snapshots_traj(s)

        s_current = nth_snapshot(l, n + datasSize)     # 現在の気配値
        s_future  = nth_snapshot(l, n + datasSize + future_sample) # 1サンプル後の気配値

        should_buy  = s_current[300][0] - s_future[301][0] < 0
        should_sell = s_current[301][0] - s_future[300][0] > 0

        det_class = 'neither'
        if should_buy & should_sell:
            det_class = 'both'
        elif should_buy & (not should_sell):
            det_class = 'should_buy'
        elif should_sell & (not should_buy):
            det_class = 'should_sell'
        else:
            det_class = 'neither'

        path = f'./model/{timestamp}/train/{det_class}/model{n}.csv'
        with open(path, 'w') as file:
            w = csv.writer(file)
            w.writerows(t)

        with open(f'./model/{timestamp}/train/reference.csv', 'a') as file:
            w = csv.writer(file)
            w.writerow([n, path, should_buy, should_sell])

    # テスト用データ
    l = snapshot_list()
    n_min = len(l) - datasSize - future_sample - n_train
    n_max = len(l) - datasSize - future_sample

    os.makedirs(f'./model/{timestamp}/test/both', exist_ok=True)
    os.makedirs(f'./model/{timestamp}/test/neither', exist_ok=True)
    os.makedirs(f'./model/{timestamp}/test/should_buy', exist_ok=True)
    os.makedirs(f'./model/{timestamp}/test/should_sell', exist_ok=True)


    for n in range(n_min,n_max):
        print(n)

        # s = snapshots_10(l, n)
        s = snapshots_between(l, n, n+datasSize)
        t = snapshots_traj(s)

        s_current = nth_snapshot(l, n + datasSize)     # 現在の気配値
        s_future  = nth_snapshot(l, n + datasSize +future_sample) # 1サンプル後の気配値

        should_buy  = s_current[300][0] - s_future[301][0] < 0
        should_sell = s_current[301][0] - s_future[300][0] > 0

        det_class = 'neither'
        if should_buy & should_sell:
            det_class = 'both'
        elif should_buy & (not should_sell):
            det_class = 'should_buy'
        elif should_sell & (not should_buy):
            det_class = 'should_sell'
        else:
            det_class = 'neither'

        path = f'./model/{timestamp}/test/{det_class}/model{n}.csv'
        with open(path, 'w') as file:
            w = csv.writer(file)
            w.writerows(t)

        with open(f'./model/{timestamp}/test/reference.csv', 'a') as file:
            w = csv.writer(file)
            w.writerow([n, path, should_buy, should_sell])

'''
    # データから学習用データ・テスト用データを作る
    ## ラベル設定
    + 現在のbestBid,bestAskに対して利益の出るbestBid,bestAskがn分間以内に現れる
    ## 入力
    + datasSise: 1つのデータに用いる気配値の数量
    + n_train:   学習用データの数量
    + n_test:    テスト用データの数量
    ## 出力: なし
'''
def createModel2(datasSize, n_train, n_test):
    future_sample = 10
    # 学習用データ
    l = snapshot_list()
    print(l)
    n_min = len(l) - datasSize - future_sample - n_test -n_train -1
    n_max = len(l) - datasSize - future_sample - n_test -1

    timestamp = dt.now(timezone('UTC')).strftime('%Y%m%d%H%M')
    os.makedirs(f'./model/2_{timestamp}/train/both', exist_ok=True)
    os.makedirs(f'./model/2_{timestamp}/train/neither', exist_ok=True)
    os.makedirs(f'./model/2_{timestamp}/train/should_buy', exist_ok=True)
    os.makedirs(f'./model/2_{timestamp}/train/should_sell', exist_ok=True)


    for n in range(n_min,n_max):
        print(n)

        # s = snapshots_10(l, n)
        s = snapshots_between(l, n, n+datasSize)
        t = snapshots_traj(s)

        s_current = nth_snapshot(l, n + datasSize)     # 現在の気配値
        s_future = np.zeros((600,2,future_sample))
        for i in range(0,future_sample):
            # print(f'i: {i}')
            s_future[:,:,i]  = nth_snapshot(l, n + datasSize + i+1) # 1サンプル後までの気配値群
            # print(s_future.shape)

        max_sell = max(s_future[301,0,:])
        min_buy  = max(s_future[300,0,:])
        print(s_future[301,0,:])
        print(s_future[300,0,:])
        print(f'max sold prive: {max_sell}, min bought price: {min_buy}')
        should_buy  = s_current[300][0] - max_sell < 0 # 将来できるだけ高く売れればよい
        should_sell = s_current[301][0] - min_buy  > 0 # 将来できるだけ安く買えればよい
        print(f'future_buy: {should_buy}, future_sell: {should_sell}')

        det_class = 'neither'
        if should_buy & should_sell:
            det_class = 'both'
        elif should_buy & (not should_sell):
            det_class = 'should_buy'
        elif should_sell & (not should_buy):
            det_class = 'should_sell'
        else:
            det_class = 'neither'

        path = f'./model/2_{timestamp}/train/{det_class}/model{n}.csv'
        with open(path, 'w') as file:
            w = csv.writer(file)
            w.writerows(t)

        with open(f'./model/2_{timestamp}/train/reference.csv', 'a') as file:
            w = csv.writer(file)
            w.writerow([n, path, should_buy, should_sell])

    # テスト用データ
    l = snapshot_list()
    n_min = len(l) - datasSize - future_sample - n_train
    n_max = len(l) - datasSize - future_sample

    os.makedirs(f'./model/2_{timestamp}/test/both', exist_ok=True)
    os.makedirs(f'./model/2_{timestamp}/test/neither', exist_ok=True)
    os.makedirs(f'./model/2_{timestamp}/test/should_buy', exist_ok=True)
    os.makedirs(f'./model/2_{timestamp}/test/should_sell', exist_ok=True)


    for n in range(n_min,n_max):
        print(n)

        # s = snapshots_10(l, n)
        s = snapshots_between(l, n, n+datasSize)
        t = snapshots_traj(s)

        s_current = nth_snapshot(l, n + datasSize)     # 現在の気配値
        s_future = np.zeros((600,2,future_sample))
        for i in range(0,future_sample):
            # print(f'i: {i}')
            s_future[:,:,i]  = nth_snapshot(l, n + datasSize + i+1) # 1サンプル後までの気配値群
            # print(s_future.shape)

        max_sell = max(s_future[301,0,:])
        min_buy  = max(s_future[300,0,:])
        print(s_future[301,0,:])
        print(s_future[300,0,:])
        print(f'max sold prive: {max_sell}, min bought price: {min_buy}')
        should_buy  = s_current[300][0] - max_sell < 0 # 将来できるだけ高く売れればよい
        should_sell = s_current[301][0] - min_buy  > 0 # 将来できるだけ安く買えればよい
        print(f'future_buy: {should_buy}, future_sell: {should_sell}')

        det_class = 'neither'
        if should_buy & should_sell:
            det_class = 'both'
        elif should_buy & (not should_sell):
            det_class = 'should_buy'
        elif should_sell & (not should_buy):
            det_class = 'should_sell'
        else:
            det_class = 'neither'

        path = f'./model/2_{timestamp}/test/{det_class}/model{n}.csv'
        with open(path, 'w') as file:
            w = csv.writer(file)
            w.writerows(t)

        with open(f'./model/2_{timestamp}/test/reference.csv', 'a') as file:
            w = csv.writer(file)
            w.writerow([n, path, should_buy, should_sell])

if __name__ == '__main__':
    # createModel(20, 3000, 1000)
    createModel2(20, 1800, 100)

    # modelArr('201811011301')
    # loadModel('201811011301',20)

    # datasArr_test, y_test, datasArr_train, y_train = loadDatas('2_201811230049')
    # np.save('raw_test',datasArr_test)
    # np.save('raw_train',datasArr_train)
    # np.save('y_test',y_test)
    # np.save('y_train',y_train)

    # datasArr_test = np.load('raw_test.npy')
    # datasArr_train = np.load('raw_train.npy')
    # # print(datasArr_test.shape)
    #
    # x_test  = []
    # x_train = []
    # for datasArr in datasArr_test:
    #     x_test.append(v.snapshots2Gray(datasArr))
    #
    # for datasArr in datasArr_train:
    #     x_train.append(v.snapshots2Gray(datasArr))
    #
    # np.save('x_test',x_test)
    # np.save('x_train',x_train)
