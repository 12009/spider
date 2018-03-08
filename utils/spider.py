#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import json
from html import unescape
import platform
from utils.url import formatRelativeUrl, isUrl
from urllib.parse import urlparse, urlunparse
from utils.logger import loggerSpider as logger

def checklogout(url, content = ""):
    content = content.replace(" ","")
    if content == "":
        return False

    list1 = ['logout','exit','tuichu','quit','abort','withdraw']
    list2 = []
    temp = u"注销"
    list2.append(temp.encode('utf8'))
    list2.append(temp.encode('gb2312'))
    temp = u"退出"
    list2.append(temp.encode('utf8'))
    list2.append(temp.encode('gb2312'))

    parse = urlparse(url)
    path = parse[2]

    for row in list1:
        if path.find("%s." % (row)) >= 0:
            return True

    for row in list2:
        if content.find(str(row)) == 0:
            return True

    return False

def parseCharset(content):
    match = re.findall(r"<meta(.+?)charset(.*?)=(.+?)\"",content,re.I)
    if match and len(match) > 0:
        row = match[0][2]
        row = row.replace(" ","")
        row = row.lower()
        if row[0] == '"' or row[0] == "'":
            return row[1:]
        else:
            return row
    return False

# 从 JS 中解析 URL
def parseUrlFromJs(url, content):
    urls = []
    if content.find('url') >= 0:
        match = re.findall(r"[^_]url(\s*)=(\s*)(\"|')(.+?)\3",content,re.I)
        for row in match:
            urls.append(row[3])

    if content.find('.href') >= 0:
        match = re.findall(r"\.href(\s*)=(\s*)(\"|')(.+?)\3",content,re.I)
        for row in match:
            urls.append(row[3])

    if content.find('window.open') >= 0:
        match = re.findall(r"window\.open(\s*)\((\s*)('|\")(.+?)\3(,?)",content,re.I)
        for row in match:
            urls.append(row[3])

    if content.find('window.navigate') >= 0:
        match = re.findall(r"window\.navigate(\s*)\((\s*)('|\")(.+?)\3",content,re.I)
        for row in match:
            urls.append(row[3])

    if content.find('.location') >= 0:
        match = re.findall(r"\.location(\s*)=(\s*)('|\")(.+?)\3",content,re.I)
        for row in match:
            urls.append(row[3])

    if content.find('location.replace') >=0 or content.find('location.assign') >=0:
        match = re.findall(r"location\.(replace|assign)(\s*)\((\s*)('|\")(.+?)\4",content,re.I)
        for row in match:
            urls.append(row[4])
    rows = []
    for row in urls:
        if not row:
            continue
        if not isUrl(row):
            row = formatRelativeUrl(url, row)
        rows.append(row)
    return list(set(rows))

# 从内容中解析URL ok
def parseUrlByMatchQuotes(url, content):
    urls = []
    match = re.findall(r"('|\")(http|https)://(.+?)\1",content,re.I)
    for row in match:
        urls.append("%s://%s" % (row[1],row[2]))
    rows = []
    for row in urls:
        if not row:
            continue
        if not isUrl(row):
            row = formatRelativeUrl(url, row)
        rows.append(row)
    return list(set(rows))

# 解析 href ok
def parseHref(url, content):
    urls = []
    if content != '' and (content.find('href') > 0 or content.find('HREF') > 0):
        match = re.findall(r"(\s+)href(\s*)=(\s*)('|\")(.*?)\4(.*?)>(.*?)<",content,re.I|re.DOTALL)
        if len(match) > 0:
            for row in match:
                if row[4] != '':
                    urls.append(row[4])
        match = re.findall(r"(\s+)href(\s*)=(\s*)([\d\w#].*?)(/>|>| )",content,re.I|re.DOTALL)
        if len(match) > 0:
            for row in match:
                urls.append(row[3])
    rows = []
    for row in urls:
        if not row:
            continue
        if not isUrl(row):
            row = formatRelativeUrl(url, row)
        rows.append(row)
    return list(set(rows))

# 解析 src ok
def parseSrc(url, content):
    urls = []
    if content != '' and (content.find('src') >= 0 or content.find('SRC') >= 0):
        match = re.findall(r"src(\s*)=(\s*)('|\")(.*?)\3",content,re.I)
        for row in match:
            if row[3] != '':
                urls.append(row[3])
        match = re.findall(r"src(\s*)=(\s*)([\d\w#].*?)(/>|>| )",content,re.I)
        if len(match) > 0:
            for row in match:
                urls.append(row[2])
    rows = []
    for row in urls:
        if not row:
            continue
        if not isUrl(row):
            row = formatRelativeUrl(url, row)
        rows.append(row)
    return list(set(rows))

