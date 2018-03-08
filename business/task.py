# -*- coding: utf-8 -*-
from __future__ import absolute_import
import json
import pytz
from copy import deepcopy
import db.mongodb as mgdb
from utils import mq as Mq
from datetime import datetime
from utils.logger import logger
import business.mirror as bMirror
import business.notify as bNotify
from urllib.parse import urlparse
from common import db, redis, mongoMq, mongoSpider
from utils.url import getDomainMain, getDomainNoPort
from utils.time import getTime, formatTimestamp, now_format

mqidKey = 'mq_id'
batchKey = 'mq_batch'
def _str2int(raw):
    '''字符串转整型'''
    if type(raw) == list:
        return [int(i) if type(i) == str else i for i in raw]
    else:
        return raw if type(raw) == int else int(raw)

def _startUrls2Json(startUrls):
    rows = startUrls.split("\n")
    urls = [url.strip() for url in rows]
    return json.dumps(urls, ensure_ascii=False)

def _startUrls2Raw(startUrls):
    return "\n".join(json.loads(startUrls))

def _getSiteid(url):
    '''获取域名ID'''
    domain = urlparse(url)[1]
    if ':' in domain: domain = domain.split(':')[0]

    domainMain = getDomainMain(domain)
    siteDict = db.fetchone('select * from site where domain=:domain', {'domain': domainMain})
    siteid = siteDict['id'] if siteDict else db.insert('site', {'domain':domainMain})

    if domain != domainMain:
        domainDict = db.fetchone('select * from domain where subdomain=:domain', {'domain': domain})
        if not domainDict: db.insert('domain', {'site_id':siteid, 'subdomain':domain})

    return siteid

def task_save(params = None):
    if not params['id'] and not params['start_urls']: return False
    if params['start_urls']:
        startUrls = params['start_urls'].split("\n")
        params['start_urls'] = json.dumps(startUrls, ensure_ascii=False)
    else:
        params['start_urls'] = ''

    #默认值
    defaultKeys = {
        'app_id':0,
        'type':'spider',
        'start_urls':'',
        'exec_level': 0,
        'limit_depth':2,
        'limit_total': 1000,
        'limit_time': 0, 
        'limit_subdomain': 0, 
        'limit_image':0,
        'limit_js':0,
        'url_unique_mode':'url-query',
        'notify_url':'',
        'exec_level':0,
        'source_ip':'',
        'exclude_urls':'',
        'proxies':'',
        'crontab':'',
        'status': 0,
    }

    #处理定时任务
    rundate = None
    if 'execute_at' in params.keys() and params['execute_at']:
        rundate = datetime.strptime(params['execute_at'], '%Y-%m-%d %H:%M:%S')

    if 'execute_delay' in params.keys() and params['execute_delay']:
        rundateStr = getTime('%Y-%m-%d %H:%M:%S', getTime() + params['execute_delay'])
        rundate = datetime.strptime(rundateStr, '%Y-%m-%d %H:%M:%S')

    #保存数据
    taskdata = {}
    keys = defaultKeys.keys()
    if params['id']:
        taskid = params['id']
        for key in keys:
            if key in params.keys() and params[key]:
                taskdata[key] = params[key]
        result = db.updatebyid('task', taskdata, taskid)
    else:
        taskdata['site_id'] = _getSiteid(startUrls[0])
        for key in keys:
            if key in params.keys() and params[key]:
                taskdata[key] = params[key]
            else:
                taskdata[key] = defaultKeys[key]
        taskid = db.insert('task', taskdata)

    #定时任务
    func_name = task_start
    jobid = 'task_%s' % taskid
    if rundate:
        job = db.getbyid('scheduler', jobid)
        if job: 
            db.updatebyid('scheduler', {'run_date':rundate}, jobid)
        else:
            scheduler = {
                'id': jobid,
                'name': jobid,
                'func': 'business.task:task_start',
                'args': '[' + str(taskid) + ']',
                'trigger_type': 'date',
                'run_date': rundate,
                'coalesce': 0,
                'next_run_time': rundate,
                'max_instances': 3,
                'executor': 'default',
                'misfire_grace_time ': 1,
            }
            db.insert(scheduler)
        return taskid

    #非计划任务
    task = db.fetchone("select * from task where id=:id", {'id':taskid})
    if not task['crontab']: 
        task_start(taskid)
        return taskid

    #删除计划任务
    if taskdata['status'] < 1 and taskdata['crontab']:
        db.exec('delete from scheduler where id=:id', {'id':jobid})
        return taskid

    #添加或修改计划任务
    job = db.getbyid('scheduler', jobid)
    cs = params['crontab'].split(' ')
    if job:
        crontab = '0 '+task['crontab']+' * *,SMHdmwWY'
        db.updatebyid('scheduler', {'crontab': crontab}, jobid)
    else:
        tz = pytz.timezone('Asia/Shanghai')
        scheduler = {
            'id': jobid,
            'name': jobid,
            'func': 'business.task:task_start',
            'args': '[' + str(taskid) + ']',
            'trigger_type': 'cron',
            'crontab': '0 ' + task['crontab'] + ' * *,SMHdmwWY',
            'coalesce': 0,
            'next_run_time': datetime.now(tz=tz).strftime('%Y-%m-%d %H:%M:%S%z'),
            'max_instances': 3,
            'executor': 'default',
            'misfire_grace_time ': 1,
        }
        db.insert('scheduler', scheduler)

    return taskid

