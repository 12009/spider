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
{"task_id":1, "pipings":[{"type": "fingerprint", "status": 1}, {"type": "filterword", "filterwords":"习近平\n中共\n简洁\n直观", "filterword_type":"mixed", "filterword_operate":"plus", "status": 1}, {"type": "keyword", "keywords": [{"url":"http://local.com/spider.html", "words":["CDN", "云平台", "安全"]}], "status": 1}, {"type": "error_http_code", "http_codes": "403\n404\n405\n406\n500\n501\n502\n503\n504", "status": 1}]}


# 项目中使用到的库或者模块
beautifulsoup4
flask(Flask,session)
flask-restful
lxml
html5lib
lxml
redis
psycopg2
sqlalchemy
pymongo
setproctitle
apscheduler
rsa
qiniu
numpy
ipython


## About sublists

sublists is a python tool designed to enumerate subdomains of websites using OSINT. It helps penetration testers and bug hunters collect and gather subdomains for the domain they are targeting. Sublist3r enumerates subdomains using many search engines such as Google, Yahoo, Bing, Baidu, and Ask. Sublist3r also enumerates subdomains using Netcraft, Virustotal, ThreatCrowd, DNSdumpster, and ReverseDNS.

[subbrute](https://github.com/TheRook/subbrute) was integrated with sublists to increase the possibility of finding more subdomains using bruteforce with an improved wordlist. The credit goes to TheRook who is the author of subbrute.


## Recommended Python Version:

sublists currently supports **Python 2** and **Python 3**.

* The recommended version for Python 2 is **2.7.x**
* The recommened version for Python 3 is **3.4.x**

## Dependencies:

sublists depends on the `requests`, `dnspython`, and `argparse` python modules.

These dependencies can be installed using the requirements file:

```
- Installation on Linux
```
sudo pip install -r requirements.txt
```

Alternatively, each module can be installed independently as shown below.

#### Requests Module (http://docs.python-requests.org/en/latest/)

- Install for Ubuntu/Debian:
```
sudo apt-get install python-requests
```

- Install for Centos/Redhat:
```
sudo yum install python-requests
```

- Install using pip on Linux:
```
sudo pip install requests
```

#### dnspython Module (http://www.dnspython.org/)

- Install for Windows:
```
c:\python27\python.exe -m pip install dnspython
```

- Install for Ubuntu/Debian:
```
sudo apt-get install python-dnspython
```

- Install using pip:
```
sudo pip install dnspython
```

#### argparse Module

- Install for Ubuntu/Debian:
```
sudo apt-get install python-argparse
```

- Install for Centos/Redhat:
```
sudo yum install python-argparse
```

- Install using pip:
```
sudo pip install argparse
```

**for coloring in windows install the following libraries**
```
c:\python27\python.exe -m pip install win_unicode_console colorama


**Function Usage:**
* **domain**: The domain you want to enumerate subdomains of.
* **savefile**: save the output into text file.
* **ports**: specify a comma-sperated list of the tcp ports to scan.
* **silent**: set sublist3r to work in silent mode during the execution (helpful when you don't need a lot of noise).
* **verbose**: display the found subdomains in real time.
* **enable_bruteforce**: enable the bruteforce module.
* **engines**: (Optional) to choose specific engines.