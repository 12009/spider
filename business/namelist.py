# -*- coding: utf-8 -*-
from __future__ import absolute_import
import json
from urllib.parse import urlparse
from utils.url import getDomainMain, getDomainNoPort
from utils.time import getTime, formatTimestamp, now_format
from utils.logger import logger
from common import db

#def link_save(params = None):
#    '''保存外链名单'''
#    #参数错误
#    if params['scope'] == 'gloal': params['domain'] = '__all__'
#    if params['list_type'] not in ['white', 'black']: return False
#    if params['status'] not in [-1, 1]: return False
#
#    if params['status'] == 1:
#        #增加或保存
#        nlLink = session.query(NamelistLink).filter(
#            NamelistLink.domain==params['domain'], 
#            NamelistLink.list_type==params['list_type'], 
#            NamelistLink.url==params['url']
#        ).first()
#        if not nlLink:
#            nlLink = NamelistLink(**{
#                'domain': params['domain'],
#                'primary_domain': getDomainMain(params['domain']),
#                'list_type': params['list_type'],
#                'scope': params['scope'],
#                'url': params['url'],
#                'status': params['status'],
#            });
#            session.add(nlLink)
#            session.commit()
#        return nlLink.id
#
#    elif params['status'] == -1:
#        #删除
#        nlLink = session.query(NamelistLink).filter(
#            NamelistLink.domain==params['domain'], 
#            NamelistLink.list_type==params['list_type'], 
#            NamelistLink.url==params['url']
#        ).first()
#        if nlLink:
#            session.delete(nlLink)
#            session.commit()
#        return True
#    else:
#        return False

#def link_getbydomain(listType = '', domain = None):
#    '''根据域名查询名单'''
#    rows = session.query(NamelistLink).filter(
#        NamelistLink.domain==domain, 
#        NamelistLink.list_type==listType).all()
#    nlLinks = []
#    if rows:
#        for row in rows:
#            tmp = row.to_dict()
#            tmp['create_at'] = formatTimestamp(tmp['create_at'])
#            tmp['update_at'] = formatTimestamp(tmp['update_at'])
#            del(tmp['id'])
#            nlLinks.append(tmp)
#    return nlLinks

#def link_getglobal(listType = ''):
#    '''查询全局白名单'''
#    rows = session.query(NamelistLink).filter(
#        NamelistLink.scope=='global', 
#        NamelistLink.list_type==listType).all()
#    nlLinks = []
#    if rows:
#        for row in rows:
#            tmp = row.to_dict()
#            tmp['create_at'] = formatTimestamp(tmp['create_at'])
#            tmp['update_at'] = formatTimestamp(tmp['update_at'])
#            del(tmp['id'])
#            nlLinks.append(tmp)
#    return nlLinks

#def link_getbyurl(listType = '', url = None):
#    '''根据URL查询名单'''
#    rows = session.query(NamelistLink).filter(
#        NamelistLink.list_type==listType, 
#        NamelistLink.scope=='domain', 
#        NamelistLink.url==url).all()
#    nlLinks = []
#    if rows:
#        for row in rows:
#            tmp = row.to_dict()
#            tmp['create_at'] = formatTimestamp(tmp['create_at'])
#            tmp['update_at'] = formatTimestamp(tmp['update_at'])
#            del(tmp['id'])
#            nlLinks.append(tmp)
#    return nlLinks

