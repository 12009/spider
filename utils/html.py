# -*- coding: utf-8 -*-

import json
from utils.file import write
from utils.mime import mapMimeFile
from utils.logger import logger
from subprocess import Popen, PIPE, STDOUT
from config.config import PATH_NODEJS, PATH_TMP_CODE, PATH_TMP_SNAPSHOT

def mime2file(contentType):
    if contentType in mapMimeFile.keys():
        filename = mapMimeFile[contentType][0]
        return filename[1:]

def formatCharset(charset = 'UTF-8'):
    if charset == 'ascii':
        charset = 'UTF-8'
    elif charset == 'GB2312':
        charset = 'GBK'
    else:
        charset = 'UTF-8'
    return charset

def parseContentType(contentType, default=None):
    if not contentType:
        return default
    if ';' in contentType:
        return contentType.split(';')[0]
    else:
        return contentType

