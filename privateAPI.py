# -*- coding: utf-8 -*-

# HTTP Private API
import errorLogger as error

import requests
import time
from datetime import datetime
import hmac
import hashlib
import json

import emailMessanger as email

endpoint = 'https://api.bitflyer.jp'

def getTimestamp():
    now = datetime.now()
    unix = int(now.timestamp())
    return str(unix)

class API(object):
    """docstring for API."""
    def __init__(self):
        super(API, self).__init__()
        apiPath = 'API.txt'
        with open(apiPath) as f:
            l_strip = [s.strip() for s in f.readlines()]
            self.API_KEY    = l_strip[0]
            self.API_SECRET = l_strip[1]
            print(self.API_KEY)
            print(self.API_SECRET)
        return

    def sign(self, method, path, body, timestamp):
        text = timestamp + method + path + body
        bytesKey  = self.API_SECRET.encode('utf-8')
        bytesText = text.encode('utf-8')
        sign = hmac.new(bytesKey, bytesText, hashlib.sha256).hexdigest()
        return sign

    def headers(self, timestamp, sign):
        h = {
            'ACCESS-KEY'       : self.API_KEY,
            'ACCESS-TIMESTAMP' : timestamp,
            'ACCESS-SIGN'      : sign,
            'Content-Type'     : 'application/json'
        }
        return h

def privateGetRequest(path, *payload):
    api = API()
    url = endpoint + path
    t = getTimestamp()
    s = api.sign('GET', path, '', t)
    while True:
        try:
            r = requests.get(url, headers= api.headers(t, s))
            return r.json(), r.status_code
        except requests.exceptions.RequestException as e:
            print("Error: ", e)
            error.output(str(e))
            time.sleep(5)

def privatePostRequest(path, body):
    api = API()
    url = endpoint + path
    t = getTimestamp()
    print(body)
    s = api.sign('POST', path, json.dumps(body), t)
    while True:
        try:
            r = requests.post(url, headers= api.headers(t, s), data=json.dumps(body))
            return r.status_code
        except requests.exceptions.RequestException as e:
            print("Error: ", e)
            print("We cannot complete trade.")
            error.output(str(e))

def getPermissions():
    path = '/v1/me/getpermissions'
    r = privateGetRequest(path)
    return r

def getBalance():
    path = '/v1/me/getbalance'
    r = privateGetRequest(path)
    return r

# 証拠金の状態を取得
def getCollateral():
    path = '/v1/me/getcollateral'
    r = privateGetRequest(path)
    return r

# 通貨別の証拠金の数量を取得
def getCollateralAccounts():
    path = '/v1/me/getcollateralaccounts'
    r = privateGetRequest(path)
    return r

# 預入用アドレス取得
def getAddresses():
    path = '/v1/me/getaddresses'
    r = privateGetRequest(path)
    return r

# 仮想通貨預入履歴
def getCoinIns():
    path = '/v1/me/getcoinins'
    r = privateGetRequest(path)
    return r

# 仮想通貨送付履歴
def getCoinOuts():
    path = '/v1/me/getcoinouts'
    r = privateGetRequest(path)
    return r

# 銀行口座一覧取得
def getBankAccounts():
    path = '/v1/me/getbankaccounts'
    r = privateGetRequest(path)
    return r

# 入金履歴
def getDeposits():
    path = '/v1/me/getdeposits'
    r = privateGetRequest(path)
    return r

# 出金履歴
def getWithdrawals():
    path = '/v1/me/getwithdrawals'
    r = privateGetRequest(path)
    return r

# 注文の一覧を取得
def getChildOrders():
    path = '/v1/me/getchildorders'
    r = privateGetRequest(path)
    return r

# 親注文の一覧を取得
def getParentOrders():
    path = '/v1/me/getparentorders'
    r = privateGetRequest(path)
    return r

# 親注文の詳細を取得
def getParentOrders(productCode, count, before, after, *parentOrderState):
    path = '/v1/me/getparentorder?' + 'product_code=' + productCode + '&count=' + str(count) + '&before=' + str(before) + '&after=' + str(after)
    if len(parentOrderState) > 0:
        path += parentOrderState[0]
    r = privateGetRequest(path)
    return r

# 約定の一覧を取得
def getExecutions(productCode, count, before, after, *childOrderid):
    path = '/v1/me/getexecutions?' + 'product_code=' + productCode + '&count=' + str(count) + '&before=' + str(before) + '&after=' + str(after)
    r = privateGetRequest(path)
    return r

# 建玉の一覧を取得
def getPositions():
    path = '/v1/me/getpositions?' + 'product_code=' + "FX_BTC_JPY"
    r = privateGetRequest(path)
    return r

# 証拠金の変動履歴を取得
def getCollateralHistory(count, before, after):
    path = '/v1/me/getcollateralhistory?'+'count='+ str(count) + '&before=' + str(before) + '&after=' + str(after)
    r = privateGetRequest(path)
    return r

# 取引手数料を取得
def getTradingCommission(productCode):
    path = '/v1/me/gettradingcommission?'+'product_code='+ productCode
    r = privateGetRequest(path)
    return r

# 新規注文を出す
def sendChildOrder(productCode, side, size, limit=False, expired=1440, TIF='GTC'):
    path = '/v1/me/sendchildorder'
    body = {
        'product_code' : productCode,
        'child_order_type' : 'MARKET',
        'side' : side,
        'size' : str(size),
        'minute_to_expire' : str(expired),
        'time_in_force' : TIF
    }
    r = privatePostRequest(path, body)

    return r

# 注文をキャンセルする
def cancelChildOrder(productCode, childOrderId):
    path = '/v1/me/cancelchildorder'
    body = {
        'product_code' : productCode,
        'child_order_id' : str(childOrderId)
    }
    r = privatePostRequest(path, body)
    return r

if __name__ == '__main__':
    # res = getPermissions()
    # print(res)
    #
    res = getBalance()
    print(res)
    #
    # res = getCollateral()
    # print(res)
    #
    # res = getCollateralAccounts()
    # print(res)
    #
    # res = getAddresses()
    # print(res)
    #
    # res = getCoinIns()
    # print(res)
    #
    # res = getCoinOuts()
    # print(res)
    #
    # res = getBankAccounts()
    # print(res)
    #
    # res = getDeposits()
    # print(res)
    #
    res = getExecutions("FX_BTC_JPY", 100, 100, 1)
    print(res)
    #
    # res = getCollateralHistory(100, 100, 1)
    # print(res)
    #
    res = getTradingCommission("BTC_JPY")
    print(res)

    # res = sendChildOrder("BTC_JPY", side="BUY", size=0.001)
    # print(res)

    # res = cancelChildOrder("BTC_JPY", "JOR20150707-055555-022222")
    # print(res)
