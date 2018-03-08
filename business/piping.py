'''
数据处理
'''
# -*- coding: utf-8 -*-

import time
import json
from os.path import basename
from utils.acism import Acism
import business.task as bTask
from utils.security import md5
from db import mongodb as mgdb
from config.config import DFS_URL
import business.notify as bNotify
from urllib.parse import urlparse
from common import db, mongoSpider
from urllib.request import urlopen
from utils.file import qiniu_upload
from business import snapshot as bSnapshot
from utils.logger import loggerPiping as logger
from utils.time import getTime, formatTimestamp
from utils.url import getDomainMain, getDomainNoPort


def _snapshot_save(eid, type, url, filename, words = []):
    '''保存快到到队列'''
    params = {
        'app_key': 'spider',
        'batch': 'spider_%s' % eid,
        'type': type,
        'url': url,
        'filename': filename,
        'words': words,
        'proxy': '',
        'notify_url': '',
        'error':'',
        'status':0,
    }
    return bSnapshot.save(params)


def result_save(execute, piping, results):
    #数据入库
    pipingResult = {}
    pipingResult['app_id'] = execute['app_id']
    pipingResult['site_id'] = execute['site_id']
    pipingResult['task_id'] = execute['task_id']
    pipingResult['execute_id'] = execute['id']
    pipingResult['piping_id'] = piping['id']
    pipingResult['type'] = piping['type']
    '''
    处理的结果以json字符串的形式保存
    包含敏感词,关键字,指纹,错误状态码,暗链
    '''
    pipingResult['result'] = json.dumps(results, ensure_ascii=False)
    pipingResult['status'] = 1
    pipingResult['audit_status'] = 0
    resultOld = db.fetchone('select id from task_piping_result where execute_id=:eid and piping_id=:pid', {'eid': execute['id'], 'pid': piping['id']})

    if resultOld:
        resultId = resultOld['id']
        db.updatebyid('task_piping_result', pipingResult, resultId)
    else:
        resultId = db.insert('task_piping_result', pipingResult)
    bNotify.save(execute['id'], 'piping_%s' % piping['type'], {'piping_status':'ok'})
    return resultId


def piping_filterword(executeid):
    '''敏感词过滤'''
    execute = db.fetchone('select * from task_execute where id=:id', {'id': executeid})
    piping = db.fetchone('select * from task_piping where task_id=:tid and type=:type and status=1', {'tid': execute['task_id'], 'type':'filterword'})
    if not piping: return True

    #系统词库
    systemWords = ''
    if piping['filterword_type'] in ['system','mixed']:
        pipingExtend = db.fetchall('select name from sys_filterword')
        systemWords = [row['name'] for row in pipingExtend] if pipingExtend else []
    # 自有词库
    ownWords = ''
    if piping['filterword_type'] in ['own', 'mixed']:
        pipingExtend = db.fetchone('select data from piping_extend where id=:id and status=1', {'id': piping['extend_id']})
        ownWords = pipingExtend['data'] if pipingExtend else ''
    words = []
    if piping['filterword_type'] == 'system':
        words = systemWords
    if piping['filterword_type'] == 'own':
        words = ownWords.split("\n")
    if piping['filterword_type'] == 'mixed':
        words = systemWords  + ownWords.split('\n')
    words = list(set(words))

    # print(words,type(words))
    if '' in words:
        words.remove('')
    if not words:
        return True

    acism = Acism(words)

    results = []
    rows = mgdb.spiderurl_getall_executeid_status(executeid, 2, ['id','url', 'file_path', 'file_extension','url_type'])
    for row in rows:
        if row['url_type'] != 'self':continue
        if not (row['file_extension'] == 'html' or row['file_extension'] == ''): continue
        body = urlopen("%s/download?filekey=%s" % (DFS_URL, row['file_path'])).read().decode('utf-8','ignore')
        # body = open('demo.html', 'r').read()
        result = acism.scan(body)
        if result:
            filename = "snap_code_filterword_%s.png" % row['id']
            snapshots = _snapshot_save(executeid, 'code', row['file_path'], filename, words=result.keys())
            pipingResult = {"id":row['id'], "url":row['url'], "matches":result, 'snapshot':"\n".join(snapshots)}
            snapshot_insert(executeid, piping, row, pipingResult, snapshots)
            results.append(pipingResult)
    if results:
        return result_save(execute, piping, results)
    else:
        return True


