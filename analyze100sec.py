# -*- coding:'utf-8' -*-
import os, csv
import math
from datetime import datetime

def execute(current):
    now = datetime.now()
    date = now.strftime('%Y-%m-%d')
    with open('./'+date+'/midprices.csv','r') as f:
    # with open('./2018-08-25/midprices.csv','r') as f:
        r = csv.reader(f, lineterminator='\r\n',skipinitialspace=True)
        # print(r)
        len = 0
        list = []
        for line in r:
            len += 1
            # d = line.rstrip('\r\n')
            if len % 2 == 1:
                list.append(line)

        # print(list)

        size = len //2
        # print(size)

        if size >= 10:
            avg = 0
            for i in range(1,11):
                avg += float(list[size-i][1])
            avg /= 10
            # print('avg:', avg)

            var = 0
            for i in range(1,11):
                var += (float(list[size-i][1]) -avg)**2
            var /= 10
            if var >= 0.01:
                sd = math.sqrt(var) # TODO ゼロ割が発生する可能性がある
                val = (current - avg)/sd
                return val
            else:
                return 0.0
        else:
            return 0.0

class Analyzer(object):
    """docstring for Analyzer."""
    def __init__(self):
        super(Analyzer, self).__init__()
        self.pastPrice = 0.0
        self.price     = 0.0
        self.dPrice    = 0.0

    def run(self, newPrice):
        self.pastPrice = self.price
        self.price = newPrice
        self.dPrice = self.price - self.pastPrice

        print(self.dPrice)
        return execute(newPrice)
