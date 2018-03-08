### 相关命令记录


状态位说明
所有的任务状态码为3位，如果后面是00，可以省略
0   初始化完成
1   执行中
101 消息队列初始化完成
2   抓取完成
3   异常
4   表示数据处理完成状态

casperjs 1.1.4 版本
phantomjs 2.1.1 版本


任务数据处理
{"task_id":6, "pipings":[{"type": "fingerprint", "status": 1}, {"type": "filterword", "filterwords":"习近平\n中共\n简洁\n直观", "filterword_type":"mixed", "filterword_operate":"plus", "status": 1}, {"type": "keyword", "keywords": [{"url":"http://local.com/spider.html", "words":["CDN", "云平台", "安全"]}], "status": 1}, {"type": "error_http_code", "http_codes": "403\n404\n405\n406\n500\n501\n502\n503\n504", "status": 1}]}

