# -*- coding: utf-8 -*-
import json
from copy import deepcopy
from utils.time import now_format
from common import mongoSpider
from utils.logger import logger

mgStatic = mongoSpider['static']
mgAutoids = mongoSpider['autoids']
mgExecute = mongoSpider['execute']
mgSpiderurl = mongoSpider['spiderurl']
mgSpiderjsurl = mongoSpider['spiderjsurl']
mgSnapshot = mongoSpider['snapshot']

fields = {
    "spiderurl":[
        'id', 'site_id', 'task_id', 'app_id', 'execute_id', 'task_type', 'url',  'url_type', 
        'md5_url', 'file_name', 'file_path', 'file_extension', 'referer', 'method', 'exec_level', 
        'depth', 'query', 'post', 'http_code', 'nettime', 'request_headers', 'response_headers', 
        'redirects', 'response_body_type', 'body', 'md5_body', 'invisible', 'pattern_path', 
        'pattern_query', 'pattern_post', 'error', 'status', 'start_at', 'end_at', 'create_at', 'update_at'],
    "spiderurl_int":['id', 'site_id', 'task_id', 'app_id', 'execute_id', 'exec_level', 'depth', 'status', 'invisible'],

    "spiderjsurl":['id', 'url', 'md5_url', 'referer', 'method', 'http_code', 'request_headers ', 
        'response_headers', 'redirects', 'body', 'md5_body', 'parse_result', 'error', 'status', 
        'start_at', 'end_at', 'create_at'],

    "execute":[
        'id', 'site_id', 'task_id', 'app_id', 'task_type', 'start_urls', 'exec_level', 'domain', 
        'limit_depth', 'limit_total', 'limit_time', 'limit_subdomain', 'limit_image', 'limit_js', 
        'limit_jsevent', 'exclude_urls', 'url_unique_mode', 'notify_url', 'source_ip', 'proxies',
        'status', 'start_at', 'end_at', 'create_at', 'update_at'],
    "execute_int":['id', 'site_id', 'task_id', 'app_id', 'exec_level', 'limit_depth', 
        'limit_total', 'limit_time', 'limit_subdomain', 'limit_image', 'limit_js', 'limit_jsevent'],

    "snapshot":['id', 'app_key', 'batch_no', 'uuid', 'type', 'url', 'filename', 'words', 'proxy', 
        'notify_url', 'error', 'status', 'create_at', 'update_ad'],
    "snapshot_int":['id', 'status'],

    "static":['id', 'domain', 'url', 'md5_url', 'file_name', 'file_key', 'md5_body', 'create_at', 'update_at'],
    "static_int":['id'],

    "parse":['id', 'site_id', 'task_id', 'app_id', 'execute_id', 'url_id', 'referer', 'url', 
        'md5_url', 'md5_body', 'parse_type', 'result', 'create_at', 'update_at'],
    "parse_int": ['id', 'site_id', 'task_id', 'app_id', 'execute_id', 'url_id'],

    'outlink': ['id', 'site_id', 'domain_id', 'task_id', 'execute_id', 'domain', 'url', 'md5_url', 
        'outlink', 'md5_outlink', 'invisible', 'filterwords', 'create_at', 'update_at'],
    'outlink_int': ['id', 'site_id', 'domain_id', 'task_id', 'execute_id', 'invisible'],
}

##################################################### 通用私有方法 ######################################################
def _str2int(raw):
    '''
    字符串转整型
    传入字符串和整型统一返回整型，且为一个参数
    '''
    if type(raw) == list:
        return [int(i) if type(i) == str else i for i in raw]
    else:
        return raw if type(raw) == int else int(raw)

def _get_autoid(table = None, step=1):
    '''获取自增ID'''
    step = _str2int(step)
    if step < 1: return False
    result = mgAutoids.find_and_modify({"name":table}, {"$inc":{'id':step}})
    if result: 
        return result['id']+1 if step == 1 else [result['id']+1+i for i in list(range(step))]
    mgAutoids.update({'name': table}, {'$set': {"name":table, "id":0}}, upsert=True)
    result = mgAutoids.find_and_modify({"name":table}, {"$inc":{'id':step}})
    return result['id']+1 if step == 1 else [result['id']+1+i for i in list(range(step))]

##################################################### 通用公有方法 ######################################################
def c_insert(table, item, autoid=True):
    '''插入数据'''
    tableInt = '%s_int' % table
    if autoid:
        item['id'] = _get_autoid(table)
    for field in fields[table]:
        if field not in item.keys():
            item[field] = 0 if field in fields[tableInt] else ''
    for field in fields[tableInt]:
        if field in item.keys():
            item[field] = _str2int(item[field])
    mongoSpider[table].insert(item)
    return item['id']

def c_getbyids(table, ids, fields=[], display_id=False):
    '''根据ID或一组ID获取数据'''
    ids = _str2int(ids)
    fieldDict = {} if display_id else {"_id":0}
    for field in fields: fieldDict[field] = 1
    fieldDict = fieldDict if fieldDict else None
    if type(ids) == int:
        return mongoSpider[table].find_one({'id':ids}, fieldDict)
    else:
        return [i for i in mongoSpider[table].find({'id':{'$in':ids}}, fieldDict)]

def c_updatebyids(table, setting, ids):
    '''根据一组id更新spider_url'''
    tableInt = "%s_int" % table
    sets  = {}
    for field in fields[table]:
        if field in setting.keys():
            sets[field] = setting[field]
    for field in fields[tableInt]:
        if field in sets.keys():
            sets[field] = _str2int(sets[field])
    return mongoSpider[table].update({'id':{"$in":_str2int(ids)}}, {"$set":sets}, upsert=False, multi=True)