def task_update_ids(setting=None, ids = []):
    '''删除任务'''
    if not ids: return True
    db.updatebyids('task', setting, ids)
    return True 

def task_getnew_id(taskid):
    execute = db.fetchone('select * from task_execute where task_id=:task_id order by id desc limit 1', {'task_id':taskid})
    execute['start_at'] = formatTimestamp(execute['start_at']) if execute['start_at'] else ''
    execute['end_at'] = formatTimestamp(execute['end_at']) if execute['end_at'] else ''
    execute['create_at'] = formatTimestamp(execute['create_at'])
    execute['update_at'] = formatTimestamp(execute['update_at'])
    return execute

def task_get_id(id):
    task = db.fetchone('select * from task where id=:id', {'id':id})
    if not task: return False
    task['start_urls'] = _startUrls2Raw(task['start_urls'])
    task['create_at'] = formatTimestamp(task['create_at'])
    task['update_at'] = formatTimestamp(task['update_at'])
    return task

def task_delete_id(taskid):
    result = db.updatebyid('task', {'status':-1}, taskid)

def task_delete_ids(ids = None):
    '''删除任务'''
    if not ids: return True
    for taskid in ids: task_delete_id(taskid)
    return True

def task_getall(page = 1, pagesize = 20):
    page = _str2int(page) if page else 1
    pagesize = _str2int(pagesize) if pagesize else 20
    if page < 1: page = 1
    if pagesize < 1: pagesize = 20
    offset = (page - 1) * pagesize

    rows = db.fetchall('select * from task order by id desc limit :limit offset :offset;', {'limit':pagesize, 'offset':offset})
    if not rows: return False
    tasks = []
    for row in rows:
        row['create_at'] = formatTimestamp(row['create_at'])
        row['update_at'] = formatTimestamp(row['update_at'])
        tasks.append(row)
    return tasks

def task_start(taskid):
    try:
        task = db.fetchone('select * from task where id=:id', {'id': taskid})
        if not task: return False
        startUrls = json.loads(task['start_urls'])
        executedata = {
            'site_id':task['site_id'],
            'task_id':task['id'],
            'app_id':task['app_id'],
            'task_type':task['type'],
            'start_urls':task['start_urls'],
            'domain':getDomainNoPort(startUrls[0]),
            'exec_level':task['exec_level'],
            'limit_depth':task['limit_depth'],
            'limit_total':task['limit_total'],
            'limit_time':task['limit_time'],
            'limit_subdomain':task['limit_subdomain'],
            'limit_image':task['limit_image'],
            'limit_js':task['limit_js'],
            'limit_jsevent':task['limit_jsevent'],
            'exclude_urls':task['exclude_urls'],
            'url_unique_mode':task['url_unique_mode'],
            'notify_url':task['notify_url'],
            'source_ip':task['source_ip'],
            'proxies':task['proxies'],
            'status':0,
        }
        executeid = db.insert('task_execute', executedata)
        return executeid
    except Exception as e:
        logger.exception(e)
        return False

