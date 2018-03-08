"""
这里是蜘蛛的API接口，接口是REST-FUL风格的，以 RSA形式加密
"""
# -*- coding: utf-8 -*-

import os
import time
import json
import base64
from flask import Flask, session
from flask_restful import Api, Resource, reqparse
import db.mongodb as mgdb
from common import db 
from utils.security import md5
from utils.decorator import verify_token
import business.task as bTask
import business.app as bApp
import business.setting as bSet
import business.notify as bNotify
import business.proxy as bProxy
import business.piping as bPiping
import business.namelist as bNamelist
import business.snapshot as bSnapshot
from utils.logger import logger
from business import darklink
#设置时区
os.environ["TZ"] = "Asia/Shanghai"
time.tzset()

app = Flask(__name__)
app.config['SECRET_KEY']= '123456'
api = Api(app)

#获取token，token的有效期是2小时
class TokenAPI(Resource):

    def get(self, key):
        """
        @apiDescription 根据系统唯一标识符，获取token，每次获取的token有效期是2小时
        @api {get} /token/:key 获取token
        @apiName token
        @apiGroup Token
        @apiVersion 0.1.0
        @apiParam {String} key 系统的唯一标识符
        @apiSuccessExample {Json} 请求成功
            {
                "status": "ok",
                "msg": "ok",
                "data": {
                    "token": "wbsllmigfa4ct0zp4gdd4hx2umpijg4e",
                    "expired": "2017-04-20 15:14:59"
                }
            }
        @apiSuccessExample {Json} 请求失败
            {
                "status": "failed",
                "msg": "not find",
                "data": {}
            }
        """
        result = bApp.getToken_key(key)
        if result:
            return {'status':'ok', 'msg':'ok', 'data':{'token':result['token'], 'expired':result['expired']}}, 200
        else:
            return {'status':'failed', 'msg':'not find', 'data': {}}, 200

class TaskAPI(Resource):

    @verify_token
    def get(self, taskid):
        """
        @apiDescription 获取任务信息
        @api {get} /task/:id 获取任务信息
        @apiName task_executes
        @apiGroup Task
        @apiVersion 0.1.0
        @apiHeader {String} token token
        @apiParam {Number} id 任务ID，如果不存在，则为新建任务，如果存在，则是更新任务
        @apiParam {Number} id 任务ID
        @apiSuccessExample {Json} 请求成功
            {
                "status": "ok",
                "msg": "ok",
                "data": {
                    "app_id": 1,
                    "create_at": "2017-04-13 10:55:00",
                    "crontab": "*/2 * * * *",
                    "id": 1,
                    "limit_depth": 2,
                    "limit_image": 0,
                    "limit_js": 1,
                    "limit_subdomain": 0,
                    "limit_time": 7200,
                    "limit_total": 5000,
                    "notify_url": "http://localhost/",
                    "proxies": "",
                    "site_id": 1,
                    "source_ip": " ",
                    "start_urls": "http://www.ifeng.com",
                    "status": 0,
                    "type": "spider",
                    "update_at": "2017-04-13 10:55:00",
                    "url_unique_mode": "url-query"
                }
            }
        @apiSuccessExample {Json} 请求失败
            {
                "status": "failed",
                "msg": "not find",
                "data": {}
            }
        """
        task = bTask.task_get_id(taskid)
        if task:
            return {'status':'ok', 'msg':'', 'data':task}, 200
        else:
            return {'status':'failed', 'msg':'not find', 'data':{}}, 200

class TasksaveAPI(Resource):

    @verify_token
    def post(self):
        """
        @apiDescription 保存任务数据
        @api {post} /task/save 保存任务
        @apiName task_save
        @apiGroup Task
        @apiVersion 0.1.0
        @apiHeader {String} token token
        @apiParam {Number} id 任务ID，如果不存在，则为新建任务，如果存在，则是更新任务
        @apiParam {String} start_urls 入口URL，可为多个，以换行符(\n)分隔
        @apiParam {String} exec_level 执行级别，默认为0，越大越先执行，计划任务默认为0，非计划任务默认为1
        @apiParam {String} type 任务类型，目前只支持三种任务:<br/>
            spider: 蜘蛛<br/>
            monitor: 监控<br/>
            monitor_one: 单页面监控<br/>
            mirror: 镜像<br/>
            mirror_one: 单页面镜像<br/>
        @apiParam {Number} limit_depth 抓取深度, 默认为2，0为不限制
        @apiParam {Number} limit_total 抓取总数, 默认为1000，0为不限制
        @apiParam {Number} limit_time 抓取时长, 默认为0,不限制； 单位：秒
        @apiParam {Number} limit_image 是否抓取图像，0(不抓取)/1(抓取)，默认不抓取
        @apiParam {Number} limit_subdomain 是否抓取二级域名，0(不抓取)/1(抓取)，默认不抓取
        @apiParam {Number} limit_js 是否执行JS，0(不执行)/1(执行)，默认不执行
        @apiParam {Number} limit_jsevent 是否执行JS事件，0(不执行)/1(执行)，默认不执行，此操作极消耗性能
        @apiParam {String} url_unique_mode 支持两种模式：<br/>
            url：只针对URL去重<br/>
            url-query：将query格式化后去重，避免了参数值变化的影响
        @apiParam {String} notify_url 通知URL, 回调URL接收数据后，要返回 ok
        @apiParam {String} status 执行状态:
            -1删除<br/>
            0停用(默认)<br/>
            1启用<br/>
        @apiParam {String} source_ip  网站的源IP, 可以不填
        @apiParam {String} exclude_urls  不抓取的url，以换行(\n)分隔
        @apiParam {String} proxies  代理,可以为多个，以逗号分隔，支持两种格式：<br/>
            http://proxy_server:port<br/>
            http://user:password@proxy_server:port
        @apiParam {String} crontab  计划任务，与linux的crontab格式相同; 为空则立即执行
        @apiParam {String} execute_at 定时执行时间，格式 YYYY-MM-DD HH:II:SS
        @apiParam {String} execute_delay 延时时间，单位秒

        @apiExample {js} 请求示例:
            curl -H "Content-type: application/json;charset=utf-8\ntoken: wbsllmigfa4ct0zp4gdd4hx2umpijg4e" apiUrl

        @apiParamExample {json} 参数示例:
            {
                "id":0,
                "start_urls":"http://www.ifeng.com\nhttp://www.qq.com", 
                "type":"spider",
                "limit_depth":2,
                "limit_total":1000,
                "limit_time":0,
                "limit_image":0,
                "limit_subdomain":0,
                "limit_js":0,
                "limit_jsevent":0, 
                "url_unique_mode":0,
                "notify_url": "http://test.nodevops.cn/receive/spider",
                "status": 1,
                "source_ip":"", 
                "exclude_urls":"http://news.ifeng.com/a/20170626/51324880_0.shtml\nhttp://news.ifeng.com/a/20170626/51323927_0.shtml", 
                "proxies": "http://192.168.3.143,http://jw:123456@192.168.3.143:8083",
                "crontab":"* * * * *"
            }
        @apiSuccessExample {Json} 请求成功
            {
                "status": "ok",
                "msg": "ok",
                "data": {
                    "task_id": 1
                }
            }
        @apiSuccessExample {Json} 请求失败
            {
                "status": "failed",
                "msg": "not find",
                "data": {}
            }
        @apiErrorExample {Json} 回调通知数据格式：
            {
                "id": 1,
                "app_id": 1,
                "task_id": 1,
                "site_id": 1,
                "execute_id": 1,
                "task_type": "spider",
                ......
            }
        """
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int)
        parser.add_argument('start_urls', type=str)
        parser.add_argument('exec_level', type=int)
        parser.add_argument('type', type=str)
        parser.add_argument('limit_depth', type=int)
        parser.add_argument('limit_total', type=int)
        parser.add_argument('limit_time', type=int)
        parser.add_argument('limit_image', type=int)
        parser.add_argument('limit_subdomain', type=int)
        parser.add_argument('limit_js', type=int)
        parser.add_argument('limit_js', type=int)
        parser.add_argument('limit_jsevent', type=int)
        parser.add_argument('exclude_urls', type=str)
        parser.add_argument('url_unique_mode', type=str)
        parser.add_argument('notify_url', type=str)
        parser.add_argument('source_ip', type=str)
        parser.add_argument('proxies', type=str)
        parser.add_argument('crontab', type=str)
        parser.add_argument('execute_at', type=str)
        parser.add_argument('execute_delay', type=int)
        parser.add_argument('status', type=int)
        args = parser.parse_args()
        logger.info("task_save: " + json.dumps(args, ensure_ascii=False))
        params = dict({'app_id':session['app']['id']}, **args)
        result = bTask.task_save(params)
        if result:
            return {'status':'ok', 'msg':'task add success', 'data': {'task_id':result}}, 200
        else:
            return {'status':'failed', 'msg':'task add error', 'data':{}}, 200

