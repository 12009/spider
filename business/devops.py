import json
from utils import mq as Mq
from utils.file import read
from db import mongodb as mgdb
from utils.logger import logger
from business import task as bTask
from config.config import PATH_ROOT
from utils.time import formatTimestamp
from utils.time import getTime, now_format
from common import db, redis, mongoMq, mongoSpider

def task_clean(taskid):
    '''清理任务数据'''
    try:
        if not taskid: return False

        #删除任务
        db.exec('delete from task where id=:id', {'id':taskid})

        #根据任务ID清理任务执行
        db.exec("delete from task_execute where task_id=:id", {'id':taskid})

        #使用in操作,仅为测试，性能较低
        taskIds = [taskid]
        sqlIn = "','".join(['spider_execute_%s'] * len([taskIds]))
        db.exec("delete from djcelery_periodictask where name in ('%s')" % sqlIn, taskIds)

        #根据任务ID清理抓取到的URL
        db.exec("delete from spider_url where task_id=:id", {'id': taskid})

        #根据任务ID清理数据处理结果
        db.exec("delete from task_piping where task_id=:id", {'id': taskid})
        db.exec("delete from task_piping_result where task_id=:id", {'id': taskid})
        #db.exec("delete from piping_result where task_id=:id", {'id': taskid})

        #根据任务ID删除mongodb数据
        mgdb.remove_taskid(taskid)

        #根据任务ID清理文件及快照等   @todo
    except Exception as e:
        logger.exception(e)
        return False

def execute_clean(executeid):
    db.exec("delete from task_execute where id=:id",  {'id': executeid})
    db.exec("delete from spider_url where execute_id=:id",  {'id': executeid})
    db.exec("delete from task_notify where execute_id=:id",  {'id': executeid})
    #根据执行ID删除mongodb数据
    executeid = executeid if type(executeid) == int else int(executeid)
    mongoSpider['spiderurl'].delete_many({"execute_id":executeid})

def postgres2mongo(executeid):
    '''根据执行ID将数据从数据库转移到mongodb
    example:
        #for executeid in list(range(10000)):
        #    postgres2mongo(executeid)
    '''
    rows = db.fetchall('select * from spider_url where execute_id=:id', {'id': executeid})
    if not rows: return False
    for row in rows:
        row['start_at'] = formatTimestamp(row['start_at']) if row['start_at'] else ''
        row['end_at'] = formatTimestamp(row['end_at']) if row['end_at'] else ''
        row['create_at'] = formatTimestamp(row['create_at']) if row['create_at'] else ''
        row['update_at'] = formatTimestamp(row['update_at']) if row['update_at'] else ''
    mongoSpider['spiderurl'].insert(rows)
    return True

def init_system():
    #导入初始token
    sql = "insert into app(id, unique_key, public_key, token, token_expired) values(1,'tester_app','-----BEGIN RSA PUBLIC KEY-----\nMIIBCgKCAQEAvLWMYgTwkLMI8ZSw8Pd7NBKUVr0kbyqHijKOOQmR5/EKHOwgak0u\nu3+wBsllmIgfa4cT0zp4Gdd4hx2UmpIjG4eHwCgUCHHmCedu87/zEQhzE2do9p09\nBzPs7GG/azuynPJp6mZFxycaGZaoHH1d3FNWJ+yRBQ5UliFw01Tby3j7cV5u9fNU\nOjSZRGBNkHLxUi56kkbIZ46Wz14DVCjfZh6HRcwWKZHnQTDaIJKGKDbJoAbY/EIi\nrUc8OQl57PNq35hc0AJdFHa5oDQ5WtsCXx3q7XNhKjZdR/Vs4kljns5k9/zylJLn\nXI5ly2j46nz+feMaGVP1BdJpPUVWrAcgFQIDAQAB\n-----END RSA PUBLIC KEY-----','wbsllmigfa4ct0zp4gdd4hx2umpijg4e', '2017-03-22 17:01:53');"
    db.exec(sql)

    #@系统敏感词库
    pipingType = 'filterword'
    row = db.fetchone("select * from piping_extend where task_id=:task_id and piping_type=:piping_type limit 1", {'task_id':0, 'piping_type': pipingType})
    if not row:
        insertRow = {"app_id":0, "site_id":0, "task_id":0, "piping_type": pipingType, "data": "", "status": 1}
        extendId = db.insert("piping_extend", insertRow)
    else:
        extendId = row["id"]
    content = read("%s/doc/sensitive_word.txt" % PATH_ROOT)
    db.updatebyid("piping_extend", {"data":content.strip(), "status":1}, extendId)

    #@系统异常状态码
    pipingType = 'err_http_code'
    row = db.fetchone("select * from piping_extend where task_id=:task_id and piping_type=:piping_type limit 1", {'task_id':0, 'piping_type':pipingType})
    if not row:
        insertRow = {"app_id":0, "site_id":0, "task_id":0, "piping_type": pipingType, "data": "", "status": 1,}
        extendId = db.insert("piping_extend", insertRow)
    else:
        extendId = row["id"]
    content = "\n".join(['401', '402', '403', '404', '405', '500', '501', '502', '503', '504'])
    db.updatebyid("piping_extend", {"data":content.strip(), "status":1}, extendId)


