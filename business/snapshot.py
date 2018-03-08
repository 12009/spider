'''
快照截图
'''
# -*- coding: utf-8 -*-

import math
from uuid import uuid1
from copy import deepcopy
from utils import mq as Mq
from os.path import basename
from db import mongodb as mgdb
from utils.logger import logger
from utils.time import now_format
from urllib.request import urlopen
from utils.file import qiniu_upload
from common import mongoMq, mongoSpider
from utils.browser import snapshot_view, snapshot_code
from config.config import PATH_TMP_SNAPSHOT, QINIU_DOMAIN, QINIU_KEY_PREFIX, DFS_URL

mqidKey = 'mq_id'
batchKey = 'mq_batch'
def _qiniu_url(filename):
    return "%s/%s/%s" % (QINIU_DOMAIN, QINIU_KEY_PREFIX, filename)

def save(params):
    '''保存快照'''
    item = {
        'app_key': params['app_key'],
        'batch': params['batch'],
        'uuid': uuid1().hex,
        'type': params['type'],
        'url': params['url'],
        'filename': params['filename'],
        'words': ",".join(params['words']),
        'proxy': params['proxy'],
        'notify_url': params['notify_url'],
        'error':'',
        'status':0,
        'create_at': now_format(),
        'update_at': now_format(),
    }
    if item['type'] == 'code':
        downloadUrl = '%s/download?filekey=%s' % (DFS_URL, params['url'])
        pagesize = 800
        body = urlopen(downloadUrl).read().decode('utf-8','ignore')
        total = len(body.split("\n"))
        pageTotal = math.ceil(total / pagesize)
        url = '%s/%s/%s' % (QINIU_DOMAIN, QINIU_KEY_PREFIX, basename(params['filename']))
        snapshots = [url.replace('.png', '_%s.png' % i) for i in list(range(pageTotal))]
        item['snapshot'] = "\n".join(snapshots)
    else:
        item['snapshot'] = '%s/%s/%s' % (QINIU_DOMAIN, QINIU_KEY_PREFIX, basename(params['filename']))

    itemid = mgdb.c_insert('snapshot', deepcopy(item))
    item['id'] = itemid
    item[mqidKey] = item['id']
    item[batchKey] = item['batch']
    Mq.produce([item], 'snapshot')
    return item['snapshot'].split("\n")

def generate(params):
    '''生成快照'''
    try:
        results = []
        if params['type'] == 'code':
            url = "%s/download?filekey=%s" % (DFS_URL, params['url'])
            body = urlopen(url).read().decode('utf-8','ignore')
            snapshots = snapshot_code(params['filename'], body, params['words'])
            for snapshot in snapshots: results.append(_qiniu_url(basename(snapshot)))

        else:
            tmpfile = "%s/%s" % (PATH_TMP_SNAPSHOT, params['filename'])
            result = snapshot_view(params['url'], tmpfile, params['words'])
            if result: results.append(_qiniu_url(params['filename']))

        mgdb.snapshot_update_id({'status':1}, params['id'])
        return results
    except Exception as e:
        logger.error("business.snapshot.generate::" + repr(e))
        mgdb.snapshot_update_id({'status':2}, params['id'])
        return False

