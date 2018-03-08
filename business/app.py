from __future__ import absolute_import
import json
from common import db, redis
from db import mongodb as mgdb
from utils.time import getTime, formatTimestamp, now_format
from utils.security import md5
from utils.logger import logger

def getToken_key(key):
    appObj = db.fetchone('select * from app where unique_key=:key', {'key':key})
    if not appObj:
        return False

    tokenExpired = getTime("%Y-%m-%d %H:%M:%S" , (getTime() + 7200))
    token = md5(tokenExpired)
    db.updatebyid('app', {'token':token, 'token_expired':tokenExpired}, appObj['id'])
    return {'token':token, 'expired':tokenExpired}

def get_id(appid=None):
    row = db.fetchone("select * from app where id=:id", {'id':appid})
    if row:
        row['token_expired'] = formatTimestamp(row['token_expired'])
        row['create_at'] = formatTimestamp(row['create_at'])
        row['update_at'] = formatTimestamp(row['update_at'])
        del(row['public_key'])
        return row
    else:
        return False

def getall():
    sql = "select * from app order by id desc"
    rows = db.fetchall(sql)
    apps = []
    for row in rows:
        row['token_expired'] = formatTimestamp(row['token_expired'])
        row['create_at'] = formatTimestamp(row['create_at'])
        row['update_at'] = formatTimestamp(row['update_at'])
        apps.append(row)

    return apps

def save(params = None):
    if not params['unique_key']: return False
    appdata = {
        'unique_key': params['unique_key'],
        'public_key': params['public_key'],
    }
    if params['id']:
        appid = params['id']
        db.updatebyid('app', appdata, appid)
    else:
        appid = db.insert('app', appdata)
    return appid

