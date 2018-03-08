from __future__ import absolute_import
import json
from common import db
from utils.time import getTime, formatTimestamp, now_format
from utils.security import md5
from utils.logger import logger


def get_id(settingid=None):
    sql = "select * from setting where id=%s"
    row = db.fetchone(sql, [settingid])
    if row:
        row['create_at'] = formatTimestamp(row['create_at'])
        row['update_at'] = formatTimestamp(row['update_at'])
        return row
    else:
        return False

def getall():
    sql = "select * from setting"
    rows = db.fetchall(sql)
    settings = []
    for row in rows:
        row['create_at'] = formatTimestamp(row['create_at'])
        row['update_at'] = formatTimestamp(row['update_at'])
        settings.append(row)

    return settings

def save(params = None):
    if not params['name'] or not params['key'] or not params['value']:
        return False
    settingdata = {
        'name': params['name'],
        'key': params['key'],
        'value': params['value'],
        'note': _defaultValue(params, 'note', ''),
    }
    if params['id']:
        settingid = params['id']
        db.updatebyid('setting', settingdata, settingid)
    else:
        settingid = db.insert('setting', settingdata)
    return settingid
