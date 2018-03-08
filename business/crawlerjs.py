# -*- coding: utf-8 -*-

import json
import chardet
from db import mongodb as mgdb
from urllib.parse import urlparse
from utils.url import isUrl
from utils.security import md5
from utils.time import getTime
from utils.html import mime2file, formatCharset, parseContentType
from utils.spider2 import parseHref as parseHref2, parseForms as parseForms2, parseMouseEvent
from utils.logger import loggerSpider as logger
from utils.spider_request import spiderRequest
# from business.task import mg_spiderjsurl_save

def _formatUrls(urls = None):
    results = []
    for url in urls:
        if type(url) == str:
            results.append({'url':url, 'method':'get', 'post':''})
        else:                                   #type(url) == dict:
            keys = url.keys()
            if 'url' in keys:
                if 'method' in keys and url['method'] == 'GET':
                    results.append({'url':url['url'], 'method':'get', 'post':''})
                else:
                    if 'data' in keys:
                        results.append({'url':url['url'], 'method':url['method'], 'post':url['data']})
                    if 'fields' in keys:
                        results.append({'url':url['url'], 'method':url['method'], 'post':url['fields']})
            else:
                continue

    return results

def _parseForJs(currentUrl = ''):
    '''使用js解析'''
    urls = []
    results = parseHref2(currentUrl, ['a', 'link'])
    if 'links' in results.keys() and results['links']:
        urls.extend(_formatUrls(results['links']))
    if 'ajaxs' in results.keys() and results['ajaxs']:
        urls.extend(_formatUrls(results['ajaxs']))
    if 'results' in results.keys() and results['results']:
        urls.extend(_formatUrls(results['results']))

    results = parseForms2(currentUrl)
    if 'links' in results.keys() and results['links']:
        urls.extend(_formatUrls(results['links']))
    if 'ajaxs' in results.keys() and results['ajaxs']:
        urls.extend(_formatUrls(results['ajaxs']))
    if 'results' in results.keys() and results['results']:
        urls.extend(_formatUrls(results['results']))

    #results = parseMouseEvent(currentUrl)
    #if 'links' in results.keys() and results['links']:
    #    urls.extend(_formatUrls(results['links']))
    #if 'ajaxs' in results.keys() and results['ajaxs']:
    #    urls.extend(_formatUrls(results['ajaxs']))
    #if 'results' in results.keys() and results['results']:
    #    urls.extend(_formatUrls(results['results']))
    return urls

def _parseForUrl(row = {}):
    '''解析URL记录'''
    url = row['url'].strip()
    if not isUrl(url):  return {}
    method = row['method'].upper()
    post = json.dumps(row['post'], ensure_ascii=False) if row['post'] else ''

    return {
        'url': url,
        'method': method,
        'post': post,
    }

def crawljs(taskInfo):
    try:
        #已抓取过，不再抓取
        if taskInfo['status'] not in (0, 1):
            return True
        #抓取页面源代码
        requestInfo = spiderRequest(taskInfo['url'])

        parseResults = []
        results = _parseForJs(taskInfo['url'])
        for record in results:
            urlRow = _parseForUrl(record)
            if not urlRow: continue
            parseResults.append(urlRow)
        updateRow = {}
        updateRow['id'] = taskInfo['id']
        updateRow['http_code'] = requestInfo['http_code']
        updateRow['response_headers'] = json.dumps(requestInfo['response_headers'], ensure_ascii=False)
        updateRow['body'] = requestInfo['body']
        updateRow['md5_body'] = md5(requestInfo['body'])
        updateRow['parse_result'] = json.dumps(parseResults, ensure_ascii=False)
        updateRow['status'] = 2
        updateRow['end_at'] = getTime('%Y-%m-%d %H:%M:%S')
        #保存数据结果
        mg_spiderjsurl_save(updateRow)
    except Exception as e:
        logger.exception(e)
        return False

def mg_spiderjsurl_save(record, urlid = None):
    if 'id' in record.keys():
        if not urlid:
            urlid = record['id']
            del(record['id'])
        else:
            del(record['id'])
    if not urlid and 'url' not in record.keys(): return False
    #
    if not urlid and 'method' not in record.keys():
        record['method'] = 'GET'
    if 'url' in record.keys():
        record['md5_url'] = md5(record['url'])
    if 'body' in record.keys():
        record['md5_body'] = md5(record['body'])
    #
    dbFields = ['id','url','md5_url','referer','method','status','start_at','end_at','create_at']
    mongoFields = ['id','url','md5_url','referer','method','http_code,','request_headers,','response_headers',
        'redirects','body','md5_body','parse_result','error','status','start_at','end_at','create_at']
    insertRow = {}
    for field in dbFields:
        if field in record.keys():
            insertRow[field] = record[field]
    if insertRow:
        if urlid:
            db.updatebyid('spiderjs_url', insertRow, urlid)
        else:
            urlid = db.insert('spiderjs_url', insertRow)
    jsRow = db.fetchone("select * from spiderjs_url where id=:id limit 1", {'id':urlid})
    mongoRow = mgdb.c_getbyid('spiderjsurl', urlid)
    mongoRow = mongoRow if mongoRow else {}

    for field in mongoFields:
        value = ''
        if field in mongoRow.keys():
            value = mongoRow[field]
        if field in record.keys():
            value = record[field]
        if field in jsRow.keys():
            value = jsRow[field]
        mongoRow[field] = value

    mgdb.spiderjsurl_save(mongoRow)
    return urlid

