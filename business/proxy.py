from __future__ import absolute_import
import json
from common import db
from utils.security import md5
from utils.logger import logger
from utils.time import getTime, formatTimestamp, now_format

#代理列表
def get_id(proxyid=None):
    sql = "select * from proxy where id=%s"
    row = db.fetchone(sql, [proxyid])
    if row:
        row['create_at'] = formatTimestamp(row['create_at'])
        row['update_at'] = formatTimestamp(row['update_at'])
        return row
    else:
        return False

#代理列表
def getall():
    sql = "select * from proxy"
    rows = db.fetchall(sql)
    proxies = []
    for row in rows:
        row['create_at'] = formatTimestamp(row['create_at'])
        row['update_at'] = formatTimestamp(row['update_at'])
        proxies.append(row)

    return proxies

def save(params = None):
    if not params['ip'] or not params['port']:
        return False
    proxydata = {
        'ip': params['ip'],
        'port': params['port'],
        'username': _defaultValue(params, 'username', ''),
        'passwd': _defaultValue(params, 'passwd', ''),
    }
    if params['id']:
        proxyid = params['id']
        db.updatebyid('proxy', proxydata, proxyid)
    else:
        proxydata['status'] = 0
        proxyid = db.insert('proxy', proxydata)
    return proxyid
