from __future__ import absolute_import
import json
import db.mongodb as mgdb
from common import db, redis
from utils.time import getTime, formatTimestamp, now_format
from utils.security import md5
from urllib.request import Request, urlopen
from utils.logger import logger
from utils import mq as Mq

mqidKey = 'mq_id'
batchKey = 'mq_batch'

#获取下一个URL
def getall():
    sql = "select * from task_notify order by id desc"
    rows = db.fetchall(sql)
    notifies = []
    for row in rows:
        row['create_at'] = formatTimestamp(row['create_at'])
        row['update_at'] = formatTimestamp(row['update_at'])
        notifies.append(row)
    return notifies

def send(notifyid = None):
    reData = {'status':0, 'msg':'', 'donotify_notifyid':notifyid}
    row =  db.fetchone("select * from task_notify where id=:id", {'id': notifyid})
    if not row:
        return {'status':0, 'msg':'notify[%s] is not exists' % notifyid, 'donotify_notifyid':notifyid}

    try:
        data = {
            'id': row['id'],
            'app_id': row['app_id'],
            'task_id': row['task_id'],
            'site_id': row['site_id'],
            'execute_id': row['execute_id'],
            'task_type': row['task_type'],
        }
        requestData = json.loads(row['request_data']) if row['request_data'] else {}
        data = dict(data, **requestData)
        data = json.dumps(data, ensure_ascii=False)
        request = Request(row['notify_url'], method='POST')
        request.add_header('Content-Type', 'application/json')
        response = urlopen(request, data.encode('utf8'), timeout=5)
        body = response.read().decode()
        if body == 'ok':
            db.updatebyid('task_notify', {'status':'2', 'response_data':body, 'error': ''}, row['id'])
        else:
            error = 'the httpcode require 200, the body require ok;'
            db.updatebyid('task_notify', {'status':'301', 'response_data':body, 'error': error}, row['id'])
        return {'status':1, 'msg':'notify ok', 'donotify_notifyid':notifyid}
    except Exception as e:
        logger.error("doNotify::" + str(notifyid) + "::" + repr(e))
        db.updatebyid('task_notify', {'status':'3', 'error':repr(e)}, row['id'])
        return {'status':1, 'msg':repr(e), 'donotify_notifyid':notifyid}

def save(executeid, eventType = '', extData = {}):
    '''抓取完成通知
    executeid 执行ID
    eventType 事件类型，包括：spider_ok,piping_filterword,piping_fingerprint,piping_keywor,piping_error_http_code,piping_ok
    extData 附加数据，字典格式
    '''
    execute = db.getbyid('task_execute', executeid)
    startAt = formatTimestamp(execute['start_at']) if execute['start_at'] else ''
    endAt = formatTimestamp(execute['end_at']) if execute['end_at'] else ''
    requestData = {'status':execute['status'], 'start_at':startAt, 'end_at':endAt}
    requestData = dict(extData, **requestData)
    data = { 
        'site_id': execute['site_id'],
        'task_id': execute['task_id'],
        'app_id': execute['app_id'],
        'execute_id': execute['id'],
        'event_type': eventType,
        'task_type': execute['task_type'],
        'notify_url': execute['notify_url'],
        'request_data': json.dumps(requestData, ensure_ascii=False),
    }
    notifyId = db.insert('task_notify', data)
    data['id'] = notifyId
    data[mqidKey] = notifyId
    data[batchKey] = execute['id']
    Mq.produce([data], 'notify')
    return notifyId
