from pathlib import Path
import csv, os
import numpy as np
from datetime import datetime as dt
from pytz import timezone

# TODO: リストアップ
def snapshot_list():
    p = Path("./log/snapshot/")
    l = list(p.glob("*.csv"))
    # print(l)
    return l

# TODO: n 番目から n+ 10番目までのスナップショットのリストを取得
def snapshots_10(l, n):
    s = l[n:n+10]
    # print(s)
    return s

def str2float(str_list):
    return list(map(float, str_list))

# TODO: 10個のスナップショットから平面を作成
def snapshots_traj(l):
    traj = np.zeros((10,600,2), dtype=float)
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
        print(l[n])
        reader = csv.reader(file)
        # print(list(reader))
        lf = [row for row in list(reader) if row != []]
        s = np.array(lf)
        # print(lf)
        sf = s.astype(np.float)
        # print(sf)
    return sf

def makeModelData(quantity):
    # 学習用データ
    l = snapshot_list()
    n_max = len(l) - 20 - 1001

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


if __name__ == '__main__':
    # 学習用データ
    l = snapshot_list()
    n_max = len(l) - 20 - 1001

    timestamp = dt.now(timezone('UTC')).strftime('%Y%m%d%H%M')
    os.makedirs(f'./model/{timestamp}/train/both', exist_ok=True)
    os.makedirs(f'./model/{timestamp}/train/neither', exist_ok=True)
    os.makedirs(f'./model/{timestamp}/train/should_buy', exist_ok=True)
    os.makedirs(f'./model/{timestamp}/train/should_sell', exist_ok=True)


    for n in range(0,n_max):
        print(n)

        s = snapshots_10(l, n)
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

    # テスト用データ
    l = snapshot_list()
    n_min = len(l) - 20 - 1000
    n_max = len(l) - 20

    os.makedirs(f'./model/{timestamp}/test/both', exist_ok=True)
    os.makedirs(f'./model/{timestamp}/test/neither', exist_ok=True)
    os.makedirs(f'./model/{timestamp}/test/should_buy', exist_ok=True)
    os.makedirs(f'./model/{timestamp}/test/should_sell', exist_ok=True)


    for n in range(n_min,n_max):
        print(n)

        s = snapshots_10(l, n)
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

        path = f'./model/{timestamp}/test/{det_class}/model{n}.csv'
        with open(path, 'w') as file:
            w = csv.writer(file)
            w.writerows(t)

        with open(f'./model/{timestamp}/test/reference.csv', 'a') as file:
            w = csv.writer(file)
            w.writerow([n, path, should_buy, should_sell])
