## postgres 常用操作



### 业务无关常用命令

#### 1. 查看postgres 时区
show time zone;

#### 2. 设置postgres 时区
set time zone 'Asia/Shanghai';

#### 3. 性能优化
#显示执行时间
\timing

#### 3. 锁查询
select a.locktype,a.database,a.pid,a.mode,a.relation,b.relname
from pg_locks a join pg_class b on a.relation = b.oid
where upper(b.relname) = 'TABLE_NAME';

http://blog.csdn.net/lengzijian/article/details/8133471

#### 4. 将SQL执行时间倒序排列
SELECT query, calls, total_time, rows, 100.0 * shared_blks_hit /nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent 
FROM pg_stat_statements 
ORDER BY total_time DESC LIMIT 5;

#### 5. 清空pg_statstatements的数据
SELECT pg_stat_statements_reset();

#### 6. 查看当前活跃的连接
select * from pg_stat_activity;

#### 7. 导出数据
pg_dump -h 127.0.0.1 -U postgres -s -E UTF8 spider > spider_struct.sql
pg_dump -h 127.0.0.1 -U postgres -a -E UTF8 --inserts spider > spider_data.sql







### 业务相关常用命令

#### 1. 查询两分钟之内的 URL
select count(1) as total from spider_url where u.status=1 and start_at - current_timestamp < interval '2 minute'

#### 2. 查看各状态统计
select status,count(1) as total from task_execute group by status order by status asc;

#### 3. 查看每日任务量
select cdate,count(1) as total 
from (select id,to_char(create_at, 'YYYYMMDD') as cdate from task_execute) t 
group by cdate order by cdate desc;

#### 4. 查看单个任务的计划任务
select task_id,cdate,count(1) as total 
from (
        select task_id,id,to_char(create_at, 'YYYYMMDD') as cdate from task_execute where task_id=500
    ) t 
group by task_id,cdate order by cdate desc;

#### 5. 查看表索引
select * from pg_indexes where tablename='task_notify';

