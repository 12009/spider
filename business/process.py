# -*- coding: utf-8 -*-
from __future__ import absolute_import
import json
from time import time, sleep
from os import remove, getpid
from os.path import basename
from socket import gethostname
from setproctitle import setproctitle

def process_run(name, index):
    eval("process_%s(%s)" % (name, index))

def _checkActive(mongoMq, procKey):
    hostname = gethostname()
    procData = mongoMq['process_list'].find_one({"hostname":hostname, "title": procKey},{"_id":0})
    if procData:
        mongoMq['process_list'].find_and_modify({"hostname":hostname, "title": procKey},{"$set":{"processid": getpid()}}) 
    else:
        return False

def process_spider(index):
    '''蜘蛛'''
    mqkey = 'spider'
    procname = "spider-%s-%s" % (mqkey, index)
    setproctitle(procname)

    from common import mongoMq
    from utils import mq as Mq
    from business.crawler import crawl

    start = time()
    while True:
        #如果停止，退出程序
        if time() - start > 10:
            if not _checkActive(mongoMq, procname[7:]): exit()
            start = time()
        row = Mq.consume('spider')
        if not row: 
            sleep(10)
            continue

        crawl(row)
        Mq.finish(row['id'], 'spider')

def process_mirror(index):
    '''镜像的进程'''
    mqkey = 'mirror'
    procname = "spider-%s-%s" % (mqkey, index)
    setproctitle(procname)
    from common import mongoMq
    from utils import mq as Mq
    import business.mirror as bMirror
    start = time()
    while True:
        #如果停止，退出程序
        if time() - start > 10:
            if not _checkActive(mongoMq, procname[7:]): exit()
            start = time()
        row = Mq.consume('mirror')
        if not row: 
            sleep(10)
            continue
        bMirror.generate(row['id'])
        Mq.finish(row['id'], 'mirror')

def process_notify(index):
    '''蜘蛛'''
    mqkey = 'notify'
    procname = "spider-%s-%s" % (mqkey, index)
    setproctitle(procname)

    from common import mongoMq
    from utils import mq as Mq
    import business.notify as bNotify

    start = time()
    while True:
        #如果停止，退出程序
        if time() - start > 10:
            if not _checkActive(mongoMq, procname[7:]): exit()
            start = time()
        row = Mq.consume('notify')
        if not row: 
            sleep(10)
            continue

        result = bNotify.send(row['id'])
        Mq.finish(row['id'], 'notify')

def process_piping(index):
    '''数据处理'''
    mqkey = 'piping'
    procname = "spider-%s-%s" % (mqkey, index)
    setproctitle(procname)

    from common import mongoMq
    from utils import mq as Mq
    import business.piping as bPiping

    start = time()
    while True:
        #如果停止，退出程序
        if time() - start > 10:
            if not _checkActive(mongoMq, procname[7:]): exit()
            start = time()
        row = Mq.consume('piping')
        if not row: 
            sleep(10)
            continue
        bPiping.piping_all(row['id'])
        Mq.finish(row['id'], 'piping')

def process_snapshot(index):
    '''数据处理'''
    mqkey = 'snapshot'
    procname = "spider-%s-%s" % (mqkey, index)
    setproctitle(procname)

    from common import mongoMq
    from utils import mq as Mq
    from utils.logger import logger
    import business.snapshot as bSnapshot

    start = time()
    while True:
        #如果停止，退出程序
        if time() - start > 10:
            if not _checkActive(mongoMq, procname[7:]): exit()
            start = time()
        row = Mq.consume('snapshot')
        logger.debug("snapshot::::%s" % json.dumps(row))
        if not row: 
            sleep(10)
            continue

        bSnapshot.generate(row)
        Mq.finish(row['id'], 'snapshot')

def process_darklink(index):
    '''数据处理'''
    mqkey = 'darklink'
    procname = "spider-%s-%s" % (mqkey, index)
    setproctitle(procname)

    from common import mongoMq
    from utils import mq as Mq

    start = time()
    while True:
        #如果停止，退出程序
        if time() - start > 10:
            if not _checkActive(mongoMq, procname[7:]): exit()
            start = time()
        row = Mq.consume('darklink')
        if not row: 
            sleep(10)
            continue

        bSnapshot.generate(row)
        Mq.finish(row['id'], 'darklink')

