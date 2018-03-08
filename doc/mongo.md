## mongo 常用操作

### 常规操作

#### 1. 回收mongodb的空间
db.runCommand({compact:'spider'})

#### 2. 添加索引
db.spider.ensureIndex({"id":1},{"unique":true})
db.spider.ensureIndex({"task_id":1})

#### 3. mongodb 监控
mongostat -h 192.168.3.59:27017

#### 4. mongodb 监控
mongostat -h 172.16.100.229 -p 27017 --rowcount 20 1

#### 5. mongodb 监控，以 json 输出结果
mongostat -h 172.16.100.229 -p 27017 --rowcount 20 1 --json

#### 6. mongodb 导出
mongoexport -h 172.16.100.229 -p 27017 -d spider -c spiderurl -q '{"execute_id":{"$gte":8000, "$lt":10000}}' -o spiderurl_8000_10000.json

#### 7. mongodb 导入
mongoimport -h 172.16.100.229 -p 27017 -d spider -c spiderurl -j 8 spiderurl_8000_10000.json

#### 8. 执行JS 脚本
mongo 172.16.100.229/spider spider_index.js


### 慢查询

#### 1. 查询最近的10条记录
db.system.profile.find().limit(10).sort({ts: -1}).pretty()

#### 2. 返回所有的操作，除command类型的
db.system.profile.find({op:{$ne:'command'}}).pretty()

#### 3. 返回特定集合
db.system.profile.find({ns:'mydb.test'}).pretty()

#### 4. 返回大于5毫秒慢的操作
db.system.profile.find( { millis : { $gt : 5 } } ).pretty()

#### 5. 从一个特定的时间范围内返回信息
db.system.profile.find({ts : {
    $gt : new ISODate("2012-12-09T03:00:00Z") , 
    $lt : new ISODate("2012-12-09T03:40:00Z")}
    }).pretty()

#### 6. 特定时间，限制用户，按照消耗时间排序
db.system.profile.find(
    {ts: {
        $gt: new ISODate("2011-07-12T03:00:00Z"), 
        $lt: new ISODate("2011-07-12T03:40:00Z")
    }},
    {user : 0 }).sort( { millis : -1 } )