class Tasksave_multiAPI(Resource):

    @verify_token
    def post(self):
        """
        @apiDescription 保存多任务 仅增加
        @api {post} /task/save_multi 保存多任务 仅增加
        @apiName task_save_multi
        @apiGroup Task
        @apiVersion 0.1.0
        @apiHeader {String} token token
        @apiParam {Number} id 任务ID，如果不存在，则为新建任务，如果存在，则是更新任务
        @apiParam {String} start_taskurls 多任务的URL入口数据，每个任务的URL以逗号分隔，任务内如果有多个URL，以\n分隔<br/>
            示例1："http://news.ifeng.com/","http://tech.163.com/"<br/>
            示例2："http://news.ifeng.com/\nhttp://news.ifeng.com/mainland/","http://tech.163.com/\nhttp://tech.163.com/vr/"<br/>
        @apiParam {String} type 任务类型，目前只支持三种任务:<br/>
            spider: 蜘蛛<br/>
            monitor: 监控<br/>
            monitor_one: 单页面监控<br/>
            mirror: 镜像<br/>
            mirror_one: 单页面镜像<br/>
        @apiParam {String} exec_level 执行级别，默认为0，越大越先执行，计划任务默认为0，非计划任务默认为1
        @apiParam {Number} limit_depth 抓取深度, 默认为2，0为不限制
        @apiParam {Number} limit_total 抓取总数, 默认为1000，0为不限制
        @apiParam {Number} limit_time 抓取时长, 默认为0,不限制； 单位：秒
        @apiParam {Number} limit_image 是否抓取图像，0(不抓取)/1(抓取)，默认不抓取
        @apiParam {Number} limit_subdomain 是否抓取二级域名，0(不抓取)/1(抓取)，默认不抓取
        @apiParam {Number} limit_js 是否执行JS，0(不执行)/1(执行)，默认不执行
        @apiParam {Number} limit_jsevent 是否执行JS事件，0(不执行)/1(执行)，默认不执行，此操作极消耗性能
        @apiParam {String} url_unique_mode 支持两种模式：<br/>
            url：只针对URL去重<br/>
            url-query：将query格式化后去重，避免了参数值变化的影响
        @apiParam {String} notify_url 通知URL, 回调URL接收数据后，要返回 ok
        @apiParam {String} status 执行状态:
            -1删除<br/>
            0停用(默认)<br/>
            1启用<br/>
        @apiParam {String} source_ip  网站的源IP, 可以不填
        @apiParam {String} exclude_urls  不抓取的url，以换行(\n)分隔
        @apiParam {String} proxies  代理,可以为多个，以逗号分隔，支持两种格式：<br/>
            http://proxy_server:port<br/>
            http://user:password@proxy_server:port
        @apiParam {String} crontab  计划任务，与linux的crontab格式相同; 为空则立即执行
        @apiParam {String} execute_at 定时执行时间，格式 YYYY-MM-DD HH:II:SS
        @apiParam {String} execute_delay 延时时间，单位秒

        @apiExample {js} 请求示例:
            curl -H "Content-type: application/json;charset=utf-8\ntoken: wbsllmigfa4ct0zp4gdd4hx2umpijg4e" apiUrl

        @apiParamExample {json} 参数示例:
            {
                "id":0,
                "start_taskurls":"\"http://news.ifeng.com/\nhttp://news.ifeng.com/mainland/\",\"http://tech.163.com/\nhttp://tech.163.com/vr/\"",
                "type":"spider",
                "exec_level":0,
                "limit_depth":2,
                "limit_total":1000,
                "limit_time":0,
                "limit_image":0,
                "limit_subdomain":0,
                "limit_js":0,
                "limit_jsevent":0, 
                "url_unique_mode":0,
                "notify_url": "http://test.nodevops.cn/receive/spider",
                "status": 1,
                "source_ip":"", 
                "exclude_urls":"http://news.ifeng.com/a/20170626/51324880_0.shtml\nhttp://news.ifeng.com/a/20170626/51323927_0.shtml", 
                "proxies": "http://192.168.3.143,http://jw:123456@192.168.3.143:8083",
                "crontab":"* * * * *"
            }
        @apiSuccessExample {Json} 请求成功
            {
                "status": "ok",
                "msg": "ok",
                "data": {
                    "task_id": 1
                }
            }
        @apiSuccessExample {Json} 请求失败
            {
                "status": "failed",
                "msg": "not find",
                "data": {}
            }
        @apiErrorExample {Json} 回调通知数据格式：
            {
                "id": 1,
                "app_id": 1,
                "task_id": 1,
                "site_id": 1,
                "execute_id": 1,
                "task_type": "spider",
                ......
            }
        """
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int)
        parser.add_argument('start_taskurls', type=str)
        parser.add_argument('type', type=str)
        parser.add_argument('exec_level', type=int)
        parser.add_argument('limit_depth', type=int)
        parser.add_argument('limit_total', type=int)
        parser.add_argument('limit_time', type=int)
        parser.add_argument('limit_image', type=int)
        parser.add_argument('limit_subdomain', type=int)
        parser.add_argument('limit_js', type=int)
        parser.add_argument('limit_js', type=int)
        parser.add_argument('limit_jsevent', type=int)
        parser.add_argument('exclude_urls', type=str)
        parser.add_argument('url_unique_mode', type=str)
        parser.add_argument('notify_url', type=str)
        parser.add_argument('source_ip', type=str)
        parser.add_argument('proxies', type=str)
        parser.add_argument('crontab', type=str)
        parser.add_argument('execute_at', type=str)
        parser.add_argument('execute_delay', type=int)
        parser.add_argument('status', type=int)
        args = parser.parse_args()
        logger.info("task_save: " + json.dumps(args, ensure_ascii=False))
        params = dict({'app_id':session['app']['id']}, **args)
        taskurlStr = params['start_taskurls']
        del(params['start_taskurls'])
        taskurls = taskurlStr.split(',')
        taskids = []
        for taskurl in taskurls:
            taskurl = taskurl.strip()
            if not taskurl: continue
            if 'start_urls' in params.keys(): del(params['start_urls'])
            params['start_urls'] = taskurl
            taskid = bTask.task_save(params)
            if taskid: taskids.append(taskid)
        if taskids:
            return {'status':'ok', 'msg':'task add success', 'data': {'task_ids':taskids}}, 200
        else:
            return {'status':'failed', 'msg':'task add error', 'data':{}}, 200

