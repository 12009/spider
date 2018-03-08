# -*- coding: utf-8 -*-
# 引入排期调度
import threading
from common import db
from time import sleep
from setproctitle import setproctitle
from config.config import DB_PG_URL_SQL
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from utils.dbjobstore import DbJobStore
from utils.logger import logger
import click,signal,subprocess,os

jobstores = {
    'default': DbJobStore(url=DB_PG_URL_SQL)
}
executors = {
    'default': ThreadPoolExecutor(2),
    'processpool': ProcessPoolExecutor(2)
}
job_defaults = {
    'coalesce': False,
    'max_instances': 3
}
#sched = BlockingScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults)
sched = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults)
sched._logger = logger
sched.start()

def ApsCheckDb():
    rows = db.fetchall("select id,crontab from scheduler")
    dbRows = {}
    for row in rows:
        dbRows[row['id']] = row
    rows = sched.get_jobs()
    mRows = {}
    for job in rows:
        mRows[job.id] = job
    tasksNew = list(set(dbRows.keys()) - set(mRows.keys()))
    logger.debug("tasksNew::::%s" % ",".join(tasksNew))
    return True if tasksNew else False

if __name__== '__main__':
    setproctitle('spider-scheduler')
    while True:
        sleep(5)
        ApsCheckDb()

