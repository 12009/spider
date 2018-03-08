# -*- coding: utf-8 -*-

import re
import rsa
import base64
# from utils.file import read
import hashlib

#rsa加密
def rsaEncrypt(originaltext, publicKey):
    #明文编码格式
    content = originaltext.encode('utf-8')
    #公钥加密
    pubKey = rsa.PublicKey.load_pkcs1(publicKey)
    return base64.b64encode(rsa.encrypt(content, pubKey))

#rsa解密
def rsaDecrypt(ciphertext, privateKey):
    #私钥解密
    priKey = rsa.PrivateKey.load_pkcs1(privateKey)
    content = rsa.decrypt(base64.b64decode(ciphertext), priKey)
    return content.decode('utf-8')

#md5加密算法
def md5(raw = None):
    if type(raw) == bytes:
        return hashlib.md5(raw).hexdigest()
    else:
        return hashlib.md5(raw.encode("utf8")).hexdigest()

#sha256加密算法
def sha256(raw = None):
    return hashlib.sha256(raw).hexdigest()

#sha512加密算法
def sha512(raw = None):
    return hashlib.sha512(raw).hexdigest()

# 检测是否为base64编码
def checkUrlBase64(raw):
    try:
        if len(raw) > 20 and re.match(b'^[A-Za-z0-9_-+]*={0,2}$', s):
            return True
        else:
            return False
    except Exception as e:
        return False

