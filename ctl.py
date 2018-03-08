# -*- coding: utf-8 -*-
'''
例7.4：使用多个进程池
'''
import json
import socket
import logging
import threading
from time import sleep
import multiprocessing
from db.base import getMongo
from utils.logger import logger
from setproctitle import setproctitle
from subprocess import Popen, PIPE, STDOUT, DEVNULL
from multiprocessing import Process, Manager, log_to_stderr, get_logger
from config.config import PATH_ROOT, PATH_TMP, PATH_TMP_LOG, MONGO_URL
from business.process import process_run
from utils.time import now_format
import click,signal,subprocess,os

pListKey = 'process_list'
pConfigKey = 'process_config'
hostname = socket.gethostname()
mongoMq = getMongo(MONGO_URL, 'mq')
funcs = ['spider', 'mirror', 'piping', 'notify', 'snapshot', 'qiniu', 'ckready', 'ckfinish', 'ckcorrect', 'initexec', 'scheduler']


class CtlMainThread(threading.Thread):

    def __init__(self):
        super(CtlMainThread, self).__init__()

    def run(self):
        #log_to_stderr()
        #logger = multiprocessing.get_logger().setLevel(logging.INFO)
        if hostname[-6:] != 'master':
            return False

        #进程启动时，初始化数据
        while True:
            processes = []
            removes = []
            exists = []
            for row in mongoMq[pConfigKey].find({}, {"_id":0}):
                hostnameT = row['hostname']
                status = row['status']
                titles = []
                for key ,value in row.items():
                    if key in ['hostname', 'status']: continue
                    for index in list(range(value)):
                        title = "%s-%s" % (key, index + 1)
                        processes.append({
                            "hostname": hostnameT,
                            "title": title,
                            "processid": 0,
                            "mqkey": key,
                            "status": status,
                            "mqid": 0,
                            "update": now_format().replace('-','').replace(':','').replace(' ','')
                        })
                        titles.append(title)

                titleExists = [i['title'] for i in mongoMq[pListKey].find({"hostname": hostnameT}, {'_id':0})]
                for title in list(set(titleExists) - set(titles)):
                    removes.append({'hostname':hostnameT, 'title':title})

            for row in processes:
                proc = mongoMq[pListKey].find_one({"hostname": row['hostname'], "title": row['title']})
                if proc:
                    mongoMq[pListKey].find_and_modify(
                        {"hostname": row['hostname'], "title": row['title']},
                        {'$set': {"status": row['status'], "update": row['update']}}
                    )
                else:
                    mongoMq[pListKey].insert(row)
            for row in removes:
                mongoMq[pListKey].find_and_modify({'hostname': row['hostname'],'title': row['title']}, {'$set':{'status': 'disable'}})
            sleep(10)

class CtlClientThread(threading.Thread):

    def __init__(self):
        super(CtlClientThread, self).__init__()

    def run(self):
        #log_to_stderr()
        #logger = multiprocessing.get_logger().setLevel(logging.INFO)

        #进程启动时，初始化数据
        while True:
            sleep(10)
            #根据已有的进程，修改进程状态
            cmd = "ps -ef | grep spider | grep -v grep | awk '{print $8}'"
            Popen(cmd, shell=True, close_fds=True, bufsize=-1, stdout=PIPE, stderr=STDOUT, cwd=PATH_ROOT)
            child = Popen(cmd, shell=True, close_fds=True, bufsize=-1, stdout=PIPE, stderr=STDOUT, cwd=PATH_ROOT)
            output = child.stdout.read().decode().strip()
            if not output: continue

            runing = []
            lines = output.split("\n")
            for line in lines:
                action = line.strip()[7:]
                runing.append(action)

            #启动子进程
            for row in mongoMq[pListKey].find({"hostname": hostname}, {'_id':0}):
                if row['title'] in runing: continue
                if row['status'] != 'enable': continue
                titleTmp = row['title'].split('-')
                Process(target=process_run, args=(titleTmp[0], titleTmp[1], )).start()


if __name__ == '__main__':
    setproctitle('spider-master')
    CtlMainThread().start()
    CtlClientThread().start()


# 根据进程名获取进程id
# def get_process_id(pid):
#     child = subprocess.Popen(['pgrep', '-f', pid], stdout=subprocess.PIPE, shell=False)
#     response = child.communicate()[0]
#     return [int(pid) for pid in response.split()]
#
# if __name__ == '__main__':
#     setproctitle('spider-master')
#     CtlMainThread().start()
#     CtlClientThread().start()
#     pid = get_process_id('spider-master')
#     if pid:os.waitpid(-1,0)
#
#
# # 定义信号处理函数
# def signalHandler():
#     os.wait()
# signal.signal(signal.SIGTERM, signalHandler)
#
#
# @click.group()
# def cli():
#     pass
#
#
# # 开启进程
# @click.command()
# def proc_start():
#     setproctitle('spider-master')
#     CtlMainThread().start()
#     CtlClientThread().start()
#     click.echo('The server process is starting')
#
#
# # 停止进程
# @click.command()
# def proc_stop():
#     pid = get_process_id('spider-master')
#     if pid:
#         os.killpg(os.getpgid(pid[0]), signal.SIGTERM)
#         click.echo('The server process is stopped')
#     else:
#         click.echo('The server process has been stopped')
#
# # 重启进程
# @click.command()
# def proc_restart():
#     pid = get_process_id('spider-master')
#     if pid:
#         os.killpg(os.getpgid(pid[0]), signal.SIGUSR1)
#         setproctitle('spider-master')
#         CtlMainThread().start()
#         CtlMainThread().wait()
#         CtlClientThread().start()
#         click.echo('The server process is restarting')
#     else:
#         setproctitle('spider-master')
#         CtlMainThread().start()
#         CtlClientThread().start()
#         click.echo('The server process is restarting')
#
#
# # 添加子命令
# cli.add_command(proc_start)
# cli.add_command(proc_stop)
# cli.add_command(proc_restart)
#
# if __name__ == '__main__':
#     cli()


