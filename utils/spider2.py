#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import json
import time
from subprocess import Popen, PIPE, STDOUT
from sys import exit
from os import remove
from utils.file import write, read
from utils.time import getTime
from utils.security import md5
from urllib.parse import urlparse, urljoin
from utils.logger import loggerSpider as logger
from config.config import PATH_NODEJS, PATH_TMP_NODEJS

TEMPLATE_CASPER = "%s/%s" % (PATH_NODEJS, "template_casper.js")
TEMPLATE_JAVASCRIPT = "%s/%s" % (PATH_NODEJS, "template_javascript.js")

'''
windowEvents   :onload, onunload
formEvents     :onchange, onsubmit, onreset, onselect, onblur, onfocus
imageEvents    :onabort
keyboardEvents :onkeydown, onkeypress, onkeyup
mouseEvents    :onclick, ondbclick, onmousedown, onmousemove, onmouseout, onmouseover, onmouseup
fillList       :input, select, textarea
'''

def codeJavascript(func):
    try:
        content = read(TEMPLATE_JAVASCRIPT)
        pattern = re.compile(r'//--' + func + '--\n(.*?)\n//--' + func + '--', re.I | re.M | re.S)
        return pattern.findall(content)[0]
    except Exception as e:
        logger.exception(e)
        return False

def codeCasper(func, params = None):
    try:
        content = read(TEMPLATE_CASPER)
        pattern = re.compile(r'//--' + func + '--\n(.*?)\n//--' + func + '--', re.I | re.M | re.S)
        content = pattern.findall(content)[0]
        if params:
            for (k, v) in params.items():
                content = content.replace('###' + k + '###', v)
        return content
    except Exception as e:
        logger.exception(e)
        return False

def execCasper(content = None):
    try:
        filename = "%s/%s_%s" % (PATH_TMP_NODEJS, getTime('%Y%m%d'), md5(content))
        write(filename, content)
        cmd = 'casperjs ' + filename
        child = Popen(cmd, shell=True, close_fds=True, bufsize=-1, stdout=PIPE, stderr=STDOUT)
        output = child.stdout.read().decode()
        #remove(filename)
        return output
    except Exception as e:
        logger.exception(e)
        return False

def parseHref(url = None, tags = None):
    try:
        jsFunc = 'parseHrefByTags'
        js_parseHrefByTags = codeJavascript('parseHrefByTags')
        casper_create = codeCasper('casper_create')
        casper_then = codeCasper('casper_then', {'jsfunc':jsFunc, 'params':"['a', 'link']"})
        casper_run = codeCasper('casper_run')
        casper_start = codeCasper('casper_start', {'startUrl':'%s' % url})
        content = "%s\n%s\n%s\n%s\n%s" % (js_parseHrefByTags, casper_create, casper_start, casper_then, casper_run)
        output = execCasper(content)
        return json.loads(output)
    except Exception as e:
        logger.exception(e)
        return False

def parseForms(url = None):
    try:
        js_parseForms = codeJavascript('parseForms')
        js_formatRelativeUrl = codeJavascript('formatRelativeUrl')
        casper_create = codeCasper('casper_create')
        casper_parseform = codeCasper('casper_parseform')
        casper_run = codeCasper('casper_run')
        casper_start = codeCasper('casper_start', {'startUrl':'%s' % url})
        content = "%s\n%s\n%s\n%s\n%s\n%s" % (js_parseForms, js_formatRelativeUrl, casper_create, casper_start, casper_parseform, casper_run)
        output = execCasper(content)
        return json.loads(output)
    except Exception as e:
        logger.exception(e)
        return False

#def parseEvent(url = None, tags = None, events=['onclick']):
def captureEvent(url = None, tags = None, events=['onclick']):
    try:
        jsFunc = 'parseEventByTags'
        js_parseEventByTags = codeJavascript(jsFunc)
        casper_create = codeCasper('casper_create')
        casper_then = codeCasper('casper_then', {'jsfunc':jsFunc, 'params':"%s, %s" % (json.dumps(tags, ensure_ascii=False), json.dumps(events, ensure_ascii=False))})
        casper_run = codeCasper('casper_run')
        casper_start = codeCasper('casper_start', {'startUrl':'%s' % url})
        content = "%s\n%s\n%s\n%s\n%s" % (js_parseEventByTags, casper_create, casper_start, casper_then, casper_run)
        output = execCasper(content)
        jsonData = json.loads(output)
        return jsonData['results']
    except Exception as e:
        logger.exception(e)
        return False

def parseMouseEvent(url = None):
    '''解析鼠标事件
    鼠标事件包括: 'onclick', 'ondbclick', 'onmousedown', 'onmousemove', 'onmouseout', 'onmouseover', 'onmouseup'
    '''
    try:
        codes = []
        tags = ['a', 'div', 'span', 'table', 'tr', 'td', 'th', 'button', 'input']
        events = ['onclick', 'ondbclick', 'onmousedown', 'onmousemove', 'onmouseout', 'onmouseover', 'onmouseup']
        rows = captureEvent(url, tags, events)
        eventCodes = []
        for index, row in enumerate(rows):
            # eventRow 示例：
            #{'tag':'div', 'eventName': 'onclick', 'index': 1}
            casper_mouse_event = codeCasper('casper_event', {'tag':row['tag'], 'index':row['index'], 'eventName':row['event']})
            eventCodes.append(casper_mouse_event)
        js_execEvent = codeJavascript('execEvent')
        casper_create = codeCasper('casper_create')
        casper_wait = codeCasper('casper_wait')
        casper_start = codeCasper('casper_start', {'startUrl':'%s' % url})
        casper_output = codeCasper('casper_output')
        casper_run = codeCasper('casper_run')
        content = "%s\n%s\n%s\n%s\n%s\n%s\n%s" % (js_execEvent, casper_create, casper_start, casper_wait, "\n".join(eventCodes), casper_output, casper_run)
        output = execCasper(content)
        return json.loads(output)
    except Exception as e:
        logger.exception(e)
        return False