def clean_all():
    #危险，慎用
    return True
    #db.exec("TRUNCATE TABLE app CASCADE;")
    for table in ['task', 'task_execute', 'site', 'domain', 'setting', 'proxy', 'task_notify', 'task_piping', 'dk_black_list',
        'dk_white_list','dk_filterword','task_piping_result', 'task_piping_snapshot', 'spider_url', 'spiderjs_url', 'piping_extend', 'scheduler']:
        db.exec("delete from %s;" % table)

    for seq in ['app_id_seq', 'task_id_seq', 'task_execute_id_seq', 'site_id_seq', 'domain_id_seq', 'setting_id_seq',
        'dk_black_list_id_seq','dk_filterword_id_seq','dk_white_list_id_seq','proxy_id_seq', 'task_notify_id_seq', 'task_piping_id_seq', 'task_piping_result_id_seq', 'task_piping_snapshot_id_seq',
        'spider_url_id_seq', 'piping_extend_id_seq']:
        db.exec("ALTER SEQUENCE %s RESTART WITH 1;" % seq)

    itemSpider = {
        'spiderurl': {'unique':['id'], 'index': ['task_id', 'execute_id']},
        'execute': {'unique':['id'], 'index': ['task_id']},
        'static': {'unique':['domain', 'md5_body'], 'index': ['domain', 'md5_url', 'md5_body']},
        'autoids': {'unique':['name'], 'index':[]},
        'parse': {'unique':[], 'index':['task_id', 'execute_id', 'md5_url']},
        'snapshot': {'unique':['id'], 'index':['app_key', 'batch']},
        'outlink': {'unique':[], 'index':['domain', 'md5_referer', 'md5_url', 'md5_body', 'date']},
    }
    for key, item in itemSpider.items():
        mongoSpider[key].drop()
        if item['unique']:
            uniqueField = [(field, 1) for field in item['unique']]
            mongoSpider[key].ensure_index(uniqueField, unique=True)
        if item['index']:
            for field in item['index']:
                mongoSpider[key].ensure_index(field)

    itemMq = {
        'mq_spider_undo':    {'unique':['mq_id'], 'index': ['mq_batch']},
        'mq_spider_ready':   {'unique':['mq_id'], 'index': ['mq_batch']},
        'mq_spider_doing':   {'unique':['mq_id'], 'index': ['mq_batch']},
        'mq_spider_done':    {'unique':['mq_id'], 'index': ['mq_batch']},
        'mq_mirror_undo':    {'unique':['mq_id'], 'index': ['mq_batch']},
        'mq_mirror_ready':   {'unique':['mq_id'], 'index': ['mq_batch']},
        'mq_mirror_doing':   {'unique':['mq_id'], 'index': ['mq_batch']},
        'mq_mirror_done':    {'unique':['mq_id'], 'index': ['mq_batch']},
        'mq_piping_undo':    {'unique':['mq_id'], 'index': ['mq_batch']},
        'mq_piping_ready':   {'unique':['mq_id'], 'index': ['mq_batch']},
        'mq_piping_doing':   {'unique':['mq_id'], 'index': ['mq_batch']},
        'mq_piping_done':    {'unique':['mq_id'], 'index': ['mq_batch']},
        'mq_notify_undo':    {'unique':['mq_id'], 'index': ['mq_batch']},
        'mq_notify_ready':   {'unique':['mq_id'], 'index': ['mq_batch']},
        'mq_notify_doing':   {'unique':['mq_id'], 'index': ['mq_batch']},
        'mq_notify_done':    {'unique':['mq_id'], 'index': ['mq_batch']},
        'mq_snapshot_undo':  {'unique':['mq_id'], 'index': ['mq_batch']},
        'mq_snapshot_ready': {'unique':['mq_id'], 'index': ['mq_batch']},
        'mq_snapshot_doing': {'unique':['mq_id'], 'index': ['mq_batch']},
        'mq_snapshot_done':  {'unique':['mq_id'], 'index': ['mq_batch']},

        'stats_mq':          {'unique':['mqkey'],             'index': []},
        'stats_batch_run':   {'unique':['mqkey', 'batch'],    'index': []},
        'stats_batch_stage': {'unique':['mqkey', 'batch'],    'index': []},

        'process_list':      {'unique':['hostname', 'title'], 'index':['mqkey', 'status']},
        # 'process_config':    {'unique':['hostname'],          'index':[]},
    }
    for key, item in itemMq.items():
        mongoMq[key].drop()
        if item['unique']:
            uniqueField = [(field, 1) for field in item['unique']]
            mongoMq[key].ensure_index(uniqueField, unique=True)
        if item['index']:
            for field in item['index']:
                mongoMq[key].ensure_index(field)

    for key in ['spider', 'mirror', 'piping', 'notify', 'snapshot']:
        redis.delete('mq_%s_ready' % key)
