#!/usr/bin/env python  
'''
通用守护进程类 
1.启动时需要设置5个参数，即pidfile,stdin,stdout,stderr,proctitle
2.任务结束时，需要找到pidfile文件，并删除
3.系统信号导致结束时，要绑定事件
4.系统重启时，要重新执行调用的函数
5.SIGNKILL, SIGNSTOP 两个信号无法被捕获到，因此会产生程序结束，即没有删除pidfile的问题
6.易用灵活, module比类好

使用方式: 
config = {
    'pidfile' : '/tmp/daemon.pid',
    'stdin' : '/dev/null',
    'stdout' : '/tmp/daemon_stdout.log',
    'stderr' : '/tmp/daemon_error.log',
    'run': main
    'clear': clear
    'kwargs': {}
}
Daemon.start(config)
Daemon.stop(config)
Daemon.restart(config)
'''

import sys
import os
import time  
import atexit  
import setproctitle
from sys import exit
from signal import SIGTERM
from subprocess import Popen, PIPE, STDOUT

def _verifyConfig(cfg):
    stdin = cfg['stdin'] if 'stdin' in cfg.keys() else '/dev/null'
    stdout = cfg['stdout'] if 'stdout' in cfg.keys() else '/tmp/daemon_stdout.log'
    stderr = cfg['stderr'] if 'stderr' in cfg.keys() else '/tmp/daemon_stderr.log'
    pidfile = cfg['pidfile'] if 'pidfile' in cfg.keys() else '/tmp/daemon.pid'
    procname = cfg['procname'] if 'procname' in cfg.keys() else ''
    run = cfg['run'] if 'run' in cfg.keys() else None
    clear = cfg['clear'] if 'clear' in cfg.keys() else None
    kwargs = cfg['kwargs'] if 'kwargs' in cfg.keys() else {}
    return {
        'stdin':stdin,
        'stdout':stdout,
        'stderr':stderr,
        'pidfile':pidfile,
        'procname':procname,
        'run':run,
        'clear':clear,
        'kwargs': kwargs
    }

def _daemonize(cfg):
    '''设置系统环境，将进程托管给系统进程'''
    try:  
        pid = os.fork()
        if pid > 0:
            # 退出第一个父进程
            exit(0)
    except OSError as e:  
        sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))  
        exit(1)

    # 与当前环境解藕
    os.chdir("/")
    os.setsid()
    os.umask(0)

    # 生成子进程
    try:  
        pid = os.fork()  
        if pid > 0:  
            # 父进程退出，子进程托管给进程ID为1的系统进程
            exit(0)  
    except OSError as e:  
        sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))  
        exit(1)  

    # 重定向标准输出到文件
    sys.stdout.flush()
    sys.stderr.flush()
    si = open(cfg['stdin'], 'r')
    so = open(cfg['stdout'], 'a+')
    se = open(cfg['stderr'], 'a+')
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())
    #if type(sys.stderr) is file:
    #    os.dup2(se.fileno(), sys.stderr.fileno())


    #  把进程ID写入 pidfile  文件
    #atexit.register(_delpid)  
    pid = str(os.getpid())  
    open(cfg['pidfile'], 'w+').write("%s\n" % pid)

def start(config):
    '''启动守护进程'''
    cfg = _verifyConfig(config)

    cmdExists = 'ps -ef | grep %s | grep -v grep | wc -l' % cfg['procname']
    child = Popen(cmdExists, shell=True, close_fds=True, bufsize=-1, stdout=PIPE, stderr=STDOUT)
    output = int(child.stdout.read().decode().strip())
    isDoing = True if output else False

    # 如果进程已经运行，查看进程ID文件
    try:
        pf = open(cfg['pidfile'], 'r')
        pid = int(pf.read().strip())
        pf.close()
    except IOError as e:
        pid = None

    #如果是 kill -9 或 kill -19 导致的程序结束，则进程ID不会清除，这里予以修正
    if pid and not isDoing:
        os.remove(cfg['pidfile'])
        pid = None

    if pid:
        message = "pidfile %s is running"  
        sys.stderr.write(message % pid)
        exit(1)

    # 开始设置守护进程环境
    _daemonize(cfg)
    setproctitle.setproctitle(cfg['procname'])
    # 处理信号
    #_signal()
    #执行的入口函数
    if cfg['run']: cfg['run'](cfg['kwargs'])

def stop(config):
    '''终止守护进程'''
    cfg = _verifyConfig(config)
    # 从 pidfile 文件中获取进程 ID
    try:
        pf = open(cfg['pidfile'], 'r')
        pid = int(pf.read().strip())
        pf.close()
    except IOError as e:  
        pid = None  

    if not pid:  
        return sys.stdout.write("process is not running!\n")  

    #执行的入口函数
    if cfg['clear']: cfg['clear']()

    # 根据 pid 杀死进程
    try:  
        while 1:  
            os.kill(pid, SIGTERM)  
            time.sleep(0.1)
    except OSError as err:  
        if str(err).find("No such process") > 0:
            if os.path.exists(cfg['pidfile']):  
                os.remove(cfg['pidfile'])  
            message = "stop pidfile %s success\n"  
            sys.stdout.write(message % cfg['pidfile'])
        else:
            message = "stop pidfile %s failed, %s\n"
            sys.stderr.write(message % (cfg['pidfile'], repr(err)))
            exit(1)

def restart(config):
    '''重新启动进程'''
    stop(config)
    start(config)

#def _signal():
#    signal.signal(signal.SIGHUP, stop)
#    signal.signal(signal.SIGINT, stop)
#    signal.signal(signal.SIGQUIT, stop)
#    signal.signal(signal.SIGTERM, stop)