def piping_keyword(executeid):
    '''关键字过滤'''
    execute = db.fetchone('select * from task_execute where id=:id', {'id': executeid})
    piping = db.fetchone('select * from task_piping where task_id=:tid and type=:type and status=1', {'tid': execute['task_id'], 'type': 'keyword'})
    if not piping or not piping['extend_id']: return True
    #自有词库
    pipingExtend = db.fetchone('select data from piping_extend where id=:id and status=1', {'id': piping['extend_id']})
    if not pipingExtend: return True
    if not pipingExtend['data']: return True
    rows = json.loads(pipingExtend['data'])
    if not rows: return True
    kws = {it['url']:it['words'] for it in rows}
    results = []
    mgRows = mgdb.spiderurl_getall_executeid_status(executeid, 2, ['id', 'url', 'file_path', 'file_extension','url_type'])
    for row in mgRows:
        # 非本网站的链接不给结果
        if row['url_type'] != 'self': continue
        if row['url'] not in kws.keys(): continue
        if not (row['file_extension'] == 'html' or row['file_extension'] == ''): continue
        url = row['url']
        body = urlopen("%s/download?filekey=%s" % (DFS_URL, row['file_path'])).read().decode('utf-8','ignore')
        result = Acism(kws[url]).scan(body)
        # set(kws[url])中有的而result.keys()中没有的
        wordsNoExists = list(set(kws[url]).difference(set(result.keys())))
        if wordsNoExists:
            filename = "snap_code_keyword_%s.png" % row['id']
            snapshots = _snapshot_save(executeid, 'code', row['file_path'], filename, words=wordsNoExists)
            pipingResult = {"id":row['id'], "url":row['url'], "noWords": wordsNoExists, "words": kws[url], 'snapshot':"\n".join(snapshots)}
            snapshot_insert(executeid, piping, row, pipingResult, snapshots)
            results.append(pipingResult)
    return result_save(execute, piping, results) if results else True


def piping_errorHttpCode(executeid):
    '''异常状态码'''
    execute = db.fetchone('select * from task_execute where id=:id', {'id': executeid})
    piping = db.fetchone('select * from task_piping where task_id=:tid and type=:type and status=1', {'tid': execute['task_id'], 'type': 'error_http_code'})
    if not piping: return True
    if piping['extend_id']:
        extend = db.fetchone('select data from piping_extend where id=:id and status=1', {'id': piping['extend_id']})
    else:
        extend = db.fetchone('select data from piping_extend where task_id=0 and piping_type=:type and status=1', {'type': 'error_http_code'})
    if not extend:
        return True
    httpCodes = extend['data'].split("\n")
    results = []
    mgRows = mgdb.spiderurl_getall_executeid_status(executeid, 2, ['id','url','http_code','url_type'])
    for row in mgRows:
        if row['url_type'] != 'self': continue
        if not row['http_code']: continue
        if execute['domain'] != getDomainNoPort(row['url']): continue
        if str(row['http_code']) in httpCodes: results.append(row)
    mgRows = mgdb.spiderurl_getall_executeid_status(executeid, 3, ['id','url','http_code','url_type'])
    for row in mgRows:
        if row['url_type'] != 'self': continue
        if not row['http_code']: continue
        if execute['domain'] != getDomainNoPort(row['url']): continue
        if str(row['http_code']) in httpCodes: results.append(row)
    return result_save(execute, piping, results) if results else True


