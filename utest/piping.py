# -*- coding: utf-8 -*-
import re
from utils.url import isUrl, extension, getDomainMain
from utils.file import read
from utils.security import rsaEncrypt, rsaDecrypt
from db.base import db
from business.piping import piping_errorHttpCode, piping_filterword, piping_keyword, piping_fingerprint

executeid = 79
#result = piping_keyword(executeid)
#print(result)
#result = piping_filterword(executeid)
#print(result)
#result = piping_errorHttpCode(executeid)
#print(result)
# result = piping_fingerprint(executeid)
# print(result)


