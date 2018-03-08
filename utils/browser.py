#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
from utils.file import write, read
from subprocess import Popen, PIPE, STDOUT
from utils.logger import loggerSpider as logger
from config.config import PATH_NODEJS, PATH_TMP_CODE, PATH_TMP_SNAPSHOT

def snapshot_view(url, filename, words):
    cmd = 'phantomjs %s/snapshot_view.js %s %s %s' % (PATH_NODEJS, url, filename, words)
    logger.debug(cmd)
    child = Popen(cmd, shell=True, close_fds=True, bufsize=-1, stdout=PIPE, stderr=STDOUT)
    output = child.stdout.read().decode()
    if output == 'fail':
        logger.error('snapshot_view fail::::%s' % cmd)
        return False
    return output

def snapshot_code(filename, code, words):
    codefile = '%s/%s' % (PATH_TMP_CODE, filename.replace('.png', '.html'))
    snapshot = '%s/%s' % (PATH_TMP_SNAPSHOT, filename)
    write(codefile, code)
    cmd = 'phantomjs %s/snapshot_code.js %s %s %s' % (PATH_NODEJS, codefile, snapshot, words)
    logger.debug(cmd)
    child = Popen(cmd, shell=True, close_fds=True, bufsize=-1, stdout=PIPE, stderr=STDOUT)
    output = child.stdout.read().decode()
    if output == 'fail': 
        logger.error('snapshot_code fail::::%s' % cmd)
        return False
    return json.loads(output)


def parse_darklink(url = None):
    '''解析暗链'''
    try:
        cmd = 'phantomjs %s/safe_darklink.js %s' % (PATH_NODEJS, url)
        child = Popen(cmd, shell=True, close_fds=True, bufsize=-1, stdout=PIPE, stderr=STDOUT)
        output = child.stdout.read().decode().strip()
        # logger.info('parse_darklink::::%s::::%s' % (url, output))
        if output != 'fail': return json.loads(output)
        # logger.info('parse_darklink fail::::%s' % cmd)
        return False
    except Exception as e:
        logger.exception(e)
        return False

def _get_jobs(self, *conditions):

    for row in self.engine.execute(selectable):
        try:
            jobs.append(self._db_to_job(row))
        except:
            self._logger.exeception('Unable to restore job "job"')