def piping_fingerprint(executeid):
    '''指纹检测'''
    execute = db.fetchone('select * from task_execute where id=:id', {'id': executeid})
    if not execute: return True
    piping = db.fetchone('select * from task_piping where task_id=:tid and type=:type and status=1', {'tid':execute['task_id'], 'type':'fingerprint'})
    if not piping: return True
    executeOld = db.fetchone('select * from task_execute where task_id=:tid and id<:eid order by id desc', {'tid': execute['task_id'], 'eid':executeid})
    if not executeOld: return True
    exts = ['js','css','jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
    # 比对指纹
    executeOldId = executeOld['id']
    mgRows = mgdb.spiderurl_getall_executeid_status(executeid, 2, ['id', 'url','md5_url', 'md5_body', 'status', 'file_extension'])
    rowsDict = {}
    for row in mgRows:
        if row['file_extension'] not in exts: continue
        rowsDict[row['md5_url']] = row
    mgRows = mgdb.spiderurl_getall_executeid_status(executeOldId, 2, ['id', 'url','md5_url', 'md5_body', 'status', 'file_extension'])
    rowsDictOld = {}
    for row in mgRows:
        if row['file_extension'] not in exts: continue
        rowsDictOld[row['md5_url']] = row
    results = []
    for md5Url, row in rowsDict.items():
        if md5Url in rowsDictOld.keys():
            if row['md5_body'] != rowsDictOld[md5Url]['md5_body']:
                filename = "snap_view_%s.png" % row['id']
                snapshot = _snapshot_save(executeid, 'view', row['url'], filename)[0]
                pipingResult = {
                    'url':row['url'],
                    'md5_url':md5Url,
                    'md5_body_new':row['md5_body'],
                    'md5_body_old':rowsDictOld[md5Url]['md5_body'],
                    'snapshot':snapshot
                }
                snapshot_insert(executeid, piping, row, pipingResult, snapshot)
                results.append(pipingResult)
    if results:
        return result_save(execute, piping, results)
    else:
        return True


def piping_darklink(executeid):

    execute = mgdb.execute_getbyid(executeid)
    if not execute: return False
    piping = db.fetchone('select * from task_piping where task_id=:tid and type=:type and status=1', {'tid': execute['task_id'], 'type':'darklink'})
    if not piping: return True
    pipingExtend = db.fetchall('select name from sys_filterword')
    words = [row['name'] for row in pipingExtend] if pipingExtend else []
    # if not words: return True
    acism = Acism(words)
    #查询出系统黑白名单表里面的url
    rows = db.fetchall('select domain from dk_white_list')
    whites = [row['domain'] for row in rows] if rows else []
    rows = db.fetchall('select domain from dk_black_list')
    blacks = [row['domain'] for row in rows] if rows else []
    #拼接白名单和黑名单链接，并去重
    whites_glb = list(set(whites))
    blacks_glb = list(set(blacks))
    #查询出个人黑白名单表里面的url
    pipingExtend = db.fetchone('select data from piping_extend where id=:id and status=1', {'id': piping['extend_id']})
    whites = eval(pipingExtend['data'])['white_list']
    blacks = eval(pipingExtend['data'])['black_list']
    whites_psl = list(set(whites))
    blacks_psl = list(set(blacks))
    mgRows = mgdb.spiderurl_getall_executeid_status(executeid, 2, ['id', 'url', 'md5_url', 'md5_body', 'url_type','file_extension','file_path', 'invisible','referer'])
    results = []
    for row in mgRows:
        # 匹配个人黑白名单里面的url
        if row['url'] in whites_psl:continue
        if row['url'] in blacks_psl:
            words = [params['darklink'] for params in results] if results else []
            if row['url'] not in words:
                filename = 'snap_code_darklink_%s.png' % row['id']
                snapshots = _snapshot_save(executeid,'code',row['file_path'], filename, words=[row['url']])
                result = {'id':row['id'],'referer':row['referer'],'darklink':row['url'],'level':'absolute','snapshot':"\n".join(snapshots)}
                snapshot_insert(executeid, piping, row, result, snapshots)
                results.append(result)
                continue
        # 静态文件不是暗链
        if row['url_type'] != 'other':continue
        if row['file_extension'] not in ['', 'html']:continue
        # 匹配系统黑白名单(判定结果疑似度百分百 absolute)
        if row['url'] in whites_glb:continue
        if row['url'] in blacks_glb:
            words = [params['darklink'] for params in results] if results else []
            if row['url'] not in words:
                filename = 'snap_code_darklink_%s.png' % row['id']
                snapshots = _snapshot_save(executeid,'code',row['file_path'], filename, words=[row['url']])
                result = {'id':row['id'],'referer':row['referer'],'darklink':row['url'],'level':'absolute','snapshot':"\n".join(snapshots)}
                snapshot_insert(executeid, piping, row, result, snapshots)
                results.append(result)
                continue
        # 敏感词检测(判定结果疑似度高 high)
        # if words:
        body = urlopen("%s/download?filekey=%s" % (DFS_URL, row['file_path'])).read().decode('utf-8','ignore')
        resultWord = acism.scan(body)
        if resultWord:
            words = [params['darklink'] for params in results] if results else []
            if row['url'] not in words:
                filename = 'snap_code_darklink_%s.png' % row['id']
                snapshots = _snapshot_save(executeid, 'code', row['file_path'], filename, words=[row['url']])
                result = {'id': row['id'], 'referer': row['referer'], 'darklink': row['url'], 'level': 'high','snapshot': "\n".join(snapshots)}
                snapshot_insert(executeid, piping, row, result, snapshots)
                results.append(result)
                finddata = {'domain':execute['domain'], 'md5_body':row['md5_body']}
                setdata = {'$set':{'filterwords':json.dumps(resultWord, ensure_ascii=False)}}
                mongoSpider['outlink'].find_and_modify(finddata, setdata)
                continue
        # 检测是否可见(判定结果疑似度低　low)
        if row['invisible']:
            words = [params['darklink'] for params in results] if results else []
            if row['url'] not in words:
                filename = 'snap_code_darklink_%s.png' % row['id']
                snapshots = _snapshot_save(executeid,'code',row['file_path'], filename, words=[row['url']])
                result = {'id':row['id'],'referer':row['referer'],'darklink':row['url'],'level':'low','snapshot':"\n".join(snapshots)}
                snapshot_insert(executeid, piping, row, result, snapshots)
                results.append(result)
                continue
        # # 检测是否重复(超过引用阈值疑似度高 high／没有超过引用阈值疑似度中　medium)
        # if row['file_extension']:
        #     body = urlparse()
        # # 检测引用次数    @未严格定义，待定
        # match = {'$match':{'md5_url':row['md5_url']}}
        # group = {'$group':{'_id':'$domain', 'count':{'$sum':1}}}
        # results = [i for i in mongoSpider['outlink'].aggregate([match, group])]
        # if len(results) > 500:
    if results:return result_save(execute, piping, results) if results else True


def snapshot_insert(executeid, piping, urlRow, result, snapshot):
    '''插入快照'''
    pipingSnapshot = {}
    pipingSnapshot['app_id'] = piping['app_id']
    pipingSnapshot['site_id'] = piping['site_id']
    pipingSnapshot['task_id'] = piping['task_id']
    pipingSnapshot['execute_id'] = executeid
    pipingSnapshot['piping_id'] = piping['id']
    pipingSnapshot['type'] = piping['type']
    pipingSnapshot['url_id'] = urlRow['id']
    pipingSnapshot['url'] = urlRow['url']
    pipingSnapshot['snapshot'] = snapshot if type(snapshot) == str else "\n".join(snapshot)
    pipingSnapshot['result'] = json.dumps(result, ensure_ascii=False)
    pipingSnapshot['status'] = 1
    pipingSnapshot['audit_status'] = 0
    snapshotId = db.insert('task_piping_snapshot', pipingSnapshot)
    return snapshotId


def piping_all(executeid):
    '''执行任务处理'''
    reData = {'status':0, 'msg':'', 'dopiping_executeid':executeid}
    row =  mgdb.execute_getbyid(executeid)
    if not row:
        return {'status':0, 'msg':'task_execute[%s] is not exists' % executeid, 'dopiping_executeid':executeid}
    types = db.fetchall("select type from task_piping where task_id=:id", {'id':row['task_id']})
    if not types:
        db.updatebyid('task_execute', {'status':'4'}, row['id'])
        return {'status':1, 'msg':'piping ok', 'dopiping_executeid':executeid}
    for row1 in types:
        pipingType = row1['type']
        if pipingType == 'filterword':
            piping_filterword(row['id'])
        if pipingType == 'keyword':
            piping_keyword(row['id'])
        if pipingType == 'error_http_code':
            piping_errorHttpCode(row['id'])
        if pipingType == 'fingerprint':
            result = piping_fingerprint(row['id'])
        if pipingType == 'darklink':
            result = piping_darklink(row['id'])
    return {'status':1, 'msg':'piping ok', 'dopiping_executeid':executeid}


def piping_save(rows=None,taskid=None):
    task = db.fetchone('select * from task where id=:id', {'id':taskid})
    for row in rows:
        taskPiping = db.fetchone('select * from task_piping where task_id=:tid and type=:type', {'tid':taskid, 'type':row['type']})
        extendId = 0
        pipingExtendOld = None
        if taskPiping:
            extendId = taskPiping['extend_id']
            pipingExtendOld = db.fetchone('select * from piping_extend where id=:id', {'id': extendId})
        # wordId 值为0，则取系统默认词库
        if row['type'] == 'darklink':
            pipingExtend={}
            pipingExtend['app_id'] = task['app_id']
            pipingExtend['site_id'] = task['site_id']
            pipingExtend['task_id'] = taskid
            pipingExtend['piping_type'] = row['type']
            white_list = json.dumps(row['white_list'], ensure_ascii=False) if row['white_list'] else '[]'
            white_list = {'white_list':eval(white_list)}
            black_list = json.dumps(row['black_list'], ensure_ascii=False) if row['black_list'] else '[]'
            black_list = {'black_list':eval(black_list)}
            pipingExtend['data'] = json.dumps(dict(white_list, **black_list))
            pipingExtend['status'] = 1
            if pipingExtendOld:
                db.updatebyid('piping_extend', pipingExtend, extendId)
            else:
                extendId = db.insert('piping_extend', pipingExtend)

        if row['type'] == 'filterword' and 'filterwords' in row.keys() and 'filterword_operate' in row.keys():
            words = []
            wordsOld = []
            wordsNew = row['filterwords'].replace(' ', '').split("\n")
            if pipingExtendOld:
                extendId = pipingExtendOld['id']
                wordsOld = pipingExtendOld['data'].split("\n") if pipingExtendOld['data'] else []
            # 覆盖自有词库
            if row['filterword_operate'] == 'own':
                words = wordsNew
            # 加词
            if row['filterword_operate'] == 'plus':
                words.extend(wordsNew)
                if wordsOld: words.extend(wordsOld)
            # 减词
            if row['filterword_operate'] == 'reduce' and wordsOld:
                wordsCommon = list(set(wordsNew) & set(wordsOld))
                for word in wordsCommon: wordsOld.remove(word)
                words = wordsOld
            if '' in words: words.remove('')
            words = list(set(words))
            pipingExtend = {}
            pipingExtend['app_id'] = task['app_id']
            pipingExtend['site_id'] = task['site_id']
            pipingExtend['task_id'] = taskid
            pipingExtend['piping_type'] = row['type']
            pipingExtend['data'] = "\n".join(words)
            pipingExtend['status'] = 1
            if pipingExtendOld:
                db.updatebyid('piping_extend', pipingExtend, extendId)
            else:
                extendId = db.insert('piping_extend', pipingExtend)
        # 处理关键字
        if row['type'] == 'keyword' and 'keywords' in row.keys():
            pipingExtend = {}
            pipingExtend['app_id'] = task['app_id']
            pipingExtend['site_id'] = task['site_id']
            pipingExtend['task_id'] = taskid
            pipingExtend['piping_type'] = row['type']
            pipingExtend['data'] = json.dumps(row['keywords'], ensure_ascii=False) if row['keywords'] else ''
            pipingExtend['status'] = 1
            if pipingExtendOld:
                db.updatebyid('piping_extend', pipingExtend, extendId)
            else:
                extendId = db.insert('piping_extend', pipingExtend)
        # 处理错误状态吗
        if row['type'] == 'error_http_code' and 'http_codes' in row.keys():
            pipingExtend = {}
            pipingExtend['app_id'] = task['app_id']
            pipingExtend['site_id'] = task['site_id']
            pipingExtend['task_id'] = taskid
            pipingExtend['piping_type'] = row['type']
            pipingExtend['data'] = row['http_codes']
            pipingExtend['status'] = 1
            if pipingExtendOld:
                db.updatebyid('piping_extend', pipingExtend, extendId)
            else:
                extendId = db.insert('piping_extend', pipingExtend)
        wordType = row['filterword_type'] if 'filterword_type' in row.keys() else ''
        status = row['status'] if 'status' in row.keys() else 1
        piping = {}
        piping['status'] = status
        piping['extend_id'] = extendId
        piping['filterword_type'] = wordType
        if taskPiping:
            pipingId = db.updatebyid('task_piping', piping, taskPiping['id'])
        else:
            piping['app_id'] = task['app_id']
            piping['site_id'] = task['site_id']
            piping['task_id'] = taskid
            piping['type'] = row['type']
            pipingId = db.insert('task_piping', piping)
    return True


def piping_getall_taskid(taskid = None):
    ''' 获取数据处理通道'''
    pipings = {}
    taskPipings = db.fetchall('select * from task_piping where task_id=:id', {'id': taskid})
    for piping in taskPipings:
        piping['create_at'] = formatTimestamp(piping['create_at'])
        piping['update_at'] = formatTimestamp(piping['update_at'])
        pipingType = piping['type']
        if pipingType in ['filterword', 'keyword']:
            pipingExtend = db.fetchone('select * from piping_extend where id=:id', {'id': piping['extend_id']})
            piping['words'] = pipingExtend['data']
        pipings[pipingType] = piping
    return pipings


def result_getall_executeid(executeid = None):
    ''' 获取数据处理结果'''
    pipingResults = db.fetchall('select task_id,execute_id,type,result,create_at from task_piping_result where execute_id=:eid', {'eid':executeid})
    for row in pipingResults:
        row['create_at'] = formatTimestamp(row['create_at'])
        row['result'] = json.loads(row['result'])
    return pipingResults


