# -*- coding: utf-8 -*-

import sys
import json
import chardet
from time import time
from utils import mq as Mq
import business.task as bTask
from utils.security import md5
from db import mongodb as mgdb
from urllib.parse import urlparse
from business import mirror as bMirror
from utils.browser import parse_darklink
from common import db, redis, mongoSpider
from urllib.request import Request, urlopen
from os.path import basename, dirname, exists
from utils.spider_request import spiderRequest
from utils.logger import loggerSpider as logger
from utils.url import patternPath, patternQuery
from utils.time import getTime, getDate, now_format
from utils.file import writeBin as fwriteBin, mkdirs, ydfs_upload
from utils.html import mime2file, formatCharset, parseContentType
from utils.url import isUrl, extension, getDomainNoPort, getDomainMain
from utils.spider2 import parseHref as parseHref2, parseForms as parseForms2, parseMouseEvent
from utils.spider import parseUrlByMatchQuotes, parseHref, parseSrc, checklogout, parseCharset, parseUrlFromJs, parseForm
from config.config import PATH_TMP_UPLOAD, MIRROR_PROXY

batchKey = 'mq_batch'
mqidKey = 'mq_id'
staticExts = ['js', 'javascript', 'css', 'png', 'jpg', 'gif', 'ico']

def _getDomainType(url, siteDomain):
    domain = getDomainNoPort(url)
    domainMain = getDomainMain(domain)
    if domain == siteDomain:
        return 'self'
        domainType = 'self'
    elif siteDomain in domain:
        return 'child'
    elif domain in siteDomain:
        return 'parent'
    else:
        return 'other'

# def _checkUrlExists(executeid, url, method):
#     '''检查url是否存在'''
#     key = 'exists_%s' % executeid
#     value = method + '-' + url
#     hkey = md5(value)
#     if redis.hexists(key, hkey): return True
#
#     redis.hset(key, hkey, value)
#     redis.expire(key, 86400)
#     return False


def _checkUrlExists(executeid, url, method, invisible):
    '''检查url是否存在'''
    key = 'exists_%s' % executeid
    value = method + '-' + url + str(invisible)
    hkey = md5(value)
    if redis.hexists(key, hkey): return True

    redis.hset(key, hkey, value)
    redis.expire(key, 86400)
    return False


def _urls_uniq(urlItems):
    '''对格式化后的URL去重'''
    urlsUniq = {}
    for i in urlItems:
        key = md5(i['url'] + i['method'] + str(i['invisible']))
        if key not in urlsUniq.keys(): urlsUniq[key] = i
    return list(urlsUniq.values())


def _formatResponse(requestInfo, execute, urlInfo, fileInfo=('','')):
    '''格式化UrlItem'''
    try:
        response = {}
        response['nettime'] =  requestInfo['nettime']
        if requestInfo['error'] or requestInfo['http_code'] != 200:
            response['status'] =  3
            response['http_code'] = requestInfo['http_code']
            response['error'] = repr(requestInfo['error'])
            response['end_at'] =  now_format()
            response['depth'] =  urlInfo['depth']
        else:
            response['status'] =  2
            response['end_at'] =  now_format()
            response['depth'] =  urlInfo['depth']
            response['md5_url'] =  md5(urlInfo['url'])
            response['md5_body'] =  md5(requestInfo['body'])
            response['redirects'] =  json.dumps(requestInfo['redirects'], ensure_ascii=False)
            response['http_code'] =  requestInfo['http_code']
            response['request_headers'] =  json.dumps(requestInfo['request_headers'], ensure_ascii=False)
            response['response_headers'] =  json.dumps(requestInfo['response_headers'], ensure_ascii=False)
            response['file_name'] = fileInfo[0]
            response['file_path'] = fileInfo[1]
        return response
    except Exception as e:
        logger.exception(e)
        return False