class TaskdeleteAPI(Resource):

    @verify_token
    def post(self):
        """
        @apiDescription  删除任务
        @api {post} /task/delete 删除任务
        @apiName task_delete
        @apiGroup Task
        @apiVersion 0.1.0
        @apiHeader {String} token token
        @apiParam {String} ids 任务ID，多个以逗号(,)分隔, 如：ids=1,2,3,4,5
        @apiSuccessExample {Json} 请求成功
            {
                "status": "ok",
                "msg": "ok",
                "data": {}
            }
        @apiSuccessExample {Json} 请求失败
            {
                "status": "failed",
                "msg": "not find",
                "data": {}
            }
        """
        parser = reqparse.RequestParser()
        parser.add_argument('ids', type=str)
        args = parser.parse_args()
        ids = args['ids'].split(',')
        result = bTask.task_delete_ids(ids)
        if result:
            return {'status':'ok', 'msg':'task add success', 'data': ids}, 200
        else:
            return {'status':'failed', 'msg':'task add error', 'data':{}}, 200

class TaskupdatestatusAPI(Resource):

    @verify_token
    def post(self):
        """
        @apiDescription 批量修改任务状态 
        @api {post} /task/updatestatus 批量修改任务状态
        @apiName task_delete
        @apiGroup Task
        @apiVersion 0.1.0
        @apiHeader {String} token token
        @apiParam {String} ids 任务ID，多个以逗号(,)分隔, 如：ids=1,2,3,4,5
        @apiParam {String} status 任务状态：<br/>
            -1删除<br/>
            0停用(默认)<br/>
            1启用<br/>
        @apiSuccessExample {Json} 请求成功
            {
                "status": "ok",
                "msg": "ok",
                "data": {}
            }
        @apiSuccessExample {Json} 请求失败
            {
                "status": "failed",
                "msg": "not find",
                "data": {}
            }
        """
        parser = reqparse.RequestParser()
        parser.add_argument('ids', type=str)
        parser.add_argument('status', type=int)
        args = parser.parse_args()
        ids = args['ids'].split(',')
        status = args['status']
        if status not in [-1, 0, 1]:
            return {'status':'failed', 'msg':'status must be in -1,0,1,2,3', 'data':{}}, 200

        result = bTask.task_update_ids({'status':status}, ids)
        if result:
            return {'status':'ok', 'msg':'task add success', 'data': ids}, 200
        else:
            return {'status':'failed', 'msg':'task add error', 'data':{}}, 200

class TasklistAPI(Resource):

    @verify_token
    def get(self):
        """
        @apiDescription 批量获取任务
        @api {get} /task/list 任务列表
        @apiName task_list
        @apiGroup Task
        @apiVersion 0.1.0
        @apiHeader {String} token token
        @apiParam {Number} id 任务ID，如果不存在，则为新建任务，如果存在，则是更新任务
        @apiParam {Number} page 当前页码
        @apiParam {Number} pagesize 每页的数据条数
        @apiSuccessExample {Json} 请求成功
            {
                "status": "ok",
                "msg": "ok",
                "data": [
                    {
                        "app_id": 1,
                        "create_at": "2017-04-19 16:07:46",
                        "crontab": "* * * * * ",
                        "id": 10,
                        "limit_depth": 2,
                        "limit_image": 0,
                        "limit_js": 0,
                        "limit_subdomain": 0,
                        "limit_time": 1800,
                        "limit_total": 1000,
                        "notify_url": "http://www.ifeng.com/",
                        "proxies": "",
                        "site_id": 1,
                        "source_ip": "127.0.0.1 ",
                        "start_urls": "[\"http://www.ifeng.com\"]",
                        "status": 0,
                        "type": "spider",
                        "update_at": "2017-04-19 16:07:46",
                        "url_unique_mode": "url-query"
                    },
                    ......
                ]
            }
        @apiSuccessExample {Json} 请求失败
            {
                "status": "failed",
                "msg": "not find",
                "data": {}
            }
        """
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int)
        parser.add_argument('pagesize', type=int)
        args = parser.parse_args()
        tasks = bTask.task_getall(args['page'], args['pagesize'])
        if tasks:
            return {'status':'ok', 'msg':'', 'data':tasks}, 200
        else:
            return {'status':'failed', 'msg':'not find', 'data':{}}, 200


class ExecuteGetbyidAPI(Resource):

    @verify_token
    def get(self, executeid):
        """
        @apiDescription 获取任务执行信息，任务执行有四种状态：<br/>
            0待执行(默认)<br/>
            1抓取中<br/>
            2抓取完成<br/>
            3抓取异常<br/>
            4数据处理完成<br/>
        @api {get} /execute/getbyid/:executeid 获取执行信息
        @apiName execute
        @apiGroup Execute
        @apiVersion 0.1.0
        @apiHeader {String} token token
        @apiParam {Number} id 任务ID，如果不存在，则为新建任务，如果存在，则是更新任务
        @apiParam {Number} id 任务执行ID
        @apiSuccessExample {Json} 请求成功
            {
                "status": "ok",
                "msg": "ok",
                "data": {
                    "app_id": 1,
                    "create_at": "2017-04-13 10:58:00",
                    "domain": "www.ifeng.com",
                    "end_at": "2017-04-14 09:08:18",
                    "error": "",
                    "id": 1,
                    "limit_depth": 2,
                    "limit_image": 0,
                    "limit_js": 1,
                    "limit_subdomain": 0,
                    "limit_time": 7200,
                    "limit_total": 5000,
                    "notify_url": "http://localhost/",
                    "proxies": "",
                    "site_id": 1,
                    "source_ip": " ",
                    "start_at": "2017-04-14 09:08:07",
                    "start_urls": "[\"http://www.ifeng.com\"]",
                    "status": 2,
                    "task_id": 1,
                    "task_type": "spider",
                    "update_at": "2017-04-13 10:58:00",
                    "url_unique_mode": "url-query"
                }
            }
        @apiSuccessExample {Json} 请求失败
            {
                "status": "failed",
                "msg": "not find",
                "data": {}
            }
        """
        execute = bTask.execute_get_id(executeid)
        if execute:
            return {'status':'ok', 'msg':'', 'data':execute}, 200
        else:
            return {'status':'failed', 'msg':'not find', 'data':{}}, 200

