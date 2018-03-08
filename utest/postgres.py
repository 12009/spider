# -*- coding: utf-8 -*-

import psycopg2
from urllib.request import urlopen
from psycopg2.extras import RealDictCursor
from bs4 import BeautifulSoup

DB_PG_HOST='127.0.0.1'
DB_PG_PORT='5432'
DB_PG_USER='postgres'
DB_PG_PASSWORD='dbadmin'
DB_PG_DATABASE='spider'

def getDbConn():
    return psycopg2.connect(
            host=DB_PG_HOST, 
            port=DB_PG_PORT, 
            user=DB_PG_USER, 
            password=DB_PG_PASSWORD, 
            database=DB_PG_DATABASE
            )

def testInsertJson():
    conn = getDbConn()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    sql = "insert into test_json(content) values(%s)"
    vars = ['{"a":"b", "b":"c"}']
    result = cursor.execute(sql, vars)
    conn.commit()
    conn.close()
    return result

def testInsertJsonb():
    conn = getDbConn()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    sql = "insert into test_jsonb(content) values(%s)"
    vars = ['{"a":"b", "b":"c"}']
    result = cursor.execute(sql, vars)
    conn.commit()
    conn.close()
    return result

def testCreateTableJson():
    conn = getDbConn()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    sql = '''
    create table test_json(
        id serial PRIMARY KEY,
        content json,
        create_at timestamp not null default LOCALTIMESTAMP(0),
        update_at timestamp not null default LOCALTIMESTAMP(0)
    );
    '''
    result = cursor.execute(sql)
    conn.commit()
    conn.close()
    return result

def testCreateTableJsonb():
    conn = getDbConn()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    sql = '''
    create table test_jsonb(
        id serial PRIMARY KEY,
        content jsonb,
        create_at timestamp not null default LOCALTIMESTAMP(0),
        update_at timestamp not null default LOCALTIMESTAMP(0)
    );
    '''
    result = cursor.execute(sql)
    conn.commit()
    conn.close()
    return result

def testCreateTableFullsearch():
    conn = getDbConn()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    #ALTER TABLE full_post ADD IF NOT EXISTS fullindex_body tsvector;
    #UPDATE full_post SET fullindex_body = to_tsvector('testzhcfg', coalesce(body));
    sql = '''
        CREATE TABLE IF NOT EXISTS full_post (
            id SERIAL PRIMARY KEY, 
            url TEXT NOT NULL, 
            body TEXT NOT NULL,
            fullindex_body tsvector
        );
        CREATE INDEX IF NOT EXISTS fullindex_body ON full_post USING gin(fullindex_body);
        CREATE TRIGGER index_body BEFORE INSERT OR UPDATE ON full_post FOR EACH ROW EXECUTE PROCEDURE tsvector_update_trigger(fullindex_body, 'testzhcfg', to_tsvector('testzhcfg', coalesce(body));
    '''
    result = cursor.execute(sql)
    conn.commit()
    conn.close()
    return result

def testInsertFullsearch(url, body):
    conn = getDbConn()
    cursor = conn.cursor(cursor_factory = RealDictCursor)
    sql = 'INSERT INTO full_post (url, body) VALUES (%s, %s)'
    result = cursor.execute(sql, [url, body])
    conn.commit()
    conn.close()
    return result

#testCreateTableJson()
#testInsertJson()

#testCreateTableJsonb()
#testInsertJsonb()

#testCreateTableFullsearch()
#testInsertFullsearch()
url = 'http://www.ifeng.com'
body = urlopen(url).read()
for i in range(1000):
    print("%s    %s" % (i, url))
    testInsertFullsearch(url, body.decode())
soup = BeautifulSoup(body, 'lxml')
tags = soup.findAll('a')
for tag in tags:
    url = tag.get('href')
    print(url)
    if url and url[0:5] == 'http:':
        body = urlopen(url).read()
        for i in range(1000):
            print("%s    %s" % (i, url))
            testInsertFullsearch(url, body.decode())