# clean_all()


def init_app():
    '''只系统上线，初始化时使用，谨慎操作'''
    return True

    #tsgz
    appid = 2
    app = {
        'id': appid,
        'unique_key':'tsgz',
        'public_key': "-----BEGIN RSA PUBLIC KEY-----\nMIIBCgKCAQEA9Vp7hhFpJe2zYuGDDBQ2wb0e7tKHwfHdE6e8ZUJDkMgPLKBEbHwo\nSuvLXgrtGqjclVSIn6Py+NmQbtWxnOZuV/2O/jzhnflu8vVoXVwEuj4gj3+jGZV4\nB0MFICeZ/+qM2UcqrquxQrLhV1gU8InaaTgkMtC4Iag38YdDUy6MdBH7yOQzmUuq\nd5PhbsZeb45Y2OSuq2jhg3d1Xu1vHIrj1A0jSs99d5lOdubpCu7l1JC3WrjVBISj\nlQnrQmUATVy6Tr0Wvv8n1hqaZVNGpAM6pI4UtF+OldU7MrNqQzc+8a5hj2A2SGZE\nfPgyjaS8p+/K4tECY0STfXtB7wjg8oU8bQIDAQAB\n-----END RSA PUBLIC KEY-----",
        'token': '9a684815a09c65edb52b7612cda4b1ad',
        'token_expired': now_format(),
    }
    row = db.getbyid('app', appid)
    if row:
        db.updatebyid('app', app, appid)
    else:
        db.insert('app', app)

    #homev5_apiv4
    appid = 3
    app = {
        'id': appid,
        'unique_key':'homev5_apiv4',
        'public_key': "-----BEGIN RSA PUBLIC KEY-----\nMIIBCgKCAQEA7LRjexk787YP48ZiWOwHNa93VF+J0H/pdINSvqIqWU6yAarpkLWq\nKV9Xd27QCcK6z459b0v/S6QplOPWks7m0MCFrflxkAEjd6MtXJiq3a6rcnX1w0vu\nPozNcM8ibLQI6XoSWNx2sUlQDpDdT9JvdGsnoCfY+pAS3gycgAHzFJH9UbY68igk\nn1cqFuADso3YLXZssK+eslnsfK20iZPiobmSWACLz0vi0gxTABSLqXM3ovJBZgiB\n0QUqvKJY1pM0dHpVpnj73y3CutqH+v255x32y2DVfG4AC6hxCojIhQDx8vAqsKc1\nHYcKxCTPGGVGGvmDUDevwvmvF+GjDZ0SQQIDAQAB\n-----END RSA PUBLIC KEY-----",
        'token': '20d812f96badf9f811cde6f9916d5a50',
        'token_expired': now_format(),
    }
    row = db.getbyid('app', appid)
    if row:
        db.updatebyid('app', app, appid)
    else:
        db.insert('app', app)

    #homev5_apiv4_mirror
    appid = 4 
    app = {
        'id': appid,
        'unique_key':'homev5_apiv4_mirror',
        'public_key': "-----BEGIN RSA PUBLIC KEY-----\nMIIBCgKCAQEAwT90eOKM9YaUDYM1v2WR1TL7Qf1t3e3ogCkFSSbH0D4IBn/bVOi9\nCq7jDRZH9F75j6uGXymMLGF841kgrgn8NdyalqaLGRrufw+K971UfNToT/SEAW9O\n+HlZLIV+itAVbBly5/LJFc16aPUH2L47r8qFIFB0PfjLSAsHhbRRs6jLyuZTtzGi\no4iod7/5R+ip216fu7cxiAE3wBhfKTT7IYnAnW7+tYLPqlGcszJkSJtZozHcxudw\n4nVRu+2pkP9ud1YnbWSVGDADMQ33YaKSrm4O+dCDw5EqhmYo+0xH39TNS/2GjCK2\n83R0ZvuS9KkYCNhSYYEKVKiyTuavTpsWWwIDAQAB\n-----END RSA PUBLIC KEY-----",
        'token': '69866dde69bced6b006708b936e038c3',
        'token_expired': now_format(),
    }   
    row = db.getbyid('app', appid)
    if row:
        db.updatebyid('app', app, appid)
    else:
        db.insert('app', app)

    return True

