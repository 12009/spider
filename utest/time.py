# -*- coding: utf-8 -*-

# 测试 getTime 函数
# getTime 是封装的通用型时间处理函数

import unittest
from utils.time import getTime

#测试类
class timeTest(unittest.TestCase):
    def test1_now(self):
        now = getTime()
        result = isinstance(now, (int))
        self.assertTrue(result)

    def test2_now_str(self):
        now = getTime('%Y%m%d')
        #print(now)
        result = isinstance(now, (str))
        self.assertTrue(result)

    def test3_time_str(self):
        now = getTime('%Y-%m-%d', '20170101')
        #print(now)
        result = isinstance(now, (str))
        self.assertTrue(result)

    def test4_time_int(self):
        now = getTime(None, '20170101')
        #print(now)
        result = isinstance(now, (int))
        self.assertTrue(result)

params = {}
params['execute_delay'] = 3600
print(getTime())
now = getTime() + params['execute_delay']
print(now, type(now) == int)
dateStr = getTime('%Y%m%d %H%M%S', now)
print(dateStr)

