#!/usr/bin/env /data/pyenv/env35/bin/python
import json
import socket
import logging
from logging.config import dictConfig as logDictConfig
from time import sleep
from subprocess import Popen, PIPE, STDOUT, DEVNULL

logDir='/tmp/spider/log'
config = {
  'pybin': '/data/pyenv/env35/bin/python',
  'spiderDir': '/data/wwwpython/spider',
  'server': {'host': '127.0.0.1', 'port': 60080},
  'log' : {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
      "default": {
        "format": "%(asctime)s %(levelname)s %(name)s %(filename)s[line:%(lineno)d] %(message)s",
        "datefmt": "%Y-%m-%d %H:%M:%S",
      }
    },
    "handlers": {
      "console": {"class": "logging.StreamHandler", "level": "DEBUG", "formatter": "default", "stream": "ext://sys.stdout"},
      "ctlserver": {"class": "logging.FileHandler", "level": "DEBUG", "formatter": "default", "filename": "%s/ctl_server.log" % logDir, "encoding": "utf8"},
      "ctlclient": {"class": "logging.FileHandler", "level": "DEBUG", "formatter": "default", "filename": "%s/ctl_client.log" % logDir, "encoding": "utf8"}
    },
    "loggers": {
      "ctlserver": {"level": "DEBUG", "handlers": ["console", "ctlserver"], "propagate": "no"},
      "ctlclient": {"level": "DEBUG", "handlers": ["console", "ctlclient"], "propagate": "no"}
    },
    "root": {"level": "DEBUG", "handlers": ["console"]}
  }
}

result = logDictConfig(config['log'])
logger = logging.getLogger('ctlclient')


def beat(process):
  try:
    #process = {'action':'beat', 'hostname':'spider-prod-master', 'process':['spider-1']}
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((config['server']['host'], config['server']['port']))
    sock.sendall(json.dumps(process).encode('UTF-8'))
    response = sock.recv(4096).decode('UTF-8')
    sock.close()
    return response
  except ConnectionRefusedError as e:
    logger.error("the server is not connected")
    return False

def process_info():
  cmd = "ps -ef | grep spider- | grep -v grep | awk '{print $8}'"
  child = Popen(cmd, shell=True, close_fds=True, bufsize=-1, stdout=PIPE, stderr=STDOUT, cwd=config['spiderDir'])
  output = child.stdout.read().decode().strip()
  process = []
  for line in output.split("\n"):
    line = line.strip()
    tmp = line.split('-')
    if len(tmp) not in (2, 3): continue
    if tmp[0] != 'spider': continue
    if tmp[1] not in ['master', 'spdier', 'mirror', 'piping', 'notify', 'snapshot']: continue
    process.append(line)
  return process

def check_master():
  cmd = "ps -ef | grep spider-master | grep -v grep | wc -l"
  Popen(cmd, shell=True, close_fds=True, bufsize=-1, stdout=PIPE, stderr=STDOUT)
  child = Popen(cmd, shell=True, close_fds=True, bufsize=-1, stdout=PIPE, stderr=STDOUT)
  output = child.stdout.read().decode().strip()
  logger.debug("check_master:::: %s" % output)
  return int(output)

def start_master():
  cmd = "nohup %s ctl.py &" % config['pybin']
  logger.debug("start_master:::%s" % cmd)
  Popen(cmd, shell=True, close_fds=True, bufsize=-1, stdout=PIPE, stderr=STDOUT, cwd=config['spiderDir'])

def stop_master():
  cmd = "ps -ef | grep spider-master | grep -v grep | awk '{print $2}' | xargs kill -9"
  logger.debug("stop_master:::%s" % cmd)
  Popen(cmd, shell=True, close_fds=True, bufsize=-1, stdout=PIPE, stderr=STDOUT, cwd=config['spiderDir'])

while True:
  process = process_info()
  response = beat({'action':'beat', 'hostname':socket.gethostname(), 'process':process})
  if response == 'running':
      if not check_master(): start_master()
  elif response == 'ok':
      if check_master(): stop_master()
  else:
      pass
  sleep(10)