def mq_clean(): 
    collections = ['stats_mq', 'stats_batch_run', 'stats_batch_stage',
        'mq_spider_undo', 'mq_spider_ready', 'mq_spider_doing', 'mq_spider_done',
        'mq_mirror_undo', 'mq_mirror_ready', 'mq_mirror_doing', 'mq_mirror_done',
        'mq_piping_undo', 'mq_piping_ready', 'mq_piping_doing', 'mq_piping_done',
        'mq_notify_undo', 'mq_notify_ready', 'mq_notify_doing', 'mq_notify_done',
        'mq_snapshot_undo', 'mq_snapshot_ready', 'mq_snapshot_doing', 'mq_snapshot_done',
    ]
    for key in collections:
        mongoMq[key].drop() 
 
    for i in ['execute', 'spider', 'mirror', 'piping', 'notify', 'snapshot']:
        key = "mq_%s_ready" % i
        redis.delete(key)
 
    mongoMq['stats_mq'].insert({'mq_key':'execute','undo':0, 'ready':0, 'doing':0, 'done':0}); 
    mongoMq['stats_mq'].insert({'mq_key':'spider', 'undo':0, 'ready':0, 'doing':0, 'done':0}); 
    mongoMq['stats_mq'].insert({'mq_key':'mirror', 'undo':0, 'ready':0, 'doing':0, 'done':0}); 
    mongoMq['stats_mq'].insert({'mq_key':'notify', 'undo':0, 'ready':0, 'doing':0, 'done':0}); 
    mongoMq['stats_mq'].insert({'mq_key':'piping', 'undo':0, 'ready':0, 'doing':0, 'done':0});

def mq_correct():
    '''运行时错误校正'''
    return True
    rawJson = redis.hget('mq_correct_running', 'checkdb')
    dataOld = json.loads(rawJson.decode()) if rawJson else {}
    dataNew = {}
    rows = db.fetchall('select id,status from task_execute where status in(0,1,2) order by id asc;')
    stages = ['undo', 'ready', 'doing', 'done']
    batchErrors = {}
    for row in rows:
        errors = []
        eid = str(row['id'])
        dataNew[eid] = 'ok'
        logger.debug("mq execute check ::::%s" % eid)

        if eid in dataOld.keys() and dataOld[eid] == 'ok': continue

        logger.debug("mq_correct_running checkdb::::%s" % eid)
        execute = mongoSpider['execute'].find_one({'id':row['id']}, {'_id':0})
        if not execute: errors.append('noexecute')

        urlCount = mongoSpider['spiderurl'].find({'execute_id':row['id']}, {'_id':0}).count()
        if not urlCount: errors.append('nourl')

        pre = 'mq_spider_'                  
        stats = {stage:mongoMq[pre+stage].find({'mq_batch':row['id']}).count() for stage in stages}
        total = stats['undo'] + stats['ready'] + stats['doing'] + stats['done']
        if not total: errors.append('nomq')

        if errors: 
            batchErrors[eid] = errors
            dataNew[eid] = 'uncheck'
    idsDel = list(set(dataOld.keys()) - set(dataNew.keys()))
    for batch in idsDel: del(dataOld[batch])
    dataOld.update(dataNew)
    redis.hset('mq_correct_running', 'checkdb', json.dumps(dataOld, ensure_ascii=False))

    logger.debug("mq execute error ::::%s" % json.dumps(errors, ensure_ascii=False))

    #url数据未写入
    for batch,errors in batchErrors.items():
        bTask.execute_init(batch)