def _formatUrls(urls = None, invisible=0):
    '''格式化URL'''
    results = []
    for item in urls:
        if type(item) == str:

            urlRow = {'url':item, 'method':'get', 'post':''}
        else:
            if 'url' not in item.keys(): continue
            urlRow = item
        keys = urlRow.keys()

        parseResult = urlparse(urlRow['url'])
        pattern_path = patternPath(parseResult[2])
        pattern_query = patternQuery(parseResult[4])
        #移除锚点
        urlRow['url'] = urlRow['url'][0:-(len(parseResult[5])+1)] if parseResult[5] else urlRow['url']
        postdata = ''
        if 'method' in keys and urlRow['method'] != 'GET':
            if 'data' in keys: postdata = urlRow['data']
            if 'fields' in keys: postdata = urlRow['fields']

        results.append({
            'url':urlRow['url'], 
            'query':parseResult[4], 
            'method':urlRow['method'].upper(), 
            'post':postdata, 
            'invisible':invisible, 
            'pattern_path':pattern_path, 
            'pattern_query':pattern_query})

    return results


def _formatOutlink(execute, referer, url, md5Body='', invisible=0):
    '''格式化外链'''
    return {
        'task_id': execute['task_id'],
        'execute_id': execute['id'],
        'domain': execute['domain'],
        'referer': referer,
        'md5_referer': md5(referer),
        'url': url, 
        'md5_url': md5(url),
        'md5_body': md5Body, 
        'invisible': invisible, 
        'filterwords': '', 
        'date':getDate(), 
        'create_at': now_format(),
        'update_at': now_format()
    }


def _formatStatic(domain, url, filename, filekey, filetype, md5Body):
    return {
        'domain': domain,
        'url': url,
        'file_name': filename,
        'file_key': filekey,
        'file_type': filetype,
        'md5_url': md5(url),
        'md5_body': md5Body,
        'create_at': now_format(),
        'update_at': now_format(),
    }


def _formatParse(execute, urlInfo, result, md5Body, parseType='regular'):
    return {
        'site_id': execute['site_id'],
        'task_id': execute['task_id'],
        'app_id': execute['app_id'],
        'execute_id': execute['id'],
        'url_id': urlInfo['id'],
        'referer': urlInfo['referer'],
        'url': urlInfo['url'],
        'md5_url': urlInfo['md5_url'],
        'md5_body': md5Body,
        'parse_type': 'regular',
        'result': result,
        'create_at': now_format(),
        'update_at': now_format()
    }


def download(requestInfo, urlInfo, execute, fileType = 'html'):
    '''下载文件'''
    try:
        #如果有异常，直接返回
        md5Body = md5(requestInfo['body'])
        result = mgdb.static_get(execute['domain'], md5Body)
        if result: return (result['file_name'], result['file_key'])

        localfile = '%s/%s/%s.tmp' %  (PATH_TMP_UPLOAD, execute['domain'], md5Body)
        if not exists(dirname(localfile)):  mkdirs(dirname(localfile))
        if fileType == 'html':
            filename = "%s_%s.html" % (execute['id'], urlInfo['id'])
            filekey = 'html/%s/%s/%s_%s.html.%s' % (execute['domain'], execute['task_id'], execute['id'], urlInfo['id'], md5Body)
            fwriteBin(localfile, requestInfo['body'])
            fileType = 'html'
        else:
            filename = basename(requestInfo['url'])
            filekey = "static/%s/%s.%s" % (execute['domain'], requestInfo['url'][7:], md5Body)
            fwriteBin(localfile, requestInfo['body'])
            fileType = 'img'
        filepath = ydfs_upload(filekey, localfile)
        mgdb.c_insert('static', _formatStatic(execute['domain'], requestInfo['url'], filename, filekey, fileType, md5Body))
        return (filename, filekey)
    except Exception as e:
        logger.exception(e)
        return ('', '')


