# -*- coding: utf-8 -*-

import json
import unittest
from urllib.request import Request, urlopen
from urllib.parse import urlencode

class ApiTest(unittest.TestCase):

    def setUp(self):
        self.baseUrl = 'http://127.0.0.1:9022/'
        self.appKey = 'tester_app'
        self.token = 'wbsllmigfa4ct0zp4gdd4hx2umpijg4e'
        return self

    def testTokenOk(self):
        apiToken = 'token/%s'
        url = self.baseUrl + apiToken % appKey
        request = Request(url)
        request.add_header('token', '')
        response = urlopen(request)
        body = response.read().decode()
        #httpcode = response.status
        #headers = response.getheaders()

        jsonData = json.loads(body)
        token = jsonData['token']

        tokenLen = len(token)
        expected = 32
        self.assertEqual(expected, tokenLen)

    def testTokenError(self):
        appKeyError = 'tester_apps'
        url = self.baseUrl + apiToken % appKeyError
        request = Request(url)
        request.add_header('token', '')
        response = urlopen(request)
        body = response.read().decode()
        #httpcode = response.status
        #headers = response.getheaders()

        jsonData = json.loads(body)
        token = jsonData['token']

        tokenLen = len(token)
        expected = 0
        self.assertEqual(expected, tokenLen)

    def testTaskaddOk(self):
        apiTaskadd = 'task/save'
        url = self.baseUrl + apiTaskadd
        params = {
            'app_id':1,
            'type':'spider',
            'start_url':'http://www.ifeng.com',
            'limit_depth':2,
            'limit_total':5000,
            'limit_time':7200,
            'limit_subdomain':0,
            'limit_noimage':0,
            'url_unique_mode':'url-query',   #url   url-query
            'limit_js':1,
            'notify_url':'http://localhost/',
            'source_ip':'',
            'crontab':'*/2 * * * *',
            'proxies':'',
        }
        request = Request(url, data=urlencode(params).encode('utf8'), method='post')
        request.add_header('token', self.token)
        response = urlopen(request)
        body = response.read().decode()
        jsondata = json.loads(body)
        self.assertEqual(jsondata['status'], 'ok')

#testToken()
#if __name__=='__main__':
#    unittest.main()

