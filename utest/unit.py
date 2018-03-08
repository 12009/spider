#coding=utf-8

import unittest
from utest.time import timeTest
from utest.api import ApiTest

#跑全部测试用例
#unittest.main(verbosity = 2)

#跑指定测试用例
suite = unittest.TestSuite()
suite.addTest(ApiTest("testTaskaddOk"))
runner = unittest.TextTestRunner()
runner.run(suite)


