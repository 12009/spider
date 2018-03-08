# -*- coding: utf-8 -*-
import re
from utils.url import isUrl, extension, getDomainMain
from utils.file import read
from utils.security import rsaEncrypt, rsaDecrypt
from db.base import db
# from business.task import addTask, startTask

#result = db.insert('spider_url', {'url':'http://www.ifeng.com/'})
#print(result)

result = db.stopTask(13)

#data = {
#    'start_url':'http://www.ifeng.com',
#    'app_id': 1,
#    'limit_depth': 1,
#    'limit_total': 5000,
#    'limit_time': 0,
#    'limit_subdomain': 1,
#    'limit_noimage': 0,
#    'limit_js':0,
#    'source_ip':'',
#    'proxies':'',
#    'crontab':'* * * * *',
#}
#taskid = addTask(data)
#print(taskid)
#taskid=8
#result = startTask(taskid)
#print(result)

#url = 'http://ifeng.com/xxx'
#print(isUrl(url))

#content = read('/data/wwwpython/scrapy/ydspider/keys/id_rsa')
#print(content)

#idRsa = read('/data/wwwpython/scrapy/ydspider/keys/private_key.pem')
#idRsaPub = read('/data/wwwpython/scrapy/ydspider/keys/public_key.pem')
#ciphertext = rsaEncrypt("hello", idRsaPub)
#print('加密后密文：')
#print(ciphertext)
#originaltext = rsaDecrypt(ciphertext, idRsa)
#print('解密后明文：')
#print(originaltext)


#import rsa  
##rsa加密  
#def rsaEncrypt(str):  
#    #生成公钥、私钥  
#    (pubkey, privkey) = rsa.newkeys(512)  
#    print(pubkey)
#    print(privkey)
#    #明文编码格式  
#    content = str.encode('utf-8')  
#    #公钥加密  
#    crypto = rsa.encrypt(content,pubkey)  
#    return (crypto,privkey)  
  
  
##rsa解密  
#def rsaDecrypt(str,pk):  
#    #私钥解密  
#    content = rsa.decrypt(str,pk)  
#    con=content.decode('utf-8')  
#    return con  


#(a, b) = rsaEncrypt("hello")
#print('加密后密文：')
#print(a)
#content = rsaDecrypt(a, b)
#print('解密后明文：')
#print(content)

#print(extension('http://www.ifeng.com/a.js'))
#print(extension('http://www.ifeng.com/'))

#sourceUrl = 'http://www.ifeng.com/c/i.php?c=1'
#url = '..///////a.php'
#print("sourceUrl: " + sourceUrl)
#print("url: " + url)
#result = formatRelativeUrl(sourceUrl, url)
##result = changeUrl(sourceUrl, url)
#print(result)

#domain = 'www.ifeng.com.cn'
#print(getDomainMain(domain))