class ExecuteGetbytaskidAPI(Resource):

    @verify_token
    def get(self, executeid):
        """
        @apiDescription 根据任务ID获取最新执行信息，任务执行有4种状态：<br/>
            0待执行(默认)<br/>
            1抓取中<br/>
            2抓取完成<br/>
            3抓取异常<br/>
            4数据处理完成<br/>
        @api {get} /execute/getbytaskid/:taskid 根据任务ID获取最新执行信息
        @apiName execute
        @apiGroup Execute
        @apiVersion 0.1.0
        @apiHeader {String} token token
        @apiParam {Number} id 任务ID，如果不存在，则为新建任务，如果存在，则是更新任务
        @apiParam {Number} id 任务执行ID
        @apiSuccessExample {Json} 请求成功
            {
                "status": "ok",
                "msg": "ok",
                "data": {
                    "app_id": 1,
                    "create_at": "2017-04-13 10:58:00",
                    "domain": "www.ifeng.com",
                    "end_at": "2017-04-14 09:08:18",
                    "error": "",
                    "id": 1,
                    "limit_depth": 2,
                    "limit_image": 0,
                    "limit_js": 1,
                    "limit_subdomain": 0,
                    "limit_time": 7200,
                    "limit_total": 5000,
                    "notify_url": "http://localhost/",
                    "proxies": "",
                    "site_id": 1,
                    "source_ip": " ",
                    "start_at": "2017-04-14 09:08:07",
                    "start_urls": "[\"http://www.ifeng.com\"]",
                    "status": 2,
                    "task_id": 1,
                    "task_type": "spider",
                    "update_at": "2017-04-13 10:58:00",
                    "url_unique_mode": "url-query"
                }
            }
        @apiSuccessExample {Json} 请求失败
            {
                "status": "failed",
                "msg": "not find",
                "data": {}
            }
        """
        execute = bTask.execute_getnew_taskid(taskid)
        if execute:
            return {'status':'ok', 'msg':'', 'data':execute}, 200
        else:
            return {'status':'failed', 'msg':'not find', 'data':{}}, 200

class ExecutelistAPI(Resource):

    @verify_token
    def get(self,taskid):
        """
        @apiDescription 任务执行列表，任务执行有四种状态：<br/>
            0待执行(默认)<br/>
            1抓取中<br/>
            2抓取完成<br/>
            3抓取异常<br/>
            4数据处理完成<br/>
        @api {get} /execute/list/:taskid 批量获取执行信息
        @apiName execute_list
        @apiGroup Execute
        @apiVersion 0.1.0
        @apiHeader {String} token token
        @apiParam {Number} id 任务ID，如果不存在，则为新建任务，如果存在，则是更新任务
        @apiParam {Number} task_id 任务ID
        @apiSuccessExample {Json} 请求成功
            {
                "status": "ok",
                "msg": "ok",
                "data": [
                    {
                        "app_id": 1,
                        "create_at": "2017-04-13 11:02:00",
                        "domain": "www.ifeng.com",
                        "end_at": "2017-04-13 03:49:45",
                        "error": "",
                        "id": 11,
                        "limit_depth": 2,
                        "limit_image": 0,
                        "limit_js": 1,
                        "limit_subdomain": 0,
                        "limit_time": 7200,
                        "limit_total": 5000,
                        "notify_url": "http://localhost/",
                        "proxies": "",
                        "site_id": 1,
                        "source_ip": " ",
                        "start_at": "2017-04-13 03:49:24",
                        "start_urls": "[\"http://www.ifeng.com\"]",
                        "status": 2,
                        "task_id": 1,
                        "task_type": "spider",
                        "update_at": "2017-04-13 11:02:00",
                        "url_unique_mode": "url-query"
                    },
                    ......
                ]
            }
        @apiSuccessExample {Json} 请求失败
            {
                "status": "failed",
                "msg": "not find",
                "data": {}
            }
        """
        executes = bTask.execute_getall_taskid(taskid)
        if executes:
            return {'status':'ok', 'msg':'', 'data':executes}, 200
        else:
            return {'status':'failed', 'msg':'not find', 'data':{}}, 200

class ExecuteurlsbyidAPI(Resource):

    @verify_token
    def get(self, executeid):
        """
        @apiDescription 获取抓取的 url 列表
        @api {get} /execute/urlsbyid/:executeid 获取抓取的 url 列表
        @apiName execute_urlsbyid
        @apiGroup Execute
        @apiVersion 0.1.0
        @apiHeader {String} token token
        @apiParam {Number} executeid 执行ID
        @apiSuccessExample {Json} 请求成功
            {
                "status": "ok",
                "msg": "ok",
                "data": [
                    {
                        "http_code": "200",
                        "id": 1610,
                        "md5_url": "bf3f4c002d0a5b1ad16e1fcf9ec6a22c",
                        "method": "get",
                        "post": "",
                        "query": "",
                        "referer": "",
                        "url": "http://www.ifeng.com"
                    },
                    ......
                ]
            } 
        @apiSuccessExample {Json} 请求失败
            {
                "status": "failed",
                "msg": "not find",
                "data": {}
            }
        """
        parser = reqparse.RequestParser()
        parser.add_argument('exclude_extension', type=str)
        params = parser.parse_args()
        excludes = []
        if 'exclude_extension' in params.keys() and params['exclude_extension']:
            excludes = params['exclude_extension'].replace(" ", "").split(",")
        rows = []
        fields = ['id','url','md5_url','referer','method','query','post','http_code']
        urls = mgdb.spiderurl_getexecuteid(executeid, fields)
        for row in urls:
            if excludes:
                if row['file_extension'] in excludes:
                    rows.append(row)
            else:
                rows.append(row)
        if rows:
            return {'status':'ok', 'msg':'', 'data':rows}, 200
        else:
            return {'status':'failed', 'msg':'not find', 'data':{}}, 200

class ExecuteurlsbytaskidAPI(Resource):

    @verify_token
    def get(self, taskid):
        """
        @apiDescription 根据任务ID获取最新的 url
        @api {get} /execute/urlsbytaskid/:taskid 根据任务ID获取最新的 url
        @apiName execute_urlsbytaskid
        @apiGroup Execute
        @apiVersion 0.1.0
        @apiHeader {String} token token
        @apiParam {Number} taskid 执行ID
        @apiSuccessExample {Json} 请求成功
            {
                "status": "ok",
                "msg": "ok",
                "data": [
                    {
                        "http_code": "200",
                        "id": 1610,
                        "md5_url": "bf3f4c002d0a5b1ad16e1fcf9ec6a22c",
                        "method": "get",
                        "post": "",
                        "query": "",
                        "referer": "",
                        "url": "http://www.ifeng.com"
                    },
                    ......
                ]
            } 
        @apiSuccessExample {Json} 请求失败
            {
                "status": "failed",
                "msg": "not find",
                "data": {}
            }
        """
        execute = bTask.execute_getnew_taskid(taskid)
        urls = mgdb.spiderurl_getbyexecuteid(execute['id'])
        if urls:
            return {'status':'ok', 'msg':'', 'data':urls}, 200
        else:
            return {'status':'failed', 'msg':'not find', 'data':{}}, 200

