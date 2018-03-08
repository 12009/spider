# -*- coding: utf-8 -*-

import re
from urllib.parse import urlparse, urljoin, urlunparse

def isUrl(url):
    if 'javascript:' in url: return False

    pattern = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    return pattern.match(url)

#获取域名
def getDomain(url = None):
    return urlparse(url)[1]

#获取域名，不包括端口
def getDomainNoPort(url = None):
    return urlparse(url)[1].split(':')[0]

#获取主域名
def getDomainMain(domain):
    fields = domain.split('.')
    domainLevel2 = '.'.join(fields[-3:])
    domainLevel1 = '.'.join(fields[-2:])
    topDomainsSpecial = ['co.in', 'firm.in', 'gen.in', 'ind.in', 'net.in', 'org.in',
        'com.cn', 'gov.cn', 'net.cn', 'org.cn',                        'com.ag', 'net.ag', 'org.ag', 
        'co.nz', 'net.nz', 'org.nz',                                   'com.tw', 'idv.tw', 'org.tw',
        'co.uk', 'me.uk', 'org.uk',                                    'com.co', 'net.co', 'nom.co',
        'com.es', 'nom.es', 'org.es',                                  'com.br', 'net.br', 
        'com.bz', 'net.bz',                                            'co.jp', 'com.mx'
    ]
    return domainLevel2 if domainLevel1 in topDomainsSpecial else domainLevel1

def extension(url = None):
    #从path中获取文件后缀
    path = urlparse(url)[2]

    #如果路径为空，返回False
    if not path:
        return ''

    #没有取到文件名，返回False
    filename = path.split('/')[-1]
    if not filename:
        return ''

    #文件名中没有.，返回False
    if not path.find('.'):
        return ''

    extension = filename.split('.')[-1].lower()
    if extension in [
            'zip',
            'jpg', 'gif', 'png', 
            'php', 'jsp', 'asp', 
            'js', 'css', 'json'
            ]:
        return extension
    else:
        return 'html'

def patternPost(parameters):
    '''post请求参数模式'''
    try:
        paramsList = []
        for row in parameters:
            if row['name'] != 'submit':
                paramsList.append(row['name'])
        paramsList.sort()
        paramsList = list(set(paramsList))
        params = []
        needhandleNum = False
        for k in paramsList:
            params.append("%s=%s" %(k,'v'))
        return '&'.join(params)
    except Exception as e:
        logger.exception(e)


def patternQuery(parameters):
    try:
        paramsList = map(lambda s: s.split('=', 1) if len(s.split('='))>1 else [s[:s.find('=')],''] if s.find('=') != -1  else [s,''],parameters.split('&'))
        #paramsList.sort()
        params = []
        needhandleNum = False
        for k,v in paramsList:
            if not k:
                continue
            params.append("%s=%s" %(k,'v'))
        params.sort()
        return '&'.join(params)
    except Exception as e:
        logger.exception(e)
        return ''

def patternPath(path):
    '''获取路径的模式，以备后续处理'''
    pattern = ""
    #1a[alpha],2i[int]
    flag = ''
    #整个路径的深度
    depth = len(path.split('/'))

    if path.split('/')[-1:][0].find('.'):
        isFile = 1
        currentPath = "/".join(path.split('/')[:-1])
        filename = path.split('/')[-1:][0]
    else:
        isFile = 0
        currentPath = path

    current=0
    patternStr = str(depth) + '-'
    for i in range(len(currentPath)):
        num = ord(currentPath[i])
        if (num >= 65 and num <= 90) or (num >= 97 and num <= 122):   #A-Z a-z
            if flag == '':
                flag = 'a'
                current += 1
            elif flag == 'a':
                current += 1
            elif flag == 'i':
                flag = 'a'
                patternStr = patternStr + str(current) + "i"
                current = 1
        elif num >= 48 and num <= 57:   #0-9 
            if flag == '':
                flag = 'i'
                current += 1
            elif flag == 'i':
                current += 1
            elif flag == 'a':
                flag = 'i'
                patternStr = patternStr + str(current) + "a"
                current = 1
        else:
            if flag == '':
                flag = ''
                patternStr = patternStr + currentPath[i]
            elif flag == 'i':
                flag = ''
                patternStr = patternStr + str(current) + "i" + currentPath[i]
            elif flag == 'a':
                flag = ''
                patternStr = patternStr + str(current) + "a" + currentPath[i]
            current = 0
        if i == len(currentPath) - 1:
            if flag == 'i':
                patternStr = patternStr + str(current) + "i"
            elif flag == 'a':
                patternStr = patternStr + str(current) + "a"
    if isFile:
        patternStr = patternStr + "/" + filename
    return patternStr

# 转换相对URL为绝对URL
def formatRelativeUrl(baseUrl, relativeUrl):
    if relativeUrl[0:4] == 'http':
        return relativeUrl
    if relativeUrl == '':
        return baseUrl
    baseUrlParse = urlparse(baseUrl)
    baseScheme = baseUrlParse[0]
    baseDomain = baseUrlParse[1]
    basePath = baseUrlParse[2]
    if basePath == '' or basePath == '/':
        basePath = '/'

    baseArr = basePath.split('/')[1:]
    if relativeUrl[0:3] == '../':
        relativeArr = relativeUrl.split('/')
        baseArr = baseArr[0:-1]
        for i in range(20):
            if relativeArr[0] != '..' or not baseArr:
                break
            relativeArr = relativeArr[1:]
            baseArr = baseArr[:-1]
        baseArr.extend(relativeArr)
    elif relativeUrl[0:2] == './':
        if len(relativeUrl) > 2:
            baseArr = baseArr[0:-1]
            baseArr.extend(relativeUrl[2])
    elif relativeUrl[0] == '/':
        baseArr = [relativeUrl[1:]]
    else:
        baseArr = baseArr[0:-1]
        baseArr.append(relativeUrl)
    path = '/'.join(baseArr)
    for i in range(5):
        path = path.replace("//",'/')
    return urlunparse((baseUrlParse[0], baseUrlParse[1], path, baseUrlParse[3], baseUrlParse[4], baseUrlParse[5]))