def mq_do_dead():
    '''检查执行过程中死掉的任务，重新添加回待执行中'''
    from time import sleep
    mqkeys = ['spider', 'mirror', 'piping', 'notify', 'snapshot']
    for mk in mqkeys:
        plkey = 'process_list'
        undokey  = 'mq_%s_undo'  % mk
        doingkey = 'mq_%s_doing' % mk
        mqidsProc =  [i['mqid'] for i in mongoMq[plkey].find({'mqkey':mk}, {'_id':0, 'mqid':1})]
        mqidsDoing = [i['mq_id'] for i in mongoMq[doingkey].find({}, {'_id':0, 'mq_id':1})]
        mqidsDie = list(set(mqidsDoing) - set(mqidsProc))
        sleep(1)
        stats = {}
        mqidsDead = [i['mq_id'] for i in mongoMq[doingkey].find({'mq_id':{'$in':mqidsDie}}, {'_id':0, 'mq_id':1})]
        for row in mongoMq[doingkey].find({'mq_id':{'$in':mqidsDead}}, {'_id':0}):
            mongoMq[undokey].update({'id':row['id']}, row, upsert=True)
            mongoMq[doingkey].delete_many({'id':row['id']})
            if row['mq_batch'] not in stats.keys(): stats[row['mq_batch']] = 0
            stats[row['mq_batch']] = stats[row['mq_batch']] + 1
        for batch,total in stats.items():
            mongoMq['stats_batch_stage'].update({'mqkey':mk, 'batch':batch}, {"$inc":{'doing':-total, 'undo':total}})

def mq_resetstats(batchs = []):
    '''重新计数，此方便仅适合手工执行'''
    for batch in batchs:
        logger.debug("mq stats reset::::%s" % batch)
        mqkeys = ['spider', 'mirror', 'piping', 'notify', 'snapshot']
        stages = ['undo', 'ready', 'doing', 'done']
        for mk in mqkeys:
            stats = {}
            for stage in stages:
                stats[stage] = mongoMq['mq_%s_%s' % (mk,stage)].find({'mq_batch':batch}).count()
            stats['total'] = stats['undo'] + stats['ready'] + stats['doing'] + stats['done']
            mongoMq['stats_batch_stage'].update({"batch":batch, 'mqkey':mk}, {"$set":stats})

        ## 数据统计状态修正
        #for mk in mqkeys:
        #    stats = {}
        #    for stage in stages:
        #        stats[stage] = mongoMq['mq_%s_%s' % (mk,stage)].find({'mq_batch':batch}).count()
        #    if not stats['undo'] and not stats['ready'] and not stats['doing'] and stats['done']:
        #        mongoMq['stats_batch_stage'].update({'mqkey':mk, "batch":batch}, {"$set":{"end":0}})

def mq_checkbybatch(batch):
    items = {
        'spider': ['undo', 'ready', 'doing', 'done'],
        'mirror': ['undo', 'ready', 'doing', 'done'],
        'piping': ['undo', 'ready', 'doing', 'done'],
        'notify': ['undo', 'ready', 'doing', 'done'],
    }
    execute = db.getbyid('task_execute', batch)
    stats = {}
    stats['task_type'] = execute['task_type']
    stats['execute_status'] = execute['status']
    for k, stages in items.items():
        for stage in stages:
            stats["%s_%s_stage"%(k,stage)] = mongoMq['mq_%s_%s' % (k, stage)].find({'mq_batch':batch}).count()
        row = mongoMq['mq_batch_stage'].find_one({'mqkey':k, 'batch':batch})
        stats["%s_undo_stats"%k] = row['undo'] if row else 0
        stats["%s_ready_stats"%k] = row['ready'] if row else 0
        stats["%s_doing_stats"%k] = row['doing'] if row else 0
        stats["%s_done_stats"%k] = row['done'] if row else 0
    stats['spiderurl'] = mongoSpider['spiderurl'].find({'execute_id':batch}).count()

    keys = [
        'task_type',   'execute_status',
        'spider_undo_stage', 'spider_ready_stage', 'spider_doing_stage', 'spider_done_stage', 'spider_undo_stats', 'spider_ready_stats', 'spider_doing_stats', 'spider_done_stats',
        'mirror_undo_stage', 'mirror_ready_stage', 'mirror_doing_stage', 'mirror_done_stage', 'mirror_undo_stats', 'mirror_ready_stats', 'mirror_doing_stats', 'mirror_done_stats',
        'piping_undo_stage', 'piping_ready_stage', 'piping_doing_stage', 'piping_done_stage', 'piping_undo_stats', 'piping_ready_stats', 'piping_doing_stats', 'piping_done_stats',
        'notify_undo_stage', 'notify_ready_stage', 'notify_doing_stage', 'notify_done_stage', 'notify_undo_stats', 'notify_ready_stats', 'notify_doing_stats', 'notify_done_stats',
        'spiderurl'
    ]
    values = [key+': '+str(stats[key]) for key in keys]
    return "\n".join(values)

