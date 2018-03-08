from __future__ import absolute_import
import json
import subprocess
from common import db, redis
import db.mongodb as mgdb
from utils.time import getTime, formatTimestamp, now_format
from utils.security import md5
from utils.logger import loggerMirror as logger
from config.config import MIRROR_PROXY, PATH_NODEJS

def generate(urlid):
    row = mgdb.spiderurl_getbyid(urlid)
    if not row:
        return {'status':0, 'msg':'spider_url[%s] is not exists' % urlid, 'domirror_urlid':urlid}

    try:
        command = "phantomjs --ignore-ssl-errors=true --proxy=%s %s/mirror.js %s" % (MIRROR_PROXY, PATH_NODEJS, row['url'])
        child = subprocess.Popen(command, shell=True, close_fds=True, bufsize=-1, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        lines = child.stdout.readlines()
        output = getTime('%Y%m%d%H%M%S') + "\t" + command
        processOutputs = []
        for line in lines:
            processOutputs.append(line.decode().strip())
        if child.poll():
            mgdb.spiderurl_save({'status':401}, row['id'])
            logger.debug("failed  %s\n%s\n%s" % (row['url'], command, "\n".join(processOutputs)))
        else:
            mgdb.spiderurl_save({'status':4}, row['id'])
            logger.debug("success %s\n%s\n%s" % (row['url'], command, "\n".join(processOutputs)))
        return {'status':1, 'msg':'mirror ok', 'domirror_urlid':urlid}
    except Exception as e:
        mgdb.spiderurl_save({'status':402, 'error':repr(e)}, row['id'])
        logger.error("doMirror::" + str(urlid) + "::" + repr(e))
        return {'status':1, 'msg':repr(e), 'domirror_urlid':urlid}