class PipingsaveAPI(Resource):

    @verify_token
    def post(self):
        """
        @apiDescription 保存数据处理通道
        @api {post} /piping/save 保存数据处理通道
        @apiName piping_save
        @apiGroup Piping
        @apiVersion 0.1.0
        @apiHeader {String} token token
        @apiParam {String} data  要保存的数据，可以批量保存，JSON格式
        @apiParam {String} task_id 任务ID
        @apiParam {String} type  通道类型，支持的类型有：<br/>
            fingerprint(指纹)<br/>
            trojan(木马)<br/>
            darklink(暗链)<br/>
            brokenlink(断链)<br/>
            filterword(敏感词)<br/>
            keyword(关键词)<br/>
            error_http_code(异常状态码)<br/>
            如果通道类型是 filterword ，需要指定filterwords及filterword_type，不指定则使用默认词库<br/>
            如果通道类型是 keyword ，需要指定keywords，否则保存失败<br/>
            如果通道类型是 error_http_code ，需要指定http_codes
        @apiParam {String} filterwords 词库。以\n分隔。仅针对 filterword 通道，不指定则使用默认词库。
        @apiParam {String} filterword_type 词库类型，仅针对filterword通过。类型：<br/>
            system(使用系统词库)<br/>
            own(自有词库，即不使用默认词库)<br/>
            mixed(混合，系统词库＋自有词库)
        @apiParam {String} filterword_operate 词库操作，针对filterword通道。类型：<br/>
            own(覆盖已有词库)<br/>
            plus(追加，即在自有词库中追加新词)<br/>
            reduce(减法，即在自有词库去掉部分词)<br/>
            filterword通道，如果words_type为 system，则此项可以不填
        @apiParam {String} keywords 关键词库，针对keyword通道，字典类型，如：<br/>
            [<br/>
                {"url":"http://www.ifeng.com/","words":["CDN", "云平台", "安全"]},<br/>
                ......<br/>
            ]
        @apiParam {String} http_codes 状态码列表，针对error_http_code通道，以"\n"分隔。
        @apiParam {Number} status 状态：0停用 1启用

        @apiParamExample {Json} 新增通道:
            data = {
                'task_id':1,
                'pipings':[
                    {
                        "type": "fingerprint",
                        "status": 1,
                    },
                    {
                        "type": "filterword",
                        "filterwords":"日本狗\n高丽棒子",
                        "filterword_type":"mixed",
                        "filterword_operate":"plus",
                        "status": 1,
                    },
                    {
                        "type": "keyword",
                        "keywords": [
                            {
                                "url":"http://www.ifeng.com/",
                                "words":["CDN", "云平台", "安全"]
                            },
                            ......
                        ],
                        "status": 1,
                    },
                    {
                        "type": "error_http_code",
                        "http_codes": "403\n404\n405\n406\n500\n501\n502\n503\n504",
                        "status": 1,
                    },
                    ......
                ]
            }

        @apiSuccessExample {Json} 请求成功
           {
               "status":"ok",
               "msg":"ok",
               "data":results
           }
        @apiSuccessExample {Json} 请求失败
            {
                "status": "failed",
                "msg": "not find",
                "data": {}
            }
        """
        parser = reqparse.RequestParser()
        parser.add_argument('data', type=str)
        params = parser.parse_args()
        try:
            data = json.loads(params['data'])
            if 'task_id' not in data.keys() or 'pipings' not in data.keys():
                return {'status':'failed', 'msg':'params is error', 'data':{}}, 200
            taskid = data['task_id']
            pipings = data['pipings']
        except Exception as e:
            return {'status':'failed', 'msg':'the params is error', 'data':{}}, 200
        results = bPiping.piping_save(pipings, taskid)
        if results:
            return {'status':'ok', 'msg':'ok', 'data':results}, 200
        else:
            return {'status':'failed', 'msg':'not find', 'data':{}}, 200


class PipinglistAPI(Resource):

    @verify_token
    def get(self, taskid):
        """
        @apiDescription 获取数据处理通道
        @api {get} /piping/list/:taskid 获取数据处理通道
        @apiName piping_list
        @apiGroup Piping
        @apiVersion 0.1.0
        @apiHeader {String} token token
        @apiParam {String} taskid 任务ID
        @apiSuccessExample {Json} 请求成功
           {
               "status":"ok",
               "msg":"ok",
               "data":results
           }
        @apiSuccessExample {Json} 请求失败
            {
                "status": "failed",
                "msg": "not find",
                "data": {}
            }
        """
        '''
        根据task_id获取数据处理通道的信息
        '''
        results = bPiping.piping_getall_taskid(taskid)
        if results:
            return {'status':'ok', 'msg':'ok', 'data':results}, 200
        else:
            return {'status':'failed', 'msg':'not find', 'data':{}}, 200

class PipingresultsAPI(Resource):

    @verify_token
    def get(self, executeid):
        """
        @apiDescription 获取数据处理结果
        @api {get} /piping/results/:executeid 获取数据处理结果
        @apiName piping_results
        @apiGroup Piping
        @apiVersion 0.1.0
        @apiHeader {String} token token
        @apiParam {String} taskid 任务ID
        @apiSuccessExample {Json} 请求成功
            {
                "status": "ok"
                "msg": "ok",
                "data": [
                    {
                        "create_at": "2017-06-25 23:07:14",
                        "execute_id": 6,
                        "result": [
                            {
                                "http_code": "404",
                                "id": 1708,
                                "url": "http://p0.ifengimg.com/fe/com-survey/scripts/com-box-survey_7adab11c"
                            },
                            ......
                        ],
                        "task_id": 1,
                        "type": "error_http_code"
                    }
                ],
            }
        @apiSuccessExample {Json} 请求失败
            {
                "status": "failed",
                "msg": "not find",
                "data": {}
            }
        """
        '''
        根据executeid获取到数据处理结果
        处理结果包含所有处理的
        后的task_id、execute_id、type、result、create_at
        '''
        results = bPiping.result_getall_executeid(executeid)
        if results:
            return {'status':'ok', 'msg':'ok', 'data':results}, 200
        else:
            return {'status':'failed', 'msg':'not find', 'data':{}}, 200

class ProxyAPI(Resource):

    @verify_token
    def get(self, proxyid):
        """
        @apiDescription 获取代理信息
        @api {get} /proxy/:id 获取代理信息
        @apiName proxy
        @apiGroup Proxy
        @apiVersion 0.1.0
        @apiHeader {String} token token
        @apiParam {Number} id 任务ID，如果不存在，则为新建任务，如果存在，则是更新任务
        @apiParam {Number} id 代理ID
        @apiSuccessExample {Json} 请求成功
            {
                "status": "ok",
                "msg": "ok",
                "data": {
                    "create_at": "2017-04-18 11:01:51",
                    "id": 1,
                    "ip": "127.0.0.1 ",
                    "passwd": "tester",
                    "port": 80,
                    "status": 0,
                    "update_at": "2017-04-18 11:01:51",
                    "username": "tester"
                }
            }
        @apiSuccessExample {Json} 请求失败
            {
                "status": "failed",
                "msg": "not find",
                "data": {}
            }
        """
        proxy = bProxy.get_id(proxyid)
        if proxy:
            return {'status':'ok', 'msg':'ok', 'data':proxy}, 200
        else:
            return {'status':'failed', 'msg':'not find', 'data':{}}, 200

