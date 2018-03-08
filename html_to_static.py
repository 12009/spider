# -*- coding: utf-8 -*-
import json
import time
import logging
from os import makedirs, getcwd
from pymongo import MongoClient
from os.path import dirname, exists
from subprocess import Popen, PIPE, STDOUT

PATH_ROOT = getcwd()
PATH_NODEJS = '%s/nodejs' % PATH_ROOT
PATH_GO = '%s/golang' % PATH_ROOT
PATH_TMP_NODEJS = '/tmp/spider/nodejs'
PATH_TMP_CODE = '/tmp/spider/code'
PATH_TMP_SNAPSHOT = '/tmp/spider/snapshot'
PATH_TMP_LOG = '/tmp/spider/log'
PATH_TMP_UPLOAD = '/tmp/spider/upload'
PATH_TMP_DOWNLOAD = '/tmp/spider/download'
PATH_TMP_QINIU = '/tmp/spider/qiniu'

MONGO_HOST = '172.16.100.212'
MONGO_PORT = 27017
MONGO_USER = 'spider'
MONGO_PASSWD = 'spider'
MONGO_DB_SPIDER = 'spider'
MONGO_DB_MQ = 'mq'
MONGO_POOLSIZE = 500 
MONGO_URL = 'mongodb://172.16.100.212:27017/spider'

def fwrite(filename, content):
    fp = open(filename, 'w+')
    fp.write(content)
    fp.close()

def mkdirs(path):
    if not exists(path):
        makedirs(path)

def ydfs_upload(key, localfile):
    try:
        cmd = '%s/dfs_client -action upload -config %s/client.json --filekey %s --file=%s' % (PATH_GO, PATH_GO, key, localfile)
        print(cmd)
        child = Popen(cmd, shell=True, close_fds=True, bufsize=-1, stdout=PIPE, stderr=STDOUT)
        output = child.stdout.read().decode()
        #remove(filename)
        return output
    except Exception as e:
        logging.exception(e)
        return False

def getMongo(mongoUrl, dbname, poolSize = 100):
    conn =  MongoClient(mongoUrl, connect=False, maxPoolSize = 100)
    return conn[dbname]

mongoSpider = getMongo(MONGO_URL, 'spider')

fields = {
    "static":['id', 'domain', 'url', 'md5_url', 'file_name', 'file_key', 'md5_body', 'create_at', 'update_at'],
    "static_int":['id'],
}

def now_format():
    '''格式化显示当前时间'''
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def _str2int(raw):
    '''字符串转整型'''
    if type(raw) == list:
        return [int(i) if type(i) == str else i for i in raw]
    else:
        return raw if type(raw) == int else int(raw)

def _get_autoid(table = None, step=1):
    '''获取自增ID'''
    step = _str2int(step)
    if step < 1: return False
    result = mongoSpider['autoids'].find_and_modify({"name":table}, {"$inc":{'id':step}})
    if result: 
        return result['id']+1 if step == 1 else [result['id']+1+i for i in list(range(step))]
    mongoSpider['autoids'].update({'name': table}, {'$set': {"name":table, "id":0}}, upsert=True)
    result = mongoSpider['autoids'].find_and_modify({"name":table}, {"$inc":{'id':step}})
    return result['id']+1 if step == 1 else [result['id']+1+i for i in list(range(step))]

def execute_getbyid(executeid, fields=[], display_id=False):
    '''根据ID获取execute'''
    fieldDict = {} if display_id else {"_id":0}
    for field in fields: fieldDict[field] = 1
    fieldDict = fieldDict if fieldDict else None
    return mongoSpider['execute'].find_one({'id':_str2int(executeid)}, fieldDict)

def static_get(domain, md5Body):
    '''根据文件md5获取文件信息'''
    return mongoSpider['static'].find_one({'domain':domain, 'md5_body':md5Body}, {'_id':0})

def c_insert(table, item):
    '''插入数据'''
    tableInt = '%s_int' % table
    item['id'] = _get_autoid(table)
    for field in fields[table]:
        if field not in item.keys():
            item[field] = 0 if field in fields[tableInt] else ''
    for field in fields[tableInt]:
        if field in item.keys():
            item[field] = _str2int(item[field])
    mongoSpider[table].insert(item)

def html_to_static(start, end):
    #where = {'execute_id':{'$gte':start, '$lt':end}}
    for eid in list(range(start, end)):
        where = {'execute_id':eid}
        select = {'_id':0, 'id':1, 'execute_id':1, 'error':1, 'http_code':1, 'body':1, 'md5_body':1, 'url':1, 'md5_url':1}
        for row in mongoSpider['spiderurl'].find(where, select):
            if row['error']: continue
            if row['http_code'] != 200: continue
            if not row['body']: continue
            print("%s    eid[%s]    urlid[%s]" % (now_format(), eid, row['id']))
            execute = execute_getbyid(row['execute_id'])
            result = static_get(execute['domain'], row['md5_body'])
            if result:
                filename = result['file_name']
                filekey = result['file_key']
            else:
                localfile = '%s/%s/%s.tmp' % (PATH_TMP_UPLOAD, execute['domain'], row['md5_body'])
                mkdirs(dirname(localfile))
                filename = "%s_%s.html" % (execute['id'], row['id'])
                filekey = 'html/%s/%s/%s_%s.html.%s' % (execute['domain'], execute['task_id'], execute['id'], row['id'], row['md5_body'])
                fwrite(localfile, row['body'])
                fileType = 'html'
                static =  {
                    'domain': execute['domain'],
                    'url': row['url'],
                    'file_name': filename,
                    'file_key': filekey,
                    'file_type': fileType,
                    'md5_url': row['md5_url'],
                    'md5_body': row['md5_body'],
                    'create_at': now_format(),
                    'update_at': now_format(),
                }
                filepath = ydfs_upload(filekey, localfile)
                c_insert('static', static)
            mongoSpider['spiderurl'].update({'id':row['id']}, {'$set':{'file_name':filename, 'file_path':filekey, 'body':''}})

        #mongoSpider['spiderurl'].update(where, {'$set':{'body':''}}, multi=True)

html_to_static(1, 100)