def execute_init(eid):
    '''本函数允许重复执行'''
    execute = db.getbyid('task_execute', eid)
    if not execute: return False
    execute['create_at'] = formatTimestamp(execute['create_at']) if execute['create_at'] else ''
    execute['update_at'] = formatTimestamp(execute['update_at']) if execute['update_at'] else ''
    execute['start_at'] = formatTimestamp(execute['start_at']) if execute['start_at'] else ''
    execute['end_at'] = formatTimestamp(execute['end_at']) if execute['end_at'] else ''
    execute['status'] = 101

    mgExecute = mgdb.execute_getbyid(eid)
    if not mgExecute:
        execute_spider = deepcopy(execute)
        mgdb.c_insert('execute', execute_spider, autoid=False)

    startUrls = json.loads(execute['start_urls'])
    startUrlsLen = len(startUrls)
    urlCount = mongoSpider['spiderurl'].find({'execute_id':eid},{'_id':0}).count()
    if startUrlsLen > urlCount:
        urlRows = []
        for url in startUrls:
            urldata = {
                'site_id': execute['site_id'],
                'task_id': execute['task_id'],
                'app_id': execute['app_id'],
                'task_type': execute['task_type'],
                'execute_id': eid,
                'exec_level': execute['exec_level'],
                'url': url,
                'url_type': 'self',
                'method': 'get',
                'status': 0,
                'create_at': now_format(),
                'update_at': now_format(),
            }
            urlRows.append(urldata)
        mgdb.c_insert_batch('spiderurl', urlRows)
    undos = [i for i in mongoSpider['spiderurl'].find({'execute_id':eid},{'_id':0})]
    undos_spider = []
    undos_mirror = []
    for undo in undos:
        undo[mqidKey] = undo['id']
        undo[batchKey] = undo['execute_id']
        undos_spider.append(undo)
        undos_mirror.append(undo)

    pre = 'mq_spider_'
    stages = ['undo', 'ready', 'doing', 'done']
    stats = {stage:mongoMq[pre+stage].find({batchKey: eid}).count() for stage in stages}
    total = stats['undo'] + stats['ready'] + stats['doing'] + stats['done']
    if startUrlsLen > total: 
        #添加spider队列
        Mq.produce(undos_spider, 'spider')

        #添加mirror队列
        if execute['task_type'] == 'mirror': Mq.produce(undos_mirror, 'mirror')

    if not mgExecute: db.updatebyid('task_execute', {'status':101}, eid)
    return True

###################################### execute #################################################################

def execute_get_id(executeid):
    '''根据执行ID获取执行信息'''
    execute = db.fetchone('select * from task_execute where id=:id', {'id':executeid})
    if not execute: return False
    execute['start_at'] = formatTimestamp(execute['start_at']) if execute['start_at'] else ''
    execute['end_at'] = formatTimestamp(execute['end_at']) if execute['end_at'] else ''
    execute['create_at'] = formatTimestamp(execute['create_at'])
    execute['update_at'] = formatTimestamp(execute['update_at'])
    return execute

def execute_getnew_taskid(taskid):
    '''根据任务ID获取最新的执行信息'''
    execute = db.fetchone('select * from task_execute where task_id=:id order by id desc', {'id':taskid})
    if not execute: return False
    execute['start_at'] = formatTimestamp(execute['start_at'])
    execute['end_at'] = formatTimestamp(execute['end_at'])
    execute['create_at'] = formatTimestamp(execute['create_at'])
    execute['update_at'] = formatTimestamp(execute['update_at'])
    return execute

