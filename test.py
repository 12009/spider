
# import json
# from utils import mq as Mq
# from utils.file import read
# from db import mongodb as mgdb
# from utils.time import getTime
# from utils.logger import logger
# from business import task as bTask
# from business import mirror as bMirror
# from business import crawler as bCrawler
# from business import process as bProcess
# from business import snapshot as bSnapshot
# from utils.spider_request import spiderRequest
# from common import db, redis, mongoMq, mongoSpider

#-------------------------------------task   test-----------------------------------------------------------
# result = bTask.execute_update_ids_status({'start_at':'2017-07-28 18:50:00'}, [1373], 2)
# print(result)

# taskid = 2
# result = bTask.task_start(taskid)
# print(result)

# ids = [5]
# for id in ids:
#    row = mgdb.spiderurl_getbyid(id)
#    result = bCrawler.crawl(row)
#    print(result)
#
# for i in list(range(100)):
#    result = bTask.execute_init(i)
#    print(result)
#
# result = bTask.execute_init(2631)
# print(result)

#rows = db.fetchall("select id from task_execute where status=0 order by id asc")
#for row in rows: bTask.execute_init(row['id'])

#-------------------------------------crawl  test-----------------------------------------------------------
# from business.crawler import crawl, parseBody
# from config.config import MIRROR_PROXY
#
# row = mgdb.spiderurl_getbyid(254)
# result = crawl(row)

#proxy = {'url':'http://%s' % MIRROR_PROXY}
#row = {'url':'http://www.ifeng.com/', 'method':'GET', 'request_headers':[]}
#requestInfo = spiderRequest(row['url'], row['method'], row['request_headers'])
#print(requestInfo)
#result = parseBody(requestInfo, row)
#print(result)

#-------------------------------------piping test-----------------------------------------------------------
# from business import piping as bPiping
# bPiping.piping_filterword(960)
#
# result = bPiping.piping_all(1)
# print(result)

# result = bPiping.piping_darklink(2)
# print(result)

#---------------------------------------- devops / Mq ------------------------------------------------------
# from business import devops as bDevops
# result = bDevops.init_system()
# print(result)

#result = bDevops.task_clean(1)
#print(result)

#bDevops.clean_all()
#bDevops.mq_clean()

#bDevops.html_to_static(1, 1000)

#batchs = [1,2,3,4,5,6,7,8,9]
#bDevops.mq_resetstats(batchs)
#bDevops.mq_do_dead()
#bDevops.mq_correct()

#result = bTask.execute_finish()
#print(result)

#result = bDevops.mq_checkbybatch(1)
#print(result)

#Mq.ready('spider')
#Mq.ready('mirror')
#Mq.ready('piping')
#Mq.ready('notify')
#Mq.ready('snapshot')

#--------------------------------------------- snapshot ---------------------------------------------------------
#params = {
#    'domain': 'ifeng.com',
#    'list_type': 'black',
#    'scope': 'domain',
#    'status': 1,
#    'url': 'http://ifeng.com/',
#}
#result = bNamelist.link_save(params)
#print(result)

#result = bNamelist.link_getbydomain(listType = 'black', domain = 'www.ifeng.com')
#print(result)