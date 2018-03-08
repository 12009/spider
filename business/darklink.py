# coding: utf-8

from config.config import DB_PG_URL_SQL
from sqlalchemy import create_engine
engine = create_engine(DB_PG_URL_SQL)
connection = engine.connect()

def black_add(url):
    result = [(row['name'],)for row in url]
    sql = 'insert into dk_black_list(domain) values(%s)'
    result = connection.execute(sql,result)
    if result:return True
    else:return False
def white_add(url):
    result = [(row['name'],row['type'])for row in url]
    sql = 'insert into dk_white_list(domain,scope) values(%s,%s)'
    result = connection.execute(sql,result)
    if result:return True
    else:return False
def filterword_add(url):
    result = [(row['name'],row['type'],row['level'],)for row in url]
    sql = 'insert into sys_filterword(name,type,level) values(%s,%s,%s)'
    result = connection.execute(sql, result)
    if result:return True
    else:return False
def black_del(url):
    result = [(row['name'],)for row in url]
    sql = "delete from dk_black_list where domain=%s"
    result = connection.execute(sql,result)
    if result:return True
    else:return False
def white_del(url):
    result = [(row['name'],)for row in url]
    sql = 'delete from dk_white_list where domain=%s'
    result = connection.execute(sql,result)
    if result:return True
    else:return False
def filterword_del(url):
    result = [(row['name'],)for row in url]
    sql = 'delete from sys_filterword where name=%s'
    result = connection.execute(sql,result)
    if result:return True
    else:return False