def c_insert_batch(table, items):
    '''批量插入数据'''
    tableInt = '%s_int' % table
    length = len(items)
    ids = _get_autoid(table, length)
    if length == 1:  ids = [ids]
    inserts = []
    for index, item in enumerate(items):
        item['id'] = ids[index]
        for field in fields[table]:
            if field not in item.keys():
                item[field] = 0 if field in fields[tableInt] else ''
        for field in fields[tableInt]:
            if field in item.keys():
                item[field] = _str2int(item[field])
        inserts.append(item)
    mongoSpider[table].insert(deepcopy(inserts))
    return inserts

############################################ spiderjsurl ########################################################
def spiderjsurl_getbyid(urlid, fields=[], display_id=False):
    if not urlid: return False
    fieldDict = {} if display_id else {"_id":0}
    for field in fields: fieldDict[field] = 1
    fieldDict = fieldDict if fieldDict else None
    return mgSpiderurl.find_one({'id':urlid}, fieldDict)

def spiderjsurl_save(record):
    if 'id' not in record.keys(): return False
    urlid = record['id']
    raw = mgSpiderjsurl.find_one({'id':urlid})
    if raw:
        for key, value in record.items():
            raw[key] = value
    else:
        raw = record
        raw['id'] = urlid
    mgSpiderjsurl.update({'id':urlid}, {"$set":raw}, upsert=True)

#################################################### spiderurl #######################################################
def spiderurl_save(spiderUrl, urlid=None):
    '''更新spider_url中的数据'''
    if urlid:
        spiderUrl['id'] = urlid
    else:
        if 'id' not in spiderUrl.keys(): return False
        urlid = spiderUrl['id']
    mgRow = mgSpiderurl.find_one({'id':urlid})
    if not mgRow: return False
    for key, value in spiderUrl.items(): mgRow[key] = value
    for field in fields['spiderurl_int']:
        if field in spiderUrl.keys():
            spiderUrl[field] = _str2int(spiderUrl[field])
    return mgSpiderurl.update({'id':urlid}, {"$set":mgRow}, upsert=False)

def spiderurl_getbyid(urlid, fields=[], display_id=False):
    '''根据ID获取spider_url'''
    urlid = urlid if type(urlid) == int else int(urlid)
    fieldDict = {} if display_id else {"_id":0}
    for field in fields: fieldDict[field] = 1
    fieldDict = fieldDict if fieldDict else None
    return mgSpiderurl.find_one({'id':urlid}, fieldDict)


def spiderurl_getbyexecuteid(executeid, fields=[], display_id=False):
    '''根据execute_id获取spider_url'''
    fieldDict = {} if display_id else {"_id":0}
    for field in fields: fieldDict[field] = 1
    fieldDict = fieldDict if fieldDict else None
    return [i for i in mgSpiderurl.find({'execute_id':_str2int(executeid)}, fieldDict)]

def spiderurl_getall_executeid_status(executeid, status=2, fields=[], display_id=False):
    '''根据execute_id获取spider_url'''
    fieldDict = {} if display_id else {"_id":0}
    for field in fields: fieldDict[field] = 1
    fieldDict = fieldDict if fieldDict else None
    return [i for i in mgSpiderurl.find({'execute_id':_str2int(executeid), 'status':_str2int(status)}, fieldDict)]

def spiderurl_remove_taskid(taskid):
    if not taskid: return False
    mgSpiderurl.delete_many({'task_id':_str2int(taskid)})
    return True

def spiderurl_remove_executeid(executeid):
    if not executeid: return False
    mgSpiderurl.delete_many({'execute_id':_str2int(executeid)})
    return True

def spiderurl_update_ids(setting, ids):
    '''根据一组id更新spider_url'''
    return mgSpiderurl.update({'id':{"$in":_str2int(ids)}}, {"$set":setting}, upsert=False, multi=True)

############################################## execute  ###########################################################
def execute_save(execute):
    '''更新execute中的数据 这里只存储统计性的数据'''
    if 'id' not in execute.keys(): return False
    execute['id'] = _str2int(execute['id'])
    mgRow = mgExecute.find_one({'id':execute['id']})
    if not mgRow: return False
    for key, value in execute.items(): mgRow[key] = value
    for field in fields['execute_int']:
        if field in mgRow.keys():
            mgRow[field] = _str2int(mgRow[field])
    return mgExecute.update({'id':execute['id']}, {"$set":mgRow}, upsert=False)

def execute_update_ids(setting, ids):
    '''根据一组id更新spider_url'''
    return mgExecute.update({'id':{"$in":_str2int(ids)}}, {"$set":setting}, upsert=False, multi=True)

def execute_update_ids_status(setting, ids, status):
    '''根据一组id更新spider_url'''
    return mgExecute.update({'id':{"$in":_str2int(ids)}, 'status':_str2int(status)}, {"$set":setting}, upsert=False, multi=True)

def execute_getbyid(executeid, fields=[], display_id=False):
    '''根据ID获取execute'''
    fieldDict = {} if display_id else {"_id":0}
    for field in fields: fieldDict[field] = 1
    fieldDict = fieldDict if fieldDict else None
    return mgExecute.find_one({'id':_str2int(executeid)}, fieldDict)

#############################################  snapshot ################################################################
def snapshot_update_id(setting, id):
    '''更新快照信息'''
    return mgSnapshot.update({'id':_str2int(id)}, {"$set":setting}, upsert=False, multi=True)

#############################################  static files ################################################################
def static_get(domain, md5Body):
    '''根据文件md5获取文件信息'''
    return mgStatic.find_one({'domain':domain, 'md5_body':md5Body}, {'_id':0})