def execute_getall_taskid(taskid):
    rows = db.fetchall('select * from task_execute where task_id=:task_id order by id desc', {'task_id':taskid})
    if not rows: return False
    executes = []
    for execute in rows:
        execute['start_at'] = formatTimestamp(execute['start_at']) if execute['start_at'] else ''
        execute['end_at'] = formatTimestamp(execute['end_at']) if execute['end_at'] else ''
        execute['create_at'] = formatTimestamp(execute['create_at'])
        execute['update_at'] = formatTimestamp(execute['update_at'])
        executes.append(execute)
    return executes

def execute_update_ids(setting, executeids):
    '''同时更新数据表及mongodb'''
    db.updatebyids('task_execute', setting, executeids)
    mgdb.execute_update_ids(setting, executeids)

def execute_update_ids_status(setting, executeids, status):
    '''同时更新数据表及mongodb'''
    db.updatebyids_status('task_execute', setting, executeids, status)
    mgdb.execute_update_ids_status(setting, executeids, status)

def execute_finish():
    '''蜘蛛是否结束'''
    finishIds = []
    #查询所有未执行中的批次，进行检查
    for row in mongoMq['stats_batch_run'].find({'is_end':0},{"_id":0, 'mqkey':1, 'batch':1}):
        mqkey = row['mqkey']
        batch = row['batch']
        stats = mongoMq['stats_batch_stage'].find_one({"mqkey": mqkey, 'batch': batch}, {"_id":0})
        if not stats:
            logger.error("no stats_batch_stage::::%s::::%s" % (mqkey, batch))
            continue
        if (not stats['undo'] and not stats['ready'] and not stats['doing'] 
            and stats['done'] and stats['done'] == stats['total']):
            endAt = getTime('%Y-%m-%d %H:%M:%S')
            mongoMq['stats_batch_stage'].update({"mqkey": mqkey, 'batch': batch}, {"$set":{'end':1}})
            mongoMq['stats_batch_run'].update({"mqkey": mqkey, 'batch': batch}, {"$set":{'is_end':1, 'end_at': endAt}})
            finishIds.append(batch)
            #抓取
            if mqkey == 'spider':
                spiderResult = {'ok':0, 'failed':0, 'error':[]}
                execute = mongoSpider['execute'].find_one({'id':batch}, {'_id':0})
                limit = len(json.loads(execute['start_urls']))
                for row in mongoSpider['spiderurl'].find({'execute_id':batch}, {'_id':0}).sort([("id", 1)]).limit(limit):
                    if row['error']:
                        spiderResult['failed'] = spiderResult['failed'] + 1
                        spiderResult['error'].append(row['error'])
                    else:
                        spiderResult['ok'] = spiderResult['ok'] + 1
                #如果有超过一半页面抓取失败，则抓取失败
                if spiderResult['failed'] > limit/2:
                    result = db.updatebyid('task_execute', {'status': 3, 'end_at':endAt, 'error':"\n".join(spiderResult['error'])}, batch)
                    mgdb.execute_save({'status': 2, 'end_at':endAt, 'error':"\n".join(spiderResult['error']), "id": batch})
                    bNotify.save(batch, eventType = 'spider_failed')
                else:
                    result = db.updatebyid('task_execute', {'status': 2, 'end_at':endAt}, batch)
                    mgdb.execute_save({'status': 2, 'end_at':endAt, "id": batch})
                    bNotify.save(batch, eventType = 'spider_ok')
                    mqExecute = deepcopy(execute)
                    mqExecute[mqidKey] = mqExecute['id']
                    mqExecute[batchKey] = mqExecute['id']
                    Mq.produce([mqExecute], 'piping')

            if mqkey == 'mirror':
                result = db.updatebyid('task_execute', {'status': 4}, batch)
                mgdb.execute_save({'status': 4, "id":batch})
                bNotify.save(batch, eventType = 'mirror_ok')

            if mqkey == 'piping':
                result = db.updatebyid('task_execute', {'status': 4}, batch)
                mgdb.execute_save({'status': 4, "id": batch})
                bNotify.save(batch, 'piping_all', {'piping_status':'ok'})
    return finishIds

