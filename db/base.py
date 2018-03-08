# -*- coding: utf-8 -*-
from redis import Redis
from pymongo import MongoClient

def getMongo(mongoUrl, dbname, poolSize = 100):
    conn = MongoClient(mongoUrl, connect=False, maxPoolSize = 100)
    return conn[dbname]

def getRedis(host, port, password, dbIndex = 0):
    return Redis(host=host, port=port, password=password, db=dbIndex)

# def getEngine(dbUrl):
#     return create_engine(dbUrl)