class ProxysearchAPI(Resource):

    @verify_token
    def get(self):
        """
        @apiDescription 代理列表
        @api {get} /proxy/list 代理列表
        @apiName proxy_list
        @apiGroup Proxy
        @apiVersion 0.1.0
        @apiHeader {String} token token
        @apiParam {Number} id 任务ID，如果不存在，则为新建任务，如果存在，则是更新任务
        @apiParam {Number} page 当前页数
        @apiParam {Number} pagesize 每页数据量
        @apiSuccessExample {Json} 请求成功
            {
                "status": "ok",
                "msg": "ok",
                "data": [
                    {
                        "create_at": "2017-04-20 11:14:09",
                        "id": 2,
                        "ip": "127.0.0.1 ",
                        "passwd": "",
                        "port": 80,
                        "status": 0,
                        "update_at": "2017-04-20 11:14:09",
                        "username": ""
                    },
                    ......
                ]
            }
        @apiSuccessExample {Json} 请求失败
            {
                "status": "failed",
                "msg": "not find",
                "data": {}
            }
        """
        proxies = bProxy.getall()
        if proxies:
            return {'status':'ok', 'msg':'ok', 'data':proxies}, 200
        else:
            return {'status':'failed', 'msg':'not find', 'data':{}}, 200

class ProxysaveAPI(Resource):

    @verify_token
    def post(self):
        """
        @apiDescription 保存代理  
            无密码：http://some_proxy_server:port
            有密码：http://username:password@some_proxy_server:port
        @api {post} /proxy/save 保存代理
        @apiName proxy_save
        @apiGroup Proxy
        @apiVersion 0.1.0
        @apiHeader {String} token token
        @apiParam {Number} id 任务ID，如果不存在，则为新建任务，如果存在，则是更新任务
        @apiParam {Number} id 代理ID，如果为空，则为新建
        @apiParam {String} ip 源IP
        @apiParam {Number} port 端口
        @apiParam {String} port 用户名
        @apiParam {String} passwd 密码
        @apiSuccessExample {Json}  请求成功
            {
                "status": "ok",
                "msg": "ok",
                "data": {
                    "proxy_id": 1
                }
            }
        @apiSuccessExample {Json} 请求失败
            {
                "status": "failed",
                "msg": "not find",
                "data": {}
            }
        """
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int)
        parser.add_argument('ip', type=str)
        parser.add_argument('port', type=int)
        parser.add_argument('username', type=str)
        parser.add_argument('passwd', type=str)
        args = parser.parse_args()
        result = bProxy.save(args)
        if result:
            return {'status':'ok', 'msg':'task add success', 'data': {'proxy_id':result}}, 200
        else:
            return {'status':'failed', 'msg':'save error', 'data':{}}, 200

class SettingAPI(Resource):

    @verify_token
    def get(self, settingid):
        """
        @apiDescription 获取配置信息
        @api {get} /setting/:id 获取配置
        @apiName setting
        @apiGroup Setting
        @apiVersion 0.1.0
        @apiHeader {String} token token
        @apiParam {Number} id 任务ID，如果不存在，则为新建任务，如果存在，则是更新任务
        @apiSuccessExample {Json}  请求成功
            {
                "status": "ok",
                "msg": "ok",
                "data": {
                    "create_at": "2017-04-20 14:16:38",
                    "data_type": "str",
                    "id": 1,
                    "key": "tester",
                    "name": "tester",
                    "note": "ttss",
                    "update_at": "2017-04-20 14:16:38",
                    "value": "tester"
                }
            }
        @apiSuccessExample {Json} 请求失败
            {
                "status": "failed",
                "msg": "not find",
                "data": {}
            }
        """
        setting = bSet.get_id(settingid)
        if setting:
            return {'status':'ok', 'msg':'ok', 'data':setting}, 200
        else:
            return {'status':'failed', 'msg':'not find', 'data':{}}, 200

class SettingsAPI(Resource):

    @verify_token
    def get(self):
        """
        @apiDescription 配置列表
        @api {get} /setting/list 配置列表
        @apiName setting
        @apiGroup Setting
        @apiVersion 0.1.0
        @apiHeader {String} token token
        @apiParam {Number} page 配置ID
        @apiParam {Number} pagesize 配置ID
        @apiSuccessExample {Json}  请求成功
            {
                "status": "ok",
                "msg": "ok",
                "data": [
                    {
                        "create_at": "2017-04-20 14:16:58",
                        "data_type": "str",
                        "id": 2,
                        "key": "tester",
                        "name": "tester",
                        "note": "ttxx",
                        "update_at": "2017-04-20 14:16:58",
                        "value": "tester"
                    },
                    ......
                ]
            }
        @apiSuccessExample {Json} 请求失败
            {
                "status": "failed",
                "msg": "not find",
                "data": {}
            }
        """
        settings = bSet.getall()
        if settings:
            return {'status':'ok', 'msg':'ok', 'data':settings}, 200
        else:
            return {'status':'failed', 'msg':'not find', 'data':{}}, 200

class SettingsaveAPI(Resource):

    @verify_token
    def post(self):
        """
        @apiDescription 保存配置
        @api {post} /setting/save 保存配置
        @apiName setting_save
        @apiGroup Setting
        @apiVersion 0.1.0
        @apiHeader {String} token token
        @apiParam {Number} id 配置ID，如果为空，则为新建
        @apiParam {String} name 配置名称
        @apiParam {Number} key 配置的key，英文，只能是字母数字下划线，且字母开头
        @apiParam {String} value 值
        @apiParam {String} note 备注
        @apiSuccessExample {Json}  请求成功
            {
                "status": "ok",
                "msg": "ok",
                "data": {
                    "setting_id": 1
                }
            }
        @apiSuccessExample {Json} 请求失败
            {
                "status": "failed",
                "msg": "not find",
                "data": {}
            }
        """
        parser = reqparse.RequestParser()
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int)
        parser.add_argument('name', type=str)
        parser.add_argument('key', type=str)
        parser.add_argument('value', type=str)
        parser.add_argument('note', type=str)
        args = parser.parse_args()
        result = bSet.save(args)
        if result:
            return {'status':'ok', 'msg':'task add success', 'data': {'setting_id':result}}, 200
        else:
            return {'status':'failed', 'msg':'save error', 'data':{}}, 200

class AppAPI(Resource):

    @verify_token
    def get(self, appid):
        """
        @apiDescription 获取APP
        @api {get} /app/:appid 获取APP
        @apiName app
        @apiGroup App
        @apiVersion 0.1.0
        @apiHeader {String} token token
        @apiParam {Number} id APPID
        @apiSuccessExample {Json}  请求成功
            {
                "status": "ok",
                "msg": "ok",
                "data": {
                    "create_at": "2017-03-22 13:34:28",
                    "id": 1,
                    "token": "wbsllmigfa4ct0zp4gdd4hx2umpijg4e",
                    "token_expired": "2017-03-22 17:01:53",
                    "unique_key": "tester_app",
                    "update_at": "2017-03-22 13:34:28"
                }
            }
        @apiSuccessExample {Json} 请求失败
            {
                "status": "failed",
                "msg": "not find",
                "data": {}
            }
        """
        theApp = bApp.get_id(appid)
        if theApp:
            return {'status':'ok', 'msg':'ok', 'data': theApp}, 200
        else:
            return {'status':'failed', 'msg':'not find', 'data':{}}, 200

