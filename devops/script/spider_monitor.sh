#!/bin/bash

#vim /etc/mail.rc
#set from=gitlab@yundun.com
#set smtp=smtp.exmail.qq.com
#set smtp-auth-user=gitlab@yundun.com
#set smtp-auth-password=YUNdun160718!
#set smtp-auth=login

err_uwsgi=$(tail -1 /tmp/spider/log/uwsgi.log | grep 'uWSGI listen queue of socket' | grep 'full !!!')
if [ -n "$err_uwsgi" ]; then
    echo 'uwsgi full !!!' | mail -s 'spider_error[uwsgi]' 438010680@qq.com
fi

err_mongo=$(mongo 172.16.100.229/mq --eval 'printjson(db.adminCommand("listDatabases"))' | grep failed)
if [ -n "$err_mongo" ]; then
    echo 'mongo connect failed !!!' | mail -s 'spider_error[mongo]' 438010680@qq.com
fi

