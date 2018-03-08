# -*- coding: utf-8 -*-

from os import mkdir
from os.path import dirname, dirname, exists as path_exists

#蜘蛛系统级配置
SPIDER_CHARSET = 'utf8'
SPIDER_TIMEZONE = "Asia/Shanghai"
PYBIN = '/data/pyenv/env35/bin/python3.5'

#路径配置
PATH_ROOT = dirname(dirname(__file__))
PATH_NODEJS = '%s/nodejs' % PATH_ROOT
PATH_GO = '%s/golang' % PATH_ROOT
PATH_TMP = '/tmp/spider'
PATH_TMP_NODEJS = '/tmp/spider/nodejs'
PATH_TMP_CODE = '/tmp/spider/code'
PATH_TMP_SNAPSHOT = '/tmp/spider/snapshot'
PATH_TMP_LOG = '/tmp/spider/log'
PATH_TMP_UPLOAD = '/tmp/spider/upload'
PATH_TMP_DOWNLOAD = '/tmp/spider/download'
PATH_TMP_QINIU = '/tmp/spider/qiniu'

if not path_exists(PATH_TMP): mkdir(PATH_TMP)
if not path_exists(PATH_TMP_NODEJS): mkdir(PATH_TMP_NODEJS)
if not path_exists(PATH_TMP_CODE): mkdir(PATH_TMP_CODE)
if not path_exists(PATH_TMP_SNAPSHOT): mkdir(PATH_TMP_SNAPSHOT)
if not path_exists(PATH_TMP_LOG): mkdir(PATH_TMP_LOG)
if not path_exists(PATH_TMP_UPLOAD): mkdir(PATH_TMP_UPLOAD)
if not path_exists(PATH_TMP_DOWNLOAD): mkdir(PATH_TMP_DOWNLOAD)
if not path_exists(PATH_TMP_QINIU): mkdir(PATH_TMP_QINIU)

#日志配置
LOG_OUTPUT_STDIN = 1       #是否输出到标准输出 0/1

# 镜像配置
MIRROR_PROXY = '61.153.111.183:80'

# 数据库
DB_PG_HOST='127.0.0.1'
DB_PG_PORT='5432'
DB_PG_USER='postgres'
DB_PG_PASSWORD='dbadmin'
DB_PG_DATABASE='spider'
DB_PG_URL_SQL = "postgresql+psycopg2://postgres:dbadmin@127.0.0.1:5432/spider"

# redis
REDIS_HOST = '127.0.0.1'
REDIS_PORT = '6379'
REDIS_PASSWORD = 'bluedon_jcpt'
REDIS_DB = 0
REDIS_URL = 'redis://127.0.0.1:6379/0'

# mongo
MONGO_HOST = '127.0.0.1'
MONGO_PORT = 27017
MONGO_USER = 'spider'
MONGO_PASSWD = 'spider'
MONGO_DB_SPIDER = 'spider'
MONGO_DB_MQ = 'mq'
MONGO_POOLSIZE = 500
MONGO_URL = 'mongodb://127.0.0.1:27017/spider'

#MQ
MQ = {
    'spider': {
        'ready_total': 2000,
    },
    'mirror': {
        'ready_total': 2000,
    },
    'notify': {
        'ready_total': 2000,
    },
    'piping': {
        'ready_total': 2000,
    },
    'snapshot': {
        'ready_total': 2000,
    },
}

# 七牛云存储
QINIU_ACCESS_KEY = '06TsiBDnkSmmWNgP-yZG52vywrN5_IwRre1Z4NEM'
QINIU_SECRET_KEY = 'S45i2Sp4l8sa9MLMxbNloIQZu_g5n4NnRY8G2kg5'
QINIU_DOMAIN = 'https://yundun-statics.yundun.com'
QINIU_KEY_PREFIX = 'spider_snapshot_local'
QINIU_BUCKET = 'yundun'

# dfs 服务
DFS_URL = 'http://127.0.0.1:8058'
