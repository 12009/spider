#!/usr/bin/env /data/pyenv/env35/bin/python
import json
import logging
import socketserver
from time import sleep, time, strftime, localtime
from logging.config import dictConfig as logDictConfig
from pymongo import MongoClient, ASCENDING, DESCENDING

logDir='/tmp/spider/log'
config = {
  'mongo': 'mongodb://127.0.0.1:27017',
  'pybin': '/data/pyenv/env35/bin/python',
  'server': {'host': '127.0.0.1', 'port': 60080},
  'listen': ('0.0.0.0', 60080),
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
logger = logging.getLogger('ctlserver')

def getMongo(dbname):
  connect = MongoClient(config['mongo'], connect=False)
  return connect[dbname]

mongoMq = getMongo('mq')

mongoMq['process_beat'].insert({
  'hostname':'init',
  'datetime':'',
  'timestamp':'',
  'process':[],
})

class ServerTCPHandler(socketserver.BaseRequestHandler):

  def handle(self):
    clientIp = self.client_address[0]
    raw = self.request.recv(4096).decode('UTF-8')
    logger.debug("receive::::" + raw)
    data = json.loads(raw)
    if ('action' in data.keys() and 'hostname' in data.keys() and 
      'process' in data.keys() and data['action'] == 'beat'):
      item = {
        'hostname': data['hostname'],
        'datetime': strftime('%Y-%m-%d %H:%M:%S', localtime()),
        'timestamp': int(str(time())[0:10]),
        'process': data['process'],
      }
      logger.debug("beat::::" + json.dumps(item))
      mongoMq['process_beat'].insert(item)

    response = 'ok'
    if 'hostname' in data.keys():
      hostname = data['hostname']
      config = mongoMq['process_config'].find_one({'hostname':hostname}, {'_id':0})
      if config:
        #启用状态
        if config['status'] == 'enable': response = 'running'
        #停用状态
        if config['status'] == 'disable': response = 'ok'
    self.request.sendall(response.encode('UTF-8'))

if __name__ == "__main__":
  server = socketserver.TCPServer(config['listen'], ServerTCPHandler)
  server.serve_forever()

