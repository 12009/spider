#!/bin/bash

action=$1

cd /data/wwwpython/spider/
pyBin="/data/pyenv/env35/bin/python3.5"
uwsgiBin='/data/pyenv/env35/bin/uwsgi'

if [[ "${action}" == "start" ]]; then
   nohup ./golang/dfs_server -config ./golang/server.json &
   ${uwsgiBin} --ini /data/devops/etc/uwsgi_spider.ini
   nohup ${pyBin} djmanage.py celery beat -l debug >> /tmp/spider/log/celery_beat.log &
   nohup ${pyBin} djmanage.py celery worker -A dj.celery -l debug -c 10 -n api_default -Q default >> /tmp/spider/log/celery_default.log &
   nohup ${pyBin} djmanage.py celery flower --address=0.0.0.0 --port=5555 &
   nohup ${pyBin} /data/wwwpython/spider/ctl.py >> /tmp/spider/log/ctl.log &
   sleep 8
   echo started
else
   pids=$(ps -ef | grep dfs_server | grep -v grep | awk '{print $2}') && [[ $pids>0 ]] && kill -9 $pids || echo dfs_server_norunning
   pids=$(ps -ef | grep celery | grep -v grep | awk '{print $2}') && [[ $pids>0 ]] && kill -9 $pids || echo celery_norunning
   pids=$(ps -ef | grep spider- | grep -v grep | awk '{print $2}') && [[ $pids>0 ]] && kill -9 $pids || echo spider_norunning
   pids=$(ps -ef | grep uwsgi | grep -v grep | awk '{print $2}') && [[ $pids>0 ]] && kill -9 $pids || echo uwsgi_norunning
   echo stoped
fi
