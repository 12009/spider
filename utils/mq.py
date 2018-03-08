'''Mq 消息队列
用于实现下面的目标：
1. 实现最基本的生产与消费功能
2. 根据业务需要，可定制任务的优先级，队列消费速度等
3. 可实现分布式部署，水平扩展，动态调整消费者资源
4. 支持亿级业务量
'''
import json
from os import getpid
from socket import gethostname
from utils.time import getTime
from pymongo import ASCENDING, DESCENDING
from utils.logger import loggerMq as logger
from utils.time import now_format
from utils.file import read
from config.config import MQ
from common import db,redis, mongoMq

mqidKey = 'mq_id'
batchKey = 'mq_batch'
hostname = gethostname()
statsDefault = {"undo": 0, "ready": 0, "doing": 0, "done": 0, "end": 0, "total": 0}
def _get_proc_title():
    '''获取进程名称'''
    pid = getpid()
    title = read('/proc/%s/cmdline' % pid)
    return title

def produce(data = [], mqkey=''):
    '''生产任务'''
    #插入未执行的任务
    if not mqkey: return False
    undoKey = 'mq_%s_undo' % mqkey
    for row in data:
        mongoMq[undoKey].find_and_modify({mqidKey:row[mqidKey]}, {'$set': row}, upsert=True)
    mongoMq['stats_mq'].find_and_modify({'mq_key':mqkey}, {"$inc":{"undo":len(data)}})
    stats = {}
    for row in data:
        if row[batchKey] not in stats.keys(): stats[row[batchKey]] = 0
        stats[row[batchKey]] = stats[row[batchKey]] + 1

    for batch, total in stats.items():
        result = mongoMq['stats_batch_stage'].find_one({"mqkey": mqkey, 'batch':batch})
        if not result: mongoMq['stats_batch_stage'].find_and_modify({"mqkey": mqkey, 'batch': batch}, {"$set":statsDefault}, upsert=True)
        mongoMq['stats_batch_stage'].find_and_modify({"mqkey": mqkey, 'batch':batch}, {"$inc":{"undo":total, "total":total}})

def ready(mqkey = ''):
    '''添加准备执行的任务'''
    if not mqkey: return False
    undoKey = 'mq_%s_undo' % mqkey
    readyKey = 'mq_%s_ready' % mqkey
    readyKeyRedis = 'mq_%s_ready' % mqkey

    # 将ready队列中不足的部分补齐
    if redis.llen(readyKeyRedis) >= MQ[mqkey]['ready_total']: return True

    readyLackLen = MQ[mqkey]['ready_total'] - redis.llen(readyKey)
    stats = {}
    readySupplyLen = 0
    for row in mongoMq[undoKey].find({},{"_id":0}).sort([(batchKey, 1), (mqidKey, 1)]).limit(readyLackLen):
        redis.rpush(readyKeyRedis, json.dumps(row, ensure_ascii=False))
        mongoMq[readyKey].find_and_modify({mqidKey:row[mqidKey]}, {'$set': row}, upsert=True)
        mongoMq[undoKey].delete_many({mqidKey:row[mqidKey]})
        if row[batchKey] not in stats.keys(): stats[row[batchKey]] = 0
        stats[row[batchKey]] = stats[row[batchKey]] + 1
        readySupplyLen = readySupplyLen + 1
    for batch, total in stats.items():
        mongoMq['stats_batch_stage'].find_and_modify({"mqkey": mqkey, 'batch': batch}, {"$inc":{"undo":-total, "ready":total}})

def consume(mqkey = ''):
    '''消费任务'''
    if not mqkey: return False
    readyKey = 'mq_%s_ready' % mqkey
    doingKey = 'mq_%s_doing' % mqkey
    readyKeyRedis = 'mq_%s_ready' % mqkey
    jsonRaw = redis.lpop(readyKeyRedis)
    if not jsonRaw: return False
    item = json.loads(jsonRaw.decode('UTF8'))

    #写入 batchid
    runBatch = mongoMq['stats_batch_run'].find_one({'mqkey': mqkey, 'batch': item[batchKey]})
    if not runBatch:
        mongoMq['stats_batch_run'].insert({"mqkey": mqkey, "batch": item[batchKey], "is_end": 0, "start_at": now_format(), "end_at": ""})

    #更新当前队列ID
    title = _get_proc_title()
    mongoMq['process_list'].find_and_modify({'hostname': hostname, 'title':title[7:]}, {'$set':{mqidKey:item[mqidKey]}})

    mongoMq[doingKey].find_and_modify({mqidKey:item[mqidKey]}, {'$set': item}, upsert=True)
    mongoMq[readyKey].delete_many({mqidKey:item[mqidKey]})
    mongoMq['stats_mq'].find_and_modify({'mq_key':mqkey}, {"$inc":{"ready":-1, "doing":1}})
    mongoMq['stats_batch_stage'].find_and_modify({"mqkey":mqkey, 'batch':item[batchKey]}, {"$inc":{"ready":-1, "doing":1}})
    return item

def finish(mqid, mqkey = ''):
    '''结束任务'''
    if not mqkey: return False
    doneKey = 'mq_%s_done' % mqkey
    doingKey = 'mq_%s_doing' % mqkey
    doing = mongoMq[doingKey].find_one({"id":mqid},{"_id":0})
    if not doing:
        logger.error("mq::finish::::%s::::%s"% (mqkey, mqid))
        return False

    mongoMq[doingKey].delete_many({mqidKey:mqid})
    mongoMq[doneKey].find_and_modify({mqidKey:doing[mqidKey]}, {'$set': doing}, upsert=True)

    mongoMq['stats_mq'].find_and_modify({'mq_key':mqkey}, {"$inc":{"doing":-1, "done":1}})
    mongoMq['stats_batch_stage'].find_and_modify({"mqkey": mqkey, 'batch':doing[batchKey]}, {"$inc":{"doing":-1,"done":1}})
    return True

def get_stats_batch(mqkey, batch):
    '''获取运行状态'''
    return mongoMq['stats_batch_stage'].find_one({'mqkey':mqkey, 'batch':batch},{"_id":0})

