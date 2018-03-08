# -*- coding: utf-8 -*-

import re
import os
import time

os.environ["TZ"] = "Asia/Shanghai"
time.tzset()


# 1. 当前时间戳，到秒
# 2. 格式化当前时间显示
# 3. 转换 字符串时间为其他格式，如：20170101->2017-01-01, 20170101010101->20170101 01:01:01, 20170101->1490601154 等
def getTime(formatStr = None, timeStr = None):
    if timeStr and type(timeStr) == str:
        timeFormatStr = ''
        if re.match(r'^\d{4}\d{2}\d{2}$', timeStr):
            timeFormatStr = '%Y%m%d'
        elif re.match(r'^\d{4}-\d{2}-\d{2}$', timeStr):
            timeFormatStr = '%Y-%m-%d'
        elif re.match(r'^\d{4}\d{2}\d{2}\d{2}\d{2}\d{2}$', timeStr):
            timeFormatStr = '%Y%m%d%H%M%S'
        elif re.match(r'^\d{4}\d{2}\d{2}\s\d{2}\d{2}\d{2}$', timeStr):
            timeFormatStr = '%Y%m%d %H%M%S'
        elif re.match(r'^\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}$', timeStr):
            timeFormatStr = '%Y-%m-%d %H:%M:%S'
        else:
            raise Exception("don't support this format: " + timeStr)
        timeTmp = time.mktime(time.strptime(timeStr, timeFormatStr))
    elif timeStr and type(timeStr) == int:
        timeTmp = float(timeStr)
    else:
        timeTmp = time.time()

    if formatStr:
        return time.strftime(formatStr, time.localtime(timeTmp))
    else:
        return int(str(timeTmp).split('.')[0])

def formatTimestamp(timestamp, formatStr="%Y-%m-%d %H:%M:%S"):
    '''格式化时间戳'''
    return timestamp.strftime(formatStr)

def now_format():
    '''格式化显示当前时间'''
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def getDate():
    return time.strftime('%Y%m%d', time.localtime(time.time()))

