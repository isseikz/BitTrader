# -*- coding: utf-8 -*-

# HTTP Public API
import errorLogger as error

import requests
import time
endpoint = 'https://api.bitflyer.jp/v1/'

def publicGetRequest(url):
    while True:
        try:
            r = requests.get(url, timeout=1.0)
            return r
        except requests.exceptions.RequestException as e:
            print("Error: ", e)
            error.output(str(e))
            time.sleep(5)


# マーケット一覧
def getMarkets():
    url = endpoint + 'getmarkets'
    r = publicGetRequest(url)
    return r.json()

# 板情報
def getBoard():
    url = endpoint + 'getboard'
    r = publicGetRequest(url)
    return r.json()

# Ticker
def getTicker():
    url = endpoint + 'getticker'
    r = publicGetRequest(url)
    return r.json()

# 約定履歴
def getExecutions():
    url = endpoint + 'getexecutions'
    r = publicGetRequest(url)
    return r.json()

# 板の状態
def getBoardState():
    url = endpoint + 'getboardstate'
    r = publicGetRequest(url)
    return r.json()

# 取引所の状態
def getHealth():
    url = endpoint + 'gethealth'
    r = publicGetRequest(url)
    return r.json()

# チャット
def getChats():
    url = endpoint + 'getchats'
    r = publicGetRequest(url)
    return r.json()

if __name__ == '__main__':
    # res = getMarkets()
    # print(res)
    # res = getBoard()
    # print(res)
    # res = getTicker()
    # print(res)
    # res = getExecutions()
    # print(res)
    # res = getBoardState()
    # print(res)
    res = getHealth()
    print(res)
    # res = getChats()
