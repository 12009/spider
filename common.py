# -*- coding: utf-8 -*-
from config.config import *
from redis import Redis
from sqlalchemy import create_engine
from db import model as db
from db.base import getMongo, getRedis

redis = getRedis(REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_DB)
mongoMq = getMongo(MONGO_URL, 'mq')
mongoSpider = getMongo(MONGO_URL, 'spider')