def parseForm(url, content):
    parseResult = urlparse(url)
    scheme = parseResult[0]
    domain = parseResult[1]

    url = unescape(url)
    isJs = url.find(".js") != -1
    match = re.findall(r"<(\s*)form(.+?)>(.+?)<(\s*)/(\s*)form(\s*)>",content,re.I|re.DOTALL)
    for row in match:
        method = ''
        action = None
        fields = []

        if row[1].lower().find("action") >= 0:
            temp = re.findall(r"action(\s*)=(\s*)('|\")(.*?)(\3)",row[1],re.I)
            if len(temp) > 0:
                action = temp[0][3].replace(' ','')
            else:
                temp = re.findall(r"action(\s*)=(\s*)(.+?)(\s|$)",row[1],re.I)
                if len(temp) >0:
                    action = temp[0][2]
        else:
            action = url

        if action == None:
            continue

        if isJs:
            m = re.search(r"(['\"])(.*?)(\1)",action.decode('string_escape'))
            if m: action = m.group(2)

        if action == '':
            action = url

        temp = re.findall(r"method(\s*)=(\s*)('|\")(.*?)(\3)",row[1],re.I)
        if len(temp) > 0:
            method = temp[0][3].lower().replace(' ','')
        else:
            temp = re.findall(r"method(\s*)=(\s*)(.+?)(\s|$)",row[1],re.I)
            if len(temp) >0:
                method = temp[0][2].lower()
        if method == '':
            method = 'get'

        input_match = re.findall(r"<(\s*)input(.+?)>",row[2],re.I|re.DOTALL)
        if len(input_match) > 0:
            for input_row in input_match:
                type = ''
                name = ''
                value = ''
                temp = re.findall(r"type(\s*)=(\s*)('|\")(.+?)(\3)",input_row[1],re.I)
                if len(temp) > 0:
                    type = temp[0][3].lower().replace(' ','')
                else:
                    temp = re.findall(r"type(\s*)=(\s*)(.+?)(\s|/|$)",input_row[1],re.I)
                    if len(temp) >0:
                        type = temp[0][2].lower()
                if type == '':
                    type = 'text'

                temp = re.findall(r"name(\s*)=(\s*)('|\")(.+?)(\3)",input_row[1],re.I)
                if len(temp) > 0:
                    name = temp[0][3].replace(' ','')
                else:
                    temp = re.findall(r"name(\s*)=(\s*)(.+?)(\s|/|$)",input_row[1],re.I)
                    if len(temp) >0:
                        name = temp[0][2]

                temp = re.findall(r"value(\s*)=(\s*)('|\")(.*?)(\3)",input_row[1],re.I)
                if len(temp) > 0:
                    value = temp[0][3].replace(' ','')
                else:
                    temp = re.findall(r"value(\s*)=(\s*)(.+?)(\s|/|$)",input_row[1],re.I)
                    if len(temp) >0:
                        value = temp[0][2]

                if type in ['reset','button']:
                    continue
                if name == '':
                    continue
                fields.append({'type':type,'name':name,'value':value})

        select_match = re.findall("<(\s*)select(.+?)>(.+?)<(\s*)/(\s*)select(\s*)>",row[2],re.I|re.DOTALL)
        if len(select_match) > 0:
            for select_row in select_match:
                name = ''
                value = ''
                temp = re.findall(r"name(\s*)=(\s*)('|\")(.+?)(\3)",select_row[1],re.I)
                if len(temp) > 0:
                    name = temp[0][3].replace(' ','')
                temp = re.findall(r"<(\s*)option(.+?)value(\s*)=(\s*)('|\")(.*?)(\5)(.*?)>(.+?)<(\s*)/(\s*)option(\s*)>",select_row[2],re.I)
                if len(temp) > 0:
                    for temp_row in temp:
                        if temp_row[1].find('selected') >= 0 or temp_row[7].find('selected') >= 0:
                            value = temp_row[5].replace(' ','')
                            break
                    if value == '': value = temp[0][5].replace(' ','')
                else:
                    temp = re.findall(r"<(\s*)option(.+?)>(.+?)<(\s*)/(\s*)option(\s*)>",select_row[2],re.I)
                    if len(temp) > 0:
                        for temp_row in temp:
                            if temp_row[1].find('selected') >= 0:
                                value = temp_row[2].strip()
                                break
                        if value == '':
                            value = temp[0][2].strip()
                if name == '':
                    continue
                fields.append({'type':'select','name':name,'value':value})

        area_match = re.findall("<(\s*)textarea(.+?)>(.*?)<(\s*)/(\s*)textarea(\s*)>",row[2],re.I|re.DOTALL)
        if len(area_match) > 0:
            for area_row in area_match:
                name = ''
                value = ''
                temp = re.findall(r"name(\s*)=(\s*)('|\")(.+?)(\3)",area_row[1],re.I)
                if len(temp) > 0:
                    name = temp[0][3].replace(' ','')
                else:
                    temp = re.findall(r"name(\s*)=(\s*)(.+?)(\s|$)",area_row[1],re.I)
                    if len(temp) > 0:
                        name = temp[0][2]
                value = area_row[2].strip()
                if name == '':
                    continue
                fields.append({'type':'textarea','name':name,'value':value})
        #在字段的最后追加一项标识数据来源
        fields.append({'type':'post_data_type', 'name':'form_data',  'value':'reg_parseForms'})

        fullpath = changeUrl(url, action)
        if fullpath == "" or fullpath[0] == '#' or len(fullpath.split("?")) > 2 or fullpath.find('>') >= 0 or fullpath.find('<') >= 0 or fullpath.find('{') >= 0 or fullpath.find('}') >= 0 or fullpath.find('\\') >= 0 or fullpath.find('+') >= 0 or fullpath.find('|') >= 0 or fullpath.find(',') >=0 :
            continue
        parse = urlparse(fullpath)
        if  parse[0] != 'http' and parse[0] != 'https':
            continue

        if method != 'post':
            paramslist = []
            for f in fields:
                paramslist.append(f['name']+'='+f['value'])
            params = '&'.join(paramslist)
            return (fullpath + '?' + params, 'get', '', url)
        else:
            return (fullpath, 'post', fields, url)

