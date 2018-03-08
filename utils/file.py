from __future__ import absolute_import
# -*- coding: utf-8 -*-

import os
import os.path
from qiniu import Auth, put_file
from subprocess import Popen, PIPE, STDOUT
from utils.logger import logger
from config.config import QINIU_ACCESS_KEY, QINIU_SECRET_KEY, QINIU_KEY_PREFIX, QINIU_BUCKET, QINIU_DOMAIN, PATH_GO

def write(filename, content):
    fp = open(filename, 'w+')
    fp.write(content)
    fp.close()

def append(filename, content):
    fp = open(filename, 'a+')
    fp.write(content)
    fp.close()

def writeBin(filename, content):
    fp = open(filename, 'wb')
    fp.write(content)
    fp.close()

def read(filename):
    fp = open(filename)
    content = fp.read()
    return content

def mkdirs(path):
    if not os.path.exists(path):
        os.makedirs(path)

def qiniu_upload(key, localfile):
    try:
        key = '%s/%s' % (QINIU_KEY_PREFIX, key)
        qiniu = Auth(QINIU_ACCESS_KEY, QINIU_SECRET_KEY)
        token = qiniu.upload_token(QINIU_BUCKET, key, 86400)
        ret, info = put_file(token, key, localfile)
        return {'key':key, 'hash':ret['hash'], 'url': "%s/%s" % (QINIU_DOMAIN, key)}
    except Exception as e:
        return False

def ydfs_upload(key, localfile):
    try:
        cmd = '%s/dfs_client -action upload -config %s/client.json --filekey %s --file=%s' % (PATH_GO, PATH_GO, key, localfile)
        child = Popen(cmd, shell=True, close_fds=True, bufsize=-1, stdout=PIPE, stderr=STDOUT)
        output = child.stdout.read().decode()
        #remove(filename)
        return output
    except Exception as e:
        logger.exception(e)
        return False

