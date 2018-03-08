# -*- coding: utf-8 -*-

import urllib
from utils.spider2 import *
from bs4 import BeautifulSoup

#url = "http://www.ifeng.com/"
url = "http://local.com/index.html"
#url = "http://fashion.ifeng.com/a/20170323/40198542_0.shtml#p=1"
#body = urllib.request.urlopen(url).read()
##print(body)
#page = body.decode()
#p = page[:page.find('<script type="text/javascript">')] + page[page.find('</script>')+9:]
#print(p)

##执行事件处理，抓取URL
#model = eventModel(url, body.decode())
#urls = model.start()
#print(urls)

#pd = PageParser(body)
#pd.handleAllTag()
##eventList, elementTag, elementType, selector, fillTag = pd.getResult()
#print(pd.getResult())

#soup = BeautifulSoup(body, 'lxml')
#allTags = soup.findAll(True)

#result = parseHref(url)
result = parseForms(url)
#result = parseEvent(url)
print(result)

#result = parseMouseEvent(url)
#print(result)