def process_qiniu(index):
    '''快照图片压缩及上传到七牛
    此程序是守护进程，可start/stop/restart
    程序完成两件事：
    1.查找新生成的快照，压缩，移动到七牛上传图片的文件夹
    2.由七牛的程序将文件上传到七牛的服务器
    '''

    mqkey = 'qiniu'
    procname = "spider-%s-%s" % (mqkey, index)
    setproctitle(procname)

    from common import mongoMq
    from utils import mq as Mq
    from utils.logger import logger
    from utils.file import qiniu_upload
    from subprocess import Popen, PIPE, STDOUT
    from config.config import PATH_TMP_SNAPSHOT

    cmdFind = 'find %s -amin +1 -type f' % PATH_TMP_SNAPSHOT
    cmdCompress = 'pngquant -f --ext .png --quality 10 %s' 
    start = time()
    while True:
        #如果停止，退出程序
        if time() - start > 10:
            if not _checkActive(mongoMq, procname[7:]): exit()
            start = time()
        child = Popen(cmdFind, shell=True, close_fds=True, bufsize=-1, stdout=PIPE, stderr=STDOUT)
        output = child.stdout.read().decode()
        output = output.strip()
        if not output: continue
        files = output.split("\n")
        for localfile in files:
            logger.info(cmdCompress % localfile)
            child = Popen(cmdCompress % localfile, shell=True, close_fds=True, bufsize=-1, stdout=PIPE, stderr=STDOUT)
            output = child.stdout.read().decode()
            key = basename(localfile)
            result = qiniu_upload(key, localfile)
            if result: 
                logger.info(result)
                remove(localfile)
        sleep(5)

def process_ckready(index):
    '''
    将数据转入待处理状态
    '''
    mqkey = 'ckready'
    procname = "spider-%s-%s" % (mqkey, index)
    setproctitle(procname)

    from common import mongoMq
    from utils import mq as Mq

    start = time()
    while True:
        #如果停止，退出程序
        if time() - start > 10:
            if not _checkActive(mongoMq, procname[7:]): exit()
            start = time()
        Mq.ready('spider')
        Mq.ready('mirror')
        Mq.ready('piping')
        Mq.ready('notify')
        Mq.ready('snapshot')
        sleep(10)

def process_ckfinish(index):
    '''
    检查数据是否已处理完成
    '''
    mqkey = 'ckfinish'
    procname = "spider-%s-%s" % (mqkey, index)
    setproctitle(procname)

    from common import mongoMq
    from utils import mq as Mq
    import business.task as bTask

    start = time()
    while True:
        #如果停止，退出程序
        if time() - start > 10:
            if not _checkActive(mongoMq, procname[7:]): exit()
            start = time()
        bTask.execute_finish()
        sleep(10)

def process_ckcorrect(index):
    '''
    校正数据
    '''
    mqkey = 'ckcorrect'
    procname = "spider-%s-%s" % (mqkey, index)
    setproctitle(procname)

    from common import mongoMq
    from business.devops import mq_correct

    start = time()
    while True:
        #如果停止，退出程序
        if time() - start > 10:
            if not _checkActive(mongoMq, procname[7:]): exit()
            start = time()
        mq_correct()
        sleep(10)

def process_initexec(index):
    '''校正数据'''
    mqkey = 'initexec'
    procname = "spider-%s-%s" % (mqkey, index)
    setproctitle(procname)

    from common import db, mongoMq
    import business.task as bTask

    start = time()
    while True:
        #如果停止，退出程序
        if time() - start > 10:
            if not _checkActive(mongoMq, procname[7:]): exit()
            start = time()
        rows = db.fetchall("select id from task_execute where status=0 order by id asc");
        for row in rows: bTask.execute_init(row['id'])
        sleep(10)


def process_scheduler(index):
    '''校正数据'''
    mqkey = 'scheduler'
    procname = "spider-%s-%s" % (mqkey, index)
    setproctitle(procname)

    from common import mongoMq
    from aps import ApsCheckDb

    start = time()
    while True:
        #如果停止，退出程序
        if time() - start > 10:
            if not _checkActive(mongoMq, procname[7:]): exit()
            start = time()
        ApsCheckDb()
        sleep(10)

