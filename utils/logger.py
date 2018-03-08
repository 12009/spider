# --*-- coding: utf-8 --*--
#日志工厂类，用于统一管理所有的日志
#用法示例
__author__ = 'jingwu'

import logging
import logging.config
from config.config import PATH_ROOT

configFile = "%s/config/logger.conf" % PATH_ROOT
logging.config.fileConfig(configFile)
logger = logging.getLogger("root")
loggerSpider = logging.getLogger("spider")
loggerMirror = logging.getLogger("mirror")
loggerNotify = logging.getLogger("notify")
loggerPiping = logging.getLogger("piping")
loggerMq = logging.getLogger("mq")
loggerDb = logging.getLogger("db")