def parse_reg(requestInfo):
    try:
        # 内容为html, 检测编码，并进行解码
        try:
            charset = chardet.detect(requestInfo['body'])['encoding']
            charset = formatCharset(charset)
            body = requestInfo['body'].decode(charset)
        except Exception as e:
            charset = 'GBK' if charset == 'GB2312' else 'GBK'
            body = requestInfo['body'].decode(charset)
            logger.exception(e)

        #使用正则解析
        urls = []
        currentUrl = requestInfo['redirects'][-1]['url'] if requestInfo['redirects'] else requestInfo['url']
        urls.extend(_formatUrls(parseUrlByMatchQuotes(currentUrl, body)))      #双引号及单引号中间的链接
        urls.extend(_formatUrls(parseHref(currentUrl, body)))                  #解析href
        urls.extend(_formatUrls(parseSrc(currentUrl, body)))                   #解析src    img script frame iframe
        urls.extend(_formatUrls(parseUrlFromJs(currentUrl, body))) #从JS中解析URL
        return urls
    except Exception as e:
        logger.exception(e)
        return []


def parse_browser(requestInfo):
    '''通过浏览器方式解析'''
    try:
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
    except Exception as e:
        logger.exception(e)
        return False


def crawl(urlInfo):
    uI = urlInfo
    execute = mgdb.execute_getbyid(urlInfo['execute_id'])
    if not execute: return False
    sql = "select * from task_piping where task_id=:task_id and type=:type and status=:status"
    pipingDark = db.fetchone(sql, {'task_id': execute['task_id'], 'type': 'darklink', 'status': 1})

    try:
        ##如果任务已结束，则返回
        #if execute['status'] == 2 or urlInfo['status'] == 2:
        #    return True

        logger.info("crawl:uid[%s]:tid[%s]:eid[%s]:method[%s]::%s" % (
            uI['id'], uI['task_id'], uI['execute_id'], uI['method'], uI['url']
        ))

        # 抓取页面，解析数据
        response = {}
        urlItems = []
        #proxy = {'url':'http://%s' % MIRROR_PROXY} if execute['task_type'] == 'mirror' else {}
        proxy = {}
        requestInfo = spiderRequest(urlInfo['url'], urlInfo['method'], urlInfo['request_headers'], proxy=proxy)

        # 请求错误，直接返回
        if requestInfo['error']:
            mgdb.spiderurl_save(_formatResponse(requestInfo, execute, urlInfo), urlInfo['id'])
            return True

        # 304或其他状态码，直接返回
        if requestInfo['http_code'] != 200:
            mgdb.spiderurl_save(_formatResponse(requestInfo, execute, urlInfo), urlInfo['id'])
            return True

        # 正常请求
        responseHeaders = requestInfo['response_headers']
        contentTypeRaw = responseHeaders['Content-Type'] if 'Content-Type' in responseHeaders.keys() else None
        contentType = parseContentType(contentTypeRaw, default = 'text/html')
        fileType = mime2file(contentType)
        #logger.debug("Content-Type::::::::" + contentTypeRaw + "::::" + contentType)

        #保存响应信息
        fileInfo = download(requestInfo, urlInfo, execute, fileType)
        response = _formatResponse(requestInfo, execute, urlInfo, fileInfo)
        mgdb.spiderurl_save(response, urlInfo['id'])

        #非html页面，直接返回
        if fileType != 'html': return True

        #外部连接，不再进一步分析
        if urlInfo['url_type'] != 'self': return True

        # 如果是单页面镜像，不分析页面
        if execute['task_type'] == 'mirror_one': return True

        #正则解析页面
        urlItems = parse_reg(requestInfo)
        #检测暗链
        if pipingDark:
            result = parse_darklink(requestInfo['url'])
            # logger.info('parse_darklink::::%s::::' % (result))
            darklinks = _formatUrls(result, 1) if result else []
            urlItems = urlItems + darklinks

        '''
        浏览器解析部分
        '''
        #if execute['limit_js']:
        #    results = parse_browser(requestInfo)
        #    if results: urlItems = urlItems + results

        # logger.info('parse_darklink::::%s::::%s' % ('urls_uniq', json.dumps(urlItems)))
        # url去重
        urlItems = _urls_uniq(urlItems)
        # 追加新的URL
        undos = []
        mirrors = []
        queueOut = []
        outlinks = []
        queueSite = []
        # logger.info('parse_darklink::::%s::::' % (urlItems))
        # logger.info('parse_darklink::::%s::::%s' % ('urlItems', json.dumps(urlItems)))
        for row in urlItems:
            url = row['url'].strip()
            if not isUrl(url): continue

            fileExtension = extension(url)

            urlType = _getDomainType(url, execute['domain'])
            # isExists = _checkUrlExists(execute['id'], url, row['method'])
            isExists = _checkUrlExists(execute['id'], url, row['method'], row['invisible'])
            if isExists: continue

            flagOutlink = 0
            item = {}
            item['site_id'] = execute['site_id']
            item['task_id'] = execute['task_id']
            item['app_id'] = execute['app_id']
            item['execute_id'] = execute['id']
            item['task_type'] = execute['task_type']
            item['url'] = url
            item['url_type'] = urlType
            item['file_extension'] = fileExtension
            item['method'] = row['method']
            item['invisible'] = row['invisible']
            item['post'] = json.dumps(row['post'], ensure_ascii=False) if row['post'] else ''

            # 非本站链接或不分析暗链，状态标为5，即不需要抓取

            item['status'] = 5
            if urlType == 'self':
                item['status'] = 0
            else:
                if fileExtension in staticExts:
                    item['status'] = 0
                else:
                    if pipingDark: 
                        flagOutlink = 1
                        item['status'] = 0
            if urlType == 'other': 
                outlinks.append(_formatOutlink(execute, urlInfo['url'], url, row['invisible']))
            item['referer'] = urlInfo['url']
            item['exec_level'] = execute['exec_level']
            item['depth'] = int(urlInfo['depth']) + 1
            item['query'] = row['query']
            item['pattern_path'] = row['pattern_path']
            item['pattern_query'] = row['pattern_query']
            item['create_at'] = now_format()
            item['update_at'] = now_format()
            if flagOutlink:
                queueOut.append(item)
            else:
                queueSite.append(item)

        # logger.info('22parse_darklink::::%s::::%s' % ('queueSite', json.dumps(queueSite)))
        # logger.info('22parse_darklink::::%s::::%s' % ('queueOut', json.dumps(queueOut)))
        if urlItems:
            mgdb.c_insert('parse', _formatParse(execute, urlInfo, urlItems, response['md5_body'], 'regular'))
        if outlinks: mgdb.c_insert_batch('outlink', outlinks)
        stats = Mq.get_stats_batch('spider', execute['id'])
        if queueSite:
            # logger.info('parse_darklink::::::::%s' % (queueSite))
            results = mgdb.c_insert_batch('spiderurl', queueSite)
            for item in results:
                # 状态位非0，不抓取
                if item['status'] != 0: continue
                # 深度超过限制，不抓取
                if item['depth'] > execute['limit_depth']: continue
                # 总数超过限制，不抓取
                if stats['total'] > execute['limit_total']: continue
                # 镜像，不抓取图片
                if execute['task_type'] == 'mirror' and item['file_extension'] in staticExts: continue
                # 单页面监测，不抓取子页面
                if execute['task_type'] in ['monitor_one', 'mirror_one'] and item['file_extension'] not in staticExts: continue
                # 不抓取图片
                if not execute['limit_image'] and item['file_extension'] in staticExts: continue
                item[batchKey] = item['execute_id']
                item[mqidKey] = item['id']

                #数据放入待抓取队列
                undos.append(item)

                #数据放入镜像队列
                if execute['task_type'] == 'mirror': mirrors.append(item)
        if queueOut:
            # logger.info('parse_darklink::::::::%s' % (queueOut))
            results = mgdb.c_insert_batch('spiderurl', queueOut)
            for item in results: 
                item[batchKey] = item['execute_id']
                item[mqidKey] = item['id']
                undos.append(item)
        if undos: Mq.produce(undos, 'spider')
        if mirrors: Mq.produce(mirrors, 'mirror')

    except Exception as e:
        logger.exception(e)
        return False