class ApplistAPI(Resource):

    @verify_token
    def get(self):
        """
        @apiDescription APP列表
        @api {get} /app/list APP列表
        @apiName app
        @apiGroup App
        @apiVersion 0.1.0
        @apiHeader {String} token token
        @apiParam {Number} page 当前页码
        @apiParam {Number} pagesize 每页的数据量
        @apiSuccessExample {Json} 请求成功
            {
                "status": "ok",
                "msg": "ok",
                "data": [
                    {
                        "create_at": "2017-04-20 15:14:59",
                        "id": 3,
                        "token": "",
                        "token_expired": "2017-04-20 15:14:59",
                        "unique_key": "testerxxxxx",
                        "update_at": "2017-04-20 15:14:59"
                    },
                    ......
                ]
            }
        @apiSuccessExample {Json} 请求失败
            {
                "status": "failed",
                "msg": "not find",
                "data": {}
            }
        """
        apps = bApp.getall()
        if apps:
            return {'status':'ok', 'msg':'ok', 'data':apps}, 200
        else:
            return {'status':'failed', 'msg':'not find', 'data':{}}, 200

class AppsaveAPI(Resource):

    @verify_token
    def post(self):
        """
        @apiDescription 保存APP
        @api {post} /app/save 保存APP
        @apiName app_save
        @apiGroup App
        @apiVersion 0.1.0
        @apiHeader {String} token token
        @apiParam {Number} id 配置ID，如果为空，则为新建
        @apiParam {String} unique_key 唯一标识符
        @apiParam {Number} public_key RSA公鈅
        @apiSuccessExample {Json}  请求成功
            {
                "status": "failed",
                "msg": "not find",
                "data": {
                    "app_id": 1,
                }
            }
        @apiSuccessExample {Json} 请求失败
            {
                "status": "failed",
                "msg": "not find",
                "data": {}
            }
        """
        parser = reqparse.RequestParser()
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int)
        parser.add_argument('unique_key', type=str)
        parser.add_argument('public_key', type=str)
        args = parser.parse_args()
        result = bApp.save(args)
        if result:
            return {'status':'ok', 'msg':'task add success', 'data': {'app_id':result}}, 200
        else:
            return {'status':'failed', 'msg':'save error', 'data':{}}, 200

class NotifylistAPI(Resource):
    @verify_token
    def get(self):
        notifies = bNotify.getall()
        if notifies:
            return {'status':'ok', 'msg':'ok', 'data':notifies}, 200
        else:
            return {'status':'failed', 'msg':'not find', 'data':{}}, 200

class InfotaskAPI(Resource):
    def get(self, taskid):
        task = bTask.task_get_id(taskid)
        if task:
            return {'status':'ok', 'msg':'ok', 'data':task}, 200
        else:
            return {'status':'failed', 'msg':'not find', 'data':{}}, 200

class InfoexecuteAPI(Resource):
    def get(self, executeid):
        execute = bTask.execute_get_id(executeid)
        task = bTask.task_get_id(execute['task_id'])
        if execute:
            return {'status':'ok', 'msg':'ok', 'data':{'task':task, 'execute':execute}}, 200
        else:
            return {'status':'failed', 'msg':'not find', 'data':{}}, 200

class InfourlAPI(Resource):
    def get(self, urlid):
        row = mgdb.spiderurl_getbyid(urlid)
        del(row['body'])
        execute = bTask.execute_get_id(row['execute_id'])
        task = bTask.task_get_id(row['task_id'])
        if row:
            return {'status':'ok', 'msg':'ok', 'data':{'url':row, 'execute':execute, 'task':task}}, 200
        else:
            return {'status':'failed', 'msg':'not find', 'data':{}}, 200

class InfourlbodyAPI(Resource):
    def get(self, urlid):
        row = mgdb.spiderurl_getbyid(urlid)
        if row:
            return {'status':'ok', 'msg':'ok', 'data':row['body']}, 200
        else:
            return {'status':'failed', 'msg':'not find', 'data':{}}, 200

