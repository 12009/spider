import json
import string
from time import time
from urllib.parse import quote
from urllib.request import Request, urlopen, HTTPRedirectHandler, build_opener
from urllib.request import HTTPBasicAuthHandler, HTTPPasswordMgrWithDefaultRealm, ProxyHandler, ProxyBasicAuthHandler
from utils.logger import loggerSpider as logger
from urllib.error import URLError, HTTPError
from socket import timeout as timeoutError

def formatHeaders(headers = {}):
    '''格式化header头'''
    headersDict = {}
    for row in headers:
        headersDict[row[0]] = row[1]
    return headersDict

#捕获重定向信息
class RedirectHandler(HTTPRedirectHandler):
    redirects = []

    def __init__(self):
        self.redirects = []

    def redirect_request(self, req, fp, code, msg, hdrs, newurl):
        self.redirects.append({'code':code, 'url':newurl})
        return HTTPRedirectHandler.redirect_request(self, req, fp, code, msg, hdrs, newurl)

def spiderRequest(url=None, method="GET", data={}, headers={}, timeout=10, auth = {}, proxy={}):
    headers['Cache-Control'] = 'no-chache'
    method = method.upper()
    start = time()
    try:
        #跳转记录
        redirect_handler = RedirectHandler()

        #basic验证
        auth_handler = HTTPBasicAuthHandler()
        if auth and 'user' in auth.keys() and 'passwd' in auth.keys():
            passwdHandler = HTTPPasswordMgrWithDefaultRealm()
            passwdHandler.add_password(realm=None, uri=url, user=auth['user'], passwd=auth['passwd'])
            auth_handler = HTTPBasicAuthHandler(passwdHandler)

        #代理
        proxy_handler = ProxyHandler()
        if proxy and 'url' in proxy.keys():
           proxy_handler = ProxyHandler({'http': proxy['url']})

        #代理验证
        proxy_auth_handler = ProxyBasicAuthHandler()
        if proxy and 'url' in proxy.keys() and 'user' in proxy.keys() and 'passwd' in proxy.keys():
           proxyPasswdHandler = HTTPPasswordMgrWithDefaultRealm()
           proxyPasswdHandler.add_password(realm=None, uri=proxy['url'], user=proxy['user'], passwd=proxy['passwd'])
           proxy_auth_handler = ProxyBasicAuthHandler(proxyPasswdHandler)

        opener = build_opener(redirect_handler, auth_handler, proxy_handler, proxy_auth_handler)
        request_handler= Request(quote(url, safe=string.printable), method=method)
        for key, value in headers.items():
            request_handler.add_header(key, value)
        response = opener.open(request_handler, timeout=timeout)
        end = time()
        return {
            'url': url,
            'method': method,
            'request_headers': request_handler.headers,
            'response_headers': formatHeaders(response.getheaders()),
            'http_code': response.status,
            'redirects':redirect_handler.redirects,
            'body': response.read(),
            'nettime': end-start,
            'error':''
        }
    except HTTPError as e:          # 400 401 402 403 500 501 502 503 504
        logger.error(url + "::::::::" + repr(e))
        end = time()
        return {
            'url': url,
            'method': method,
            'request_headers': headers,
            'response_headers': dict(e.headers),
            'http_code': e.code,
            'redirects': [],
            'body': b'',
            'nettime': end-start,
            'error': repr(e)
        }
    except URLError as e:
        logger.error(url + "::::::::" + repr(e))
        end = time()
        return {
            'url': url,
            'method': method,
            'request_headers': headers,
            'response_headers': {},
            'http_code': 0,
            'redirects': [],
            'body': b'',
            'nettime': end-start,
            'error': repr(e)
        }
    except timeoutError as e:
        logger.error(url + "::::::::" + repr(e))
        end = time()
        return {
            'url': url,
            'method': method,
            'request_headers': headers,
            'response_headers': {},
            'http_code': 0,
            'redirects': [],
            'body': b'',
            'nettime': end-start,
            'error': repr(e)
        }
    except Exception as e:
        logger.exception(e)
        logger.error(url + "::::::::" + repr(e))
        return {
            'url': url,
            'method': method,
            'request_headers': headers,
            'response_headers': {},
            'http_code': 0,
            'redirects': [],
            'body': b'',
            'nettime': 0,
            'error': repr(e)
        }

#url = 'http://local.com/redirect.php'
#url = 'http://local.com/403.php'
#url = 'http://local.com/404.php'
#url = 'http://local.com/500.php'
#url = 'http://local.com/502.php'
#url = 'http://locals.comss/403.php'
#url = 'http://local.com/index.html'
#response = spiderRequest(url, timeout=10)
#response = spiderRequest(url, timeout=10, auth={'user':'jingwu', 'passwd':'jingwu'})
#response = spiderRequest(url, timeout=10, proxy={'url':'http://127.0.0.1:8210/'})
#response = spiderRequest(url, timeout=10, proxy={'url':'http://127.0.0.1:8210/', 'user':'jingwu', 'passwd':'jingwu'})
#response = spiderRequest(url, timeout=10, auth={'user':'jingwu', 'passwd':'jingwu'}, proxy={'url':'http://127.0.0.1:8210/', 'user':'jingwu', 'passwd':'jingwu'})
#print(response)