class SnapshotSaveAPI(Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('batch_no', type=str)
        parser.add_argument('filename', type=str)
        parser.add_argument('type', type=str)
        parser.add_argument('url', type=int)
        parser.add_argument('notify_url', type=int)
        parser.add_argument('proxy', type=int)
        args = parser.parse_args()
        #参数不允许为空
        if not args['batch_no'] or not args['filename'] or not args['type'] or not args['url'] or not args['notify_url']:
            return {'status':'failed', 'msg':'params is error', 'data':{}}, 200

        params = dict(args, {"app_key":session['app']['unique_key']})
        result = bSnapshot.save(params)
        if result:
            return {'status':'ok', 'msg':'ok', 'data':result}, 200
        else:
            return {'status':'failed', 'msg':'not find', 'data':{}}, 200

class NamelistSaveAPI(Resource):

    def post(self):
        """
        @apiDescription 保存黑白名单
        @api {post} /namelist/save 保存黑白名单
        @apiName namelist_save
        @apiGroup namelist
        @apiVersion 0.1.0
        @apiHeader {String} token token
        @apiParam {String} domain 域名
        @apiParam {String} list_type 列表类型：white(白名单)/black(黑名单)
        @apiParam {String} scope 作用域
        @apiParam {String} url 链接
        @apiParam {Number} status 状态，只有两个： -1停用(删除)   1启用
        @apiSuccessExample {Json}  请求成功
            {
                "status": "failed",
                "msg": "not find",
                "data": ""
            }
        @apiSuccessExample {Json} 请求失败
            {
                "status": "failed",
                "msg": "not find",
                "data": {}
            }
        """
        parser = reqparse.RequestParser()
        parser.add_argument('domain', type=str)
        parser.add_argument('list_type', type=str)
        parser.add_argument('scope', type=str)
        parser.add_argument('url', type=int)
        parser.add_argument('status', type=int)
        args = parser.parse_args()

        result = bNamelist.link_save(args)
        if result:
            return {'status':'ok', 'msg':'ok', 'data':''}, 200
        else:
            return {'status':'failed', 'msg':'not find', 'data':{}}, 200

class NamelistListAPI(Resource):

    def get(self, type, domain):
        """
        @apiDescription 获取黑白名单
        @api {get} /namelist/list 保存黑白名单
        @apiName namelistlink_list
        @apiGroup namelist
        @apiVersion 0.1.0
        @apiHeader {String} token token
        @apiParam {String} domain 域名
        @apiParam {String} list_type 列表类型：white(白名单)/black(黑名单)
        @apiSuccessExample {Json}  请求成功
            {
                "status": "failed",
                "msg": "not find",
                "data": [
                    {
                        "domain":"www.yundun.com",
                        "primary_domain":"yundun.com",
                        "list_type":"black",
                        "scope":"domain",
                        "create_at":"2017-10-20 10:10:10",
                        "update_at":"2017-10-20 10:10:10"
                    },
                    ...
                ]
            }
        @apiSuccessExample {Json} 请求失败
            {
                "status": "failed",
                "msg": "not find",
                "data": {}
            }
        """
        row = bNamelist.link_getbydomain(type, domain)
        if row:
            return {'status':'ok', 'msg':'ok', 'data':row}, 200
        else:
            return {'status':'failed', 'msg':'not find', 'data':{}}, 200

class SnapshotSaveAPI(Resource):

    def post(self):
        """
        @apiDescription 保存快照任务
        @api {post} /snapshot/save 保存快照任务
        @apiName snapshot_save
        @apiGroup snapshot
        @apiVersion 0.1.0
        @apiHeader {String} token token
        @apiParam {String} domain 域名
        @apiParam {String} list_type 列表类型：white(白名单)/black(黑名单)
        @apiParam {String} scope 作用域
        @apiParam {String} url 链接
        @apiParam {Number} status 状态，只有两个： -1停用(删除)   1启用
        @apiSuccessExample {Json}  请求成功
            {
                "status": "failed",
                "msg": "not find",
                "data": ""
            }
        @apiSuccessExample {Json} 请求失败
            {
                "status": "failed",
                "msg": "not find",
                "data": {}
            }
        """
        pass
        #parser = reqparse.RequestParser()
        #parser.add_argument('domain', type=str)
        #parser.add_argument('list_type', type=str)
        #parser.add_argument('scope', type=str)
        #parser.add_argument('url', type=int)
        #parser.add_argument('status', type=int)
        #args = parser.parse_args()

        #result = bNamelist.link_save(args)
        #if result:
        #    return {'status':'ok', 'msg':'ok', 'data':''}, 200
        #else:
        #    return {'status':'failed', 'msg':'not find', 'data':{}}, 200



class DarklinkAPI(Resource):

    @verify_token
    def post(self):
        """
        @apiDescription 暗链操作处理通道
        @api {post} /darklink/operate 暗链操作处理通道
        @apiName Darklink
        @apiGroup darklink
        @apiVersion 0.1.0
        @apiHeader {String} token token
        @apiParam {String} data 要操作的数据 可以批量保存， JSON格式
        @apiParam {String} source 要操作数据的类型<br/>
            支持的类型有：<br/>
            敏感词(sensitive)<br/>
            暗链黑名单(black_list)<br/>
            暗链白名单(white_list)<br/>
            通道类型严格按照sensitive、black_list、white_list传递
        @apiParam {String} action 具体的动作：<br/>
            支持的动作有：<br/>
            增加(add)<br/>
            删除(del)<br/>
            动作类型严格按照add、del传递
        @apiParamExample {Json} 传输数据
        {
         "source": "sensitive",
         "action": "add",
         "data": [
          {
           "name": "共产党",
           "type": "fandong",
           "id": "1",
           "level": "high"
          }
         ]
        }
        @apiSuccessExample {Json} 请求成功
        {
            "source": "black_list",
            "action": "add",
            "status": 'success'
        }
        @apiFailedExample {Json} 请求失败
        {
            "source": "black_list",
            "action": "add",
            "status": 'failed'
        }
        """
        from flask import request
        parser = request.get_data().decode()
        data =json.loads(parser)
        params = data['data']
        if data['source'] == 'black_list' and data['action'] == 'save':
            result=darklink.black_add(params)
            if result:return {'source':'black_list','action':'save','status':'success'}, 200
            else: return {'source':'black_list','action':'save','status':'failed'}, 200
        elif data['source'] == 'black_list' and data['action'] == 'del':
            result=darklink.black_del(params)
            if result:return {'source':'black_list','action':'del','status':'success'}, 200
            else: return {'source':'black_list','action':'del','status':'failed'}, 200
        elif data['source'] == 'white_list' and data['action'] == 'save':
            result = darklink.white_add(params)
            if result:return {'source': 'white_list', 'action': 'save', 'status': 'success'}, 200
            else: return {'source':'white_list','action':'save','status':'failed'}, 200
        elif data['source'] == 'white_list' and data['action'] == 'del':
            result = darklink.white_del(params)
            if result:return {'source': 'white_list', 'action': 'del', 'status': 'success'}, 200
            else: return {'source': 'white_list', 'action': 'del', 'status': 'failed'}, 200
        elif data['source'] == 'sensitive' and data['action'] == 'save':
            result = darklink.filterword_add(params)
            if result:return {'source':'sensitive','action':'add','status':'success'}
            else:return {'source': 'sensitive', 'action': 'del', 'status': 'failed'}, 200
        elif data['source'] == 'sensitive' and data['action'] == 'del':
            result = darklink.filterword_del(params)
            if result:return {'source': 'filterword', 'action': 'del', 'status': 'success'}, 200
            else: return {'source': 'filterword', 'action': 'del', 'status': 'failed'}, 200
        else:return {'msg': 'params is error','status': 'failed', }, 200

api.add_resource(DarklinkAPI,'/v1/darklink/operate')
api.add_resource(TokenAPI, '/v1/token/<string:key>')
api.add_resource(TasklistAPI, '/v1/task/list')
api.add_resource(TaskAPI, '/v1/task/<int:taskid>')
api.add_resource(TasksaveAPI, '/v1/task/save')
api.add_resource(TaskdeleteAPI, '/v1/task/delete')
api.add_resource(TaskupdatestatusAPI, '/v1/task/updatestatus')
api.add_resource(Tasksave_multiAPI, '/v1/task/save_multi')

api.add_resource(ExecuteGetbyidAPI, '/v1/execute/getbyid/<int:executeid>')
api.add_resource(ExecuteGetbytaskidAPI, '/v1/execute/getbytaskid/<int:taskid>')
api.add_resource(ExecutelistAPI, '/v1/execute/list/<int:taskid>')
api.add_resource(ExecuteurlsbyidAPI, '/v1/execute/urlsbyid/<int:executeid>')
api.add_resource(ExecuteurlsbytaskidAPI, '/v1/execute/urlsbytaskid/<int:taskid>')

api.add_resource(PipingsaveAPI, '/v1/piping/save')
api.add_resource(PipinglistAPI, '/v1/piping/list/<int:taskid>')
api.add_resource(PipingresultsAPI, '/v1/piping/results/<int:executeid>')

api.add_resource(ProxyAPI, '/v1/proxy/<int:proxyid>')
api.add_resource(ProxysaveAPI, '/v1/proxy/save')
api.add_resource(ProxysearchAPI, '/v1/proxy/search')

api.add_resource(SettingAPI, '/v1/setting/<int:settingid>')
api.add_resource(SettingsAPI, '/v1/setting/list')
api.add_resource(SettingsaveAPI, '/v1/setting/save')

api.add_resource(AppAPI, '/v1/app/<int:appid>')
api.add_resource(ApplistAPI, '/v1/app/list')
api.add_resource(AppsaveAPI, '/v1/app/save')

api.add_resource(NotifylistAPI, '/v1/notify/list')

api.add_resource(InfotaskAPI, '/v1/info/task/<int:taskid>')
api.add_resource(InfoexecuteAPI, '/v1/info/execute/<int:executeid>')
api.add_resource(InfourlAPI, '/v1/info/url/<int:urlid>')
api.add_resource(InfourlbodyAPI, '/v1/info/url/body/<int:urlid>')

api.add_resource(SnapshotSaveAPI, '/v1/snapshot/save')

api.add_resource(NamelistSaveAPI, '/v1/namelist/save')
api.add_resource(NamelistListAPI, '/v1/namelist/list')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8001)