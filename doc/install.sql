drop table if exists app;
drop table if exists setting;
/* drop table if exists spider_url; */
/* drop table if exists spiderjs_url; */
drop table if exists site;
drop table if exists setting;
drop table if exists domain;
drop table if exists task;
drop table if exists task_execute;
drop table if exists task_notify;
drop table if exists task_piping;
drop table if exists task_piping_result;
drop table if exists task_piping_snapshot;
drop table if exists namelist_link;
drop table if exists piping_extend;
drop table if exists proxy;
drop table if exists dk_white_list;
drop table if exists dk_black_list;
drop table if exists sys_filterword;

CREATE TABLE app (
    id serial PRIMARY KEY,
    unique_key varchar(100) not null default '',
    public_key text not null default '',
    token varchar(200) not null default '',
    token_expired timestamp not null default LOCALTIMESTAMP(0),
    create_at timestamp not null default LOCALTIMESTAMP(0),
    update_at timestamp not null default LOCALTIMESTAMP(0)
);
comment on table app is '应用表';
comment on column app.id is '主键，自增ID期';
comment on column app.unique_key is '唯一标识符';
comment on column app.public_key is '公钥';
comment on column app.token is '当前token';
comment on column app.token_expired is 'token过期时间';
comment on column app.create_at is '创建时间';
comment on column app.update_at is '更新时间';


CREATE TABLE setting (
    id serial PRIMARY KEY,
    data_type varchar(10) not null default 'str',
    name varchar(50) not null default '',
    key varchar(200) not null default '',
    value text not null,
    note text not null,
    create_at timestamp not null default LOCALTIMESTAMP(0),
    update_at timestamp not null default LOCALTIMESTAMP(0)
);
comment on table setting is '配置表';
comment on column setting.id is '主键，自增ID期';
comment on column setting.data_type is '数据类型：str/json';
comment on column setting.name is '配置名称';
comment on column setting.key is 'k-v结构中的键名';
comment on column setting.value is 'k-v结构中的键值';
comment on column setting.note is '备注';
comment on column setting.create_at is '创建时间';
comment on column setting.update_at is '更新时间';


/* spider_url 表中的数据已经全部移到 mongodb 中 */
/*
CREATE TABLE spider_url (
    id serial PRIMARY KEY,
    site_id int not null default '0',
    task_id int not null default '0',
    app_id int not null default '0',
    execute_id int not null default '0',
    task_type varchar(10) not null default 'spider',
    url varchar(2048) not null default '',
    url_type varchar(10) not null default '',
    md5_url varchar(32) not null default '',
    file_name varchar(500) not null default '',
    file_path varchar(500) not null default '',
    file_extension varchar(10) not null default '',
    referer varchar(1000) not null default '',
    method varchar(10) not null default '',
    exec_level int not null default 0,
    depth int not null default '0',
    query text not null default '',
    post text not null default '',
    http_code varchar(3) not null default '',
    request_headers jsonb default null,
    response_headers jsonb default null,
    redirects jsonb default null,
    response_body_type varchar not null default '',
    body text not null default '',
    md5_body varchar(32) not null default '',
    pattern_path varchar(1000) not null default '',
    pattern_query varchar(1000) not null default '',
    pattern_post varchar(1000) not null default '',
    error varchar(1000) not null default '',
    status int not null default '0',
    start_at timestamp not null default LOCALTIMESTAMP(0),
    end_at timestamp not null default LOCALTIMESTAMP(0),
    create_at timestamp not null default LOCALTIMESTAMP(0),
    update_at timestamp not null default LOCALTIMESTAMP(0)
);
comment on table spider_url is 'URL抓取表';
comment on column spider_url.id is '主键，自增ID期';
comment on column spider_url.site_id is '站点ID';
comment on column spider_url.task_id is '任务ID';
comment on column spider_url.app_id is '第三方系统ID';
comment on column spider_url.execute_id is '执行ID';
comment on column spider_url.task_type is '任务类型: spider(蜘蛛)/mirror(镜像)/mirror_one(单页面镜像)/monitor(监控)/monitor_one(单页面监控)';
comment on column spider_url.url is '抓取的URL';
comment on column spider_url.url_type is 'url类型：self(当前域名下的链接)/child(子域名下的链接)/parent(父域名下的链接)/other(外部链接)';
comment on column spider_url.md5_url is 'url的md5值，url中包含query';
comment on column spider_url.file_name is '文件名';
comment on column spider_url.file_path is '文件路径';
comment on column spider_url.file_extension is '如果是文件，则取出文件后缀';
comment on column spider_url.referer is 'Referer';
comment on column spider_url.method is '请求的方式';
comment on column spider_url.exec_level is '执行级别,默认为0，越大越先执行';
comment on column spider_url.depth is '请求的深度';
comment on column spider_url.query is '请求的query';
comment on column spider_url.post is '请求的post参数';
comment on column spider_url.http_code is '服务器响应的状态码';
comment on column spider_url.request_headers is '请求头，json存储';
comment on column spider_url.response_headers is '响应头，json存储';
comment on column spider_url.redirects is '页面跳转数据, json格式存储';
comment on column spider_url.response_body_type is '响应体类型：html/img/cssjson';
comment on column spider_url.body is '响应的内容';
comment on column spider_url.md5_body is 'body的md5值';
comment on column spider_url.pattern_path is 'URL路径模式';
comment on column spider_url.pattern_query is 'query 模式';
comment on column spider_url.pattern_post is 'post 模式';
comment on column spider_url.error is '错误信息';
comment on column spider_url.status is '状态：0默认 1执行中 2结束 3异常';
comment on column spider_url.start_at is '开始时间';
comment on column spider_url.end_at is '结束时间';
comment on column spider_url.create_at is '创建时间';
comment on column spider_url.update_at is '更新时间';
*/

/* spiderjs_url数据全部移到 mongodb 中 */
/*
CREATE TABLE spiderjs_url (
    id serial PRIMARY KEY,
    url varchar(2048) not null default '',
    md5_url varchar(32) not null default '',
    referer varchar(1000) not null default '',
    method varchar(10) not null default '',
    http_code varchar(3) not null default '',
    request_headers jsonb default null,
    response_headers jsonb default null,
    redirects jsonb default null,
    body text not null default '',
    md5_body varchar(32) not null default '',
    parse_result text not null default '',
    error varchar(1000) not null default '',
    status int not null default '0',
    start_at timestamp not null default LOCALTIMESTAMP(0),
    end_at timestamp not null default LOCALTIMESTAMP(0),
    create_at timestamp not null default LOCALTIMESTAMP(0),
    update_at timestamp not null default LOCALTIMESTAMP(0)
);
comment on table spiderjs_url is 'URL抓取表';
comment on column spiderjs_url.id is '主键，自增ID期';
comment on column spiderjs_url.url is '抓取的URL';
comment on column spiderjs_url.md5_url is 'url的md5值，url中包含query';
comment on column spiderjs_url.referer is 'Referer';
comment on column spiderjs_url.method is '请求的方式';
comment on column spiderjs_url.http_code is '服务器响应的状态码';
comment on column spiderjs_url.request_headers is '请求头，json存储';
comment on column spiderjs_url.response_headers is '响应头，json存储';
comment on column spiderjs_url.redirects is '页面跳转数据, json格式存储';
comment on column spiderjs_url.body is '响应的内容';
comment on column spiderjs_url.md5_body is 'body的md5值';
comment on column spiderjs_url.parse_result is '解析结果';
comment on column spiderjs_url.error is '错误信息';
comment on column spiderjs_url.start_at is '开始时间';
comment on column spiderjs_url.end_at is '结束时间';
comment on column spiderjs_url.create_at is '创建时间';
comment on column spiderjs_url.update_at is '更新时间';
*/


CREATE TABLE site (
    id serial PRIMARY KEY,
    domain varchar(50) not null default '',
    note text not null default '',
    create_at timestamp not null default LOCALTIMESTAMP(0),
    update_at timestamp not null default LOCALTIMESTAMP(0)
);
comment on table site is '站点表，一个主域名是一个站点';
comment on column site.id is '主键，自增ID';
comment on column site.domain is '域名';
comment on column site.note is '备注';
comment on column site.create_at is '创建时间';
comment on column site.update_at is '更新时间';

CREATE TABLE domain (
    id serial PRIMARY KEY,
    site_id int not null default '0',
    domain varchar(50) not null default '',
    subdomain varchar(50) not null default '',
    create_at timestamp not null default LOCALTIMESTAMP(0),
    update_at timestamp not null default LOCALTIMESTAMP(0)
);
comment on table domain is '子域名表，域名从属于站点';
comment on column domain.id is '主键，自增ID';
comment on column domain.site_id is '站点ID';
comment on column domain.domain is '域名';
comment on column domain.create_at is '创建时间';
comment on column domain.update_at is '更新时间';


CREATE TABLE task (
    id serial PRIMARY KEY,
    app_id int not null default '0',
    site_id int not null default '0',
    type varchar(20) not null default 'spider',
    start_urls text not null,
    exec_level int not null default 0,
    limit_depth int not null default '0',
    limit_total int not null default '0',
    limit_time int not null default '0',
    limit_subdomain int not null default '0',
    limit_image int not null default '0',
    limit_js int not null default '0',
    limit_jsevent int not null default '0',
    exclude_urls text not null default '',
    url_unique_mode varchar(10) not null default 'url-query',
    notify_url varchar(300) not null default '',
    source_ip varchar(15) not null default '',
    proxies text not null default '',
    crontab varchar(100) not null default '',
    status int not null default '0',
    create_at timestamp not null default LOCALTIMESTAMP(0),
    update_at timestamp not null default LOCALTIMESTAMP(0)
);
comment on table task is '子域名表，域名从属于站点';
comment on column task.id is '主键，自增ID';
comment on column task.app_id is '第三方系统ID';
comment on column task.site_id is '站点ID';
comment on column task.type is '任务类型: spider(蜘蛛)/mirror(镜像)/mirror_one(单页面镜像)/monitor(监控)/monitor_one(单页面监测)';
comment on column task.start_urls is '入口URL';
comment on column task.exec_level is '执行级别,默认为0，越大越先执行';
comment on column task.limit_depth is '抓取深度';
comment on column task.limit_total is '抓取数量';
comment on column task.limit_time is '执行时长，单位：秒';
comment on column task.limit_subdomain is '是否抓取子域名：0否 1是';
comment on column task.limit_image is '抓取图片：1是 0否';
comment on column task.limit_js is '是否执行JS：0否 1是';
comment on column task.limit_jsevent is '是否模拟JS事件：0否 1是';
comment on column task.exclude_urls is '不抓取的url，以换行(\n)分隔';
comment on column task.url_unique_mode is 'URL去重模式：url只针对URL去重， url-query针对url及query去重';
comment on column task.notify_url is '任务结束或产生异常时的通知 URL';
comment on column task.source_ip is '源IP';
comment on column task.proxies is '代理';
comment on column task.crontab is '计划任务';
comment on column task.status is '执行状态:-1删除 0停用(默认) 1启用 2完成';
comment on column task.create_at is '创建时间';
comment on column task.update_at is '更新时间';


CREATE TABLE task_execute (
    id serial PRIMARY KEY,
    site_id int not null default 0,
    task_id int not null default 0,
    app_id int not null default 0,
    task_type varchar(20) not null default 'spider',
    start_urls text not null,
    exec_level int not null default 0,
    domain varchar(50) not null default '',
    limit_depth int not null default '0',
    limit_total int not null default '0',
    limit_time int not null default '0',
    limit_subdomain int not null default '0',
    limit_image int not null default '0',
    limit_js int not null default '0',
    limit_jsevent int not null default '0',
    exclude_urls text not null default '',
    url_unique_mode varchar(10) not null default 'url-query',
    notify_url varchar(300) not null default '',
    source_ip varchar(15) not null default '',
    proxies text not null default '',
    error text not null default '',
    status int not null default '0',
    start_at timestamp default null,
    end_at timestamp default null,
    create_at timestamp not null default LOCALTIMESTAMP(0),
    update_at timestamp not null default LOCALTIMESTAMP(0)
);
comment on table task_execute is '任务执行表';
comment on column task_execute.id is '主键，自增ID';
comment on column task_execute.site_id is '站点ID';
comment on column task_execute.task_id is '任务ID';
comment on column task_execute.app_id is '第三方系统ID';
comment on column task_execute.task_type is '任务类型: spider(蜘蛛)/mirror(镜像)/mirror_one(单页面镜像)/monitor(监控)/monitor_one(单页面监测)';
comment on column task_execute.start_urls is '入口URL';
comment on column task_execute.exec_level is '执行级别：默认为0，越大越先执行';
comment on column task_execute.domain is '任务对应的域名';
comment on column task_execute.limit_depth is '抓取深度';
comment on column task_execute.limit_total is '抓取数量';
comment on column task_execute.limit_time is '执行时长，单位：秒';
comment on column task_execute.limit_subdomain is '是否抓取子域名: 0否 1是';
comment on column task_execute.limit_image is '不抓取图片: 1是 0否';
comment on column task_execute.limit_js is '是否执行JS: 0否 1是';
comment on column task_execute.limit_jsevent is '是否模拟JS事件：0否 1是';
comment on column task_execute.exclude_urls is '不抓取的url，以换行(\n)分隔';
comment on column task_execute.url_unique_mode is 'URL去重模式: url只针对URL去重, url-query针对url及query去重';
comment on column task_execute.notify_url is '任务结束或产生异常时的通知 URL';
comment on column task_execute.source_ip is '源IP';
comment on column task_execute.proxies is '代理';
comment on column task_execute.error is '异常中止信息';
comment on column task_execute.status is '执行状态:0默认 1执行中 102暂停 101队列初始化 2完成 201中止 3异常';
comment on column task_execute.start_at is '开始时间';
comment on column task_execute.end_at is '结束时间';
comment on column task_execute.create_at is '创建时间';
comment on column task_execute.update_at is '更新时间';


CREATE TABLE task_notify (
    id serial PRIMARY KEY,
    site_id int not null default '0',
    task_id int not null default '0',
    app_id int not null default '0',
    execute_id int not null default '0',
    event_type varchar(50) not null default '',
    task_type varchar(20) not null default 'spider',
    notify_url varchar(300) not null default '',
    request_data text not null default '',
    response_data text not null default '',
    retry_times int not null default '0',
    error text not null default '',
    status int not null default '0',
    create_at timestamp not null default LOCALTIMESTAMP(0),
    update_at timestamp not null default LOCALTIMESTAMP(0)
);
comment on table task_notify is '任务通知表';
comment on column task_notify.id is '主键，自增ID';
comment on column task_notify.site_id is '站点ID';
comment on column task_notify.task_id is '任务ID';
comment on column task_notify.app_id is '第三方系统ID';
comment on column task_notify.execute_id is '执行ID';
comment on column task_notify.event_type is '事件类型:spider_ok,piping_filterword,piping_fingerprint,piping_keywor,piping_error_http_code,piping_ok';
comment on column task_notify.task_type is '任务类型: spider(蜘蛛)/mirror(镜像)/mirror_one(单页面镜像)/monitor(监控)/monitor_one(单页面监控)';
comment on column task_notify.notify_url is '通知URL';
comment on column task_notify.request_data is '请求的参数，JSON存储';
comment on column task_notify.response_data is '返回的数据';
comment on column task_notify.retry_times is '执行时长，单位：秒';
comment on column task_notify.error is '异常中止信息';
comment on column task_notify.status is '执行状态:0默认 1通知中 2完成 3异常';
comment on column task_notify.create_at is '创建时间';
comment on column task_notify.update_at is '更新时间';


CREATE TABLE proxy (
    id serial PRIMARY KEY,
    ip varchar(15) not null default 'spider',
    port int not null default '0',
    username varchar(50) not null default '',
    passwd varchar(50) not null default '',
    status int not null default '0',
    create_at timestamp not null default LOCALTIMESTAMP(0),
    update_at timestamp not null default LOCALTIMESTAMP(0)
);
comment on table proxy is '代理表';
comment on column proxy.id is '主键，自增ID';
comment on column proxy.ip is '代理IP';
comment on column proxy.port is '代理端口';
comment on column proxy.username is '用户名';
comment on column proxy.passwd is '密码';
comment on column proxy.status is '状态:0停用 1启用';
comment on column proxy.create_at is '创建时间';
comment on column proxy.update_at is '更新时间';


CREATE TABLE piping_extend (
    id serial PRIMARY KEY,
    app_id int not null default '0',
    site_id int not null default '0',
    task_id int not null default '0',
    piping_type varchar(20) not null default '',
    data text not null default '',
    status int not null default '0',
    create_at timestamp not null default LOCALTIMESTAMP(0),
    update_at timestamp not null default LOCALTIMESTAMP(0)
);
comment on table piping_extend is '词库表';
comment on column piping_extend.id is '主键，自增ID';
comment on column piping_extend.app_id is '应用ID';
comment on column piping_extend.site_id is '站点ID';
comment on column piping_extend.task_id is '任务ID';
comment on column piping_extend.piping_type is '类型：filterword(敏感词，过滤词) keyword(关键词)';
comment on column piping_extend.data is '扩展数据，根据每种扩展类型来定义存储格式';
comment on column piping_extend.status is '状态：0停用 1启用';
comment on column piping_extend.create_at is '创建时间';
comment on column piping_extend.update_at is '更新时间';


CREATE TABLE task_piping (
    id serial PRIMARY KEY,
    app_id int not null default '0',
    site_id int not null default '0',
    task_id int not null default '0',
    type varchar(20) not null default '',
    filterword_type varchar(10) not null default '',
    extend_id int not null default '0',
    status int not null default '0',
    create_at timestamp not null default LOCALTIMESTAMP(0),
    update_at timestamp not null default LOCALTIMESTAMP(0)
);
comment on table task_piping is '数据处理表';
comment on column task_piping.id is '主键，自增ID';
comment on column task_piping.app_id is '应用ID';
comment on column task_piping.site_id is '站点ID';
comment on column task_piping.task_id is '任务ID';
comment on column task_piping.type is '类型：fingerprint(指纹) trojan(木马) darklink(暗链) brokenlink(断链) filterwordword(敏感词) keyword(关键词)';
comment on column task_piping.filterword_type is '词库类型：system(系统词库) own(自有词库) mixed(混合词库)';
comment on column task_piping.extend_id is '扩展ID';
comment on column task_piping.status is '状态：0停用 1启用';
comment on column task_piping.create_at is '创建时间';
comment on column task_piping.update_at is '更新时间';


CREATE TABLE task_piping_result (
    id serial PRIMARY KEY,
    app_id int not null default '0',
    site_id int not null default '0',
    task_id int not null default '0',
    execute_id int not null default '0',
    piping_id int not null default '0',
    type varchar(20) not null default '',
    url varchar(1000) not null default '',
    result text not null default '',
    status int not null default '0',
    audit_status int not null default '0',
    create_at timestamp not null default LOCALTIMESTAMP(0),
    update_at timestamp not null default LOCALTIMESTAMP(0)
);
comment on table task_piping_result is '数据处理结果表';
comment on column task_piping_result.id is '主键，自增ID';
comment on column task_piping_result.app_id is '应用ID';
comment on column task_piping_result.site_id is '站点ID';
comment on column task_piping_result.task_id is '任务ID';
comment on column task_piping_result.piping_id is '管理ID';
comment on column task_piping_result.type is '类型：fingerprint(指纹) trojan(木马) darklink(暗链) brokenlink(断链) filterword(敏感词,过滤词) keyword(关键词)';
comment on column task_piping_result.url is 'URL';
comment on column task_piping_result.result is '处理结果，以json存储';
comment on column task_piping_result.status is '状态：0停用 1启用';
comment on column task_piping_result.audit_status is '状态：-1审核未通过 0默认 1审核通过';
comment on column task_piping_result.create_at is '创建时间';
comment on column task_piping_result.update_at is '更新时间';


CREATE TABLE task_piping_snapshot (
    id serial PRIMARY KEY,
    app_id int not null default '0',
    site_id int not null default '0',
    task_id int not null default '0',
    execute_id int not null default '0',
    piping_id int not null default '0',
    url_id int not null default '0',
    type varchar(20) not null default '',
    url varchar(1000) not null default '',
    snapshot text not null default '',
    result text not null default '',
    status int not null default '0',
    audit_status int not null default '0',
    create_at timestamp not null default LOCALTIMESTAMP(0),
    update_at timestamp not null default LOCALTIMESTAMP(0)
);
comment on table task_piping_snapshot is '快照表';
comment on column task_piping_snapshot.id is '主键，自增ID';
comment on column task_piping_snapshot.app_id is '应用ID';
comment on column task_piping_snapshot.site_id is '站点ID';
comment on column task_piping_snapshot.task_id is '任务ID';
comment on column task_piping_snapshot.piping_id is '管理ID';
comment on column task_piping_snapshot.url_id is '';
comment on column task_piping_snapshot.type is '类型：fingerprint(指纹) trojan(木马) darklink(暗链) brokenlink(断链) filterword(敏感词,过滤词) keyword(关键词)';
comment on column task_piping_snapshot.url is 'URL';
comment on column task_piping_snapshot.snapshot is '快照，图片路径';
comment on column task_piping_snapshot.result is '处理结果，以json存储';
comment on column task_piping_snapshot.status is '状态：0停用 1启用';
comment on column task_piping_snapshot.audit_status is '状态：-1审核未通过 0默认 1审核通过';
comment on column task_piping_snapshot.create_at is '创建时间';
comment on column task_piping_snapshot.update_at is '更新时间';

/*
alter table task alter column type type varchar(20);
alter table task_execute alter column task_type type varchar(20);
alter table task_notify alter column task_type type varchar(20);

alter table task add column exec_level int not null default 0;
alter table task_execute add column exec_level int not null default 0;
comment on column task.exec_level is '执行级别,默认为0，越大越先执行';
comment on column task_execute.exec_level is '执行级别,默认为0，越大越先执行';
*/


/*link_dark(暗链) link_outside(外链) link_black(黑链)*/
/*
CREATE TABLE link_outside (
    id serial PRIMARY KEY,
    app_id int not null default '0',
    site_id int not null default '0',
    task_id int not null default '0',
    execute_id int not null default '0',
    main varchar(100) not null default '',
    primary_domain varchar(100) not null default '',
    url varchar(1000) not null default '',
    md5_url char(32) not null default '',
    is_visible int not null default 0,
    create_at timestamp not null default LOCALTIMESTAMP(0),
    update_at timestamp not null default LOCALTIMESTAMP(0)
);
comment on table link_outside is '外部链接表';
comment on column link_outside.id is '应用ID';
comment on column link_outside.app_id is '应用ID';
comment on column link_outside.site_id is '站点ID';
comment on column link_outside.task_id is '任务ID';
comment on column link_outside.domain is '外链域名';
comment on column link_outside.primary_domain is '外链主域名';
comment on column link_outside.url is '外链';
comment on column link_outside.md5_url is '外链MD5';
comment on column link_outside.is_visible is '是否可见';
comment on column link_outside.create_at is '创建时间';
comment on column link_outside.update_at is '更新时间';
*/

CREATE TABLE namelist_link (
    id serial PRIMARY KEY,
    domain varchar(100) not null default '',
    primary_domain varchar(100) not null default '',
    list_type varchar(10) not null default '',
    scope varchar(10) not null default '',
    url varchar(1000) not null default '',
    status int not null default '0',
    create_at timestamp not null default LOCALTIMESTAMP(0),
    update_at timestamp not null default LOCALTIMESTAMP(0)
);
comment on table namelist_link is '链接名单';
comment on column namelist_link.id is '自增主键';
comment on column namelist_link.domain is '域名';
comment on column namelist_link.primary_domain is '主域名';
comment on column namelist_link.list_type is '连接类型: white(白名单)/black(黑名单)';
comment on column namelist_link.scope is '作用范围: global(全局) domain(域名)';
comment on column namelist_link.url is '链接';
comment on column namelist_link.status is '状态';
comment on column namelist_link.create_at is '创建时间';
comment on column namelist_link.update_at is '更新时间';


/*
CREATE TABLE cache_site (
    id serial PRIMARY KEY,
    domain varchar(2048) not null default '',
    primary_domain varchar(2048) not null default '',
    url varchar(2048) not null default '',
    url_type varchar(10) not null default '',
    md5_url varchar(32) not null default '',
    file_name varchar(500) not null default '',
    file_path varchar(500) not null default '',
    file_extension varchar(10) not null default '',
    referer varchar(1000) not null default '',
    method varchar(10) not null default '',
    query text not null default '',
    post text not null default '',
    http_code varchar(3) not null default '',
    request_headers jsonb default null,
    response_headers jsonb default null,
    redirects jsonb default null,
    response_body_type varchar not null default '',
    body text not null default '',
    md5_body varchar(32) not null default '',
    pattern_path varchar(1000) not null default '',
    pattern_query varchar(1000) not null default '',
    pattern_post varchar(1000) not null default '',
    start_at timestamp not null default LOCALTIMESTAMP(0),
    end_at timestamp not null default LOCALTIMESTAMP(0),
    expire_at timestamp not null default LOCALTIMESTAMP(0),
    create_at timestamp not null default LOCALTIMESTAMP(0),
);
comment on table cache_site is '站点缓存';
comment on column cache_site.id is '主键，自增ID';
comment on column cache_site.domain is '域名';
comment on column cache_site.primary_domain is '主域名';
comment on column cache_site.url is 'URL';
comment on column cache_site.url_type is 'URL类型';
comment on column cache_site.md5_url is 'URL的md5';
comment on column cache_site.file_name is '文件名';
comment on column cache_site.file_path is '文件路径';
comment on column cache_site.file_extension is '文件后缀';
comment on column cache_site.referer is 'referer';
comment on column cache_site.method is '请求方式';
comment on column cache_site.query is 'query';
comment on column cache_site.post is 'post数据';
comment on column cache_site.http_code is '响应状态码';
comment on column cache_site.request_headers is '请求头';
comment on column cache_site.response_headers is '响应头';
comment on column cache_site.redirects is '重定向跳转';
comment on column cache_site.response_body_type is '响应页面类型';
comment on column cache_site.body is '响应体';
comment on column cache_site.pattern_path is '路径模式';
comment on column cache_site.pattern_query is 'query模式';
comment on column cache_site.pattern_post is 'post模式';
comment on column cache_site.start_at is '开始时间';
comment on column cache_site.end_at is '结束时间';
comment on column cache_site.expire_at is '过期时间';
comment on column cache_site.create_at is '创建时间';


CREATE TABLE cache_browser_event (
    id serial PRIMARY KEY,
    domain varchar(2048) not null default '',
    primary_domain varchar(2048) not null default '',
    url varchar(2048) not null default '',
    url_type varchar(10) not null default '',
    md5_url varchar(32) not null default '',
    file_name varchar(500) not null default '',
    file_path varchar(500) not null default '',
    file_extension varchar(10) not null default '',
    referer varchar(1000) not null default '',
    method varchar(10) not null default '',
    query text not null default '',
    post text not null default '',
    http_code varchar(3) not null default '',
    request_headers jsonb default null,
    response_headers jsonb default null,
    redirects jsonb default null,
    response_body_type varchar not null default '',
    body text not null default '',
    md5_body varchar(32) not null default '',
    pattern_path varchar(1000) not null default '',
    pattern_query varchar(1000) not null default '',
    pattern_post varchar(1000) not null default '',
    event text not null default '',
    event_result text not null default '',
    start_at timestamp not null default LOCALTIMESTAMP(0),
    end_at timestamp not null default LOCALTIMESTAMP(0),
    expire_at timestamp not null default LOCALTIMESTAMP(0),
    create_at timestamp not null default LOCALTIMESTAMP(0),
);
comment on table cache_browser is '浏览器事件缓存';
comment on column cache_browser.id is '主键，自增ID';
comment on column cache_browser.domain is '域名';
comment on column cache_browser.primary_domain is '主域名';
comment on column cache_browser.url is 'URL';
comment on column cache_browser.url_type is 'URL类型';
comment on column cache_browser.md5_url is 'URL的md5';
comment on column cache_browser.file_name is '文件名';
comment on column cache_browser.file_path is '文件路径';
comment on column cache_browser.file_extension is '文件后缀';
comment on column cache_browser.referer is 'referer';
comment on column cache_browser.method is '请求方式';
comment on column cache_browser.query is 'query';
comment on column cache_browser.post is 'post数据';
comment on column cache_browser.http_code is '响应状态码';
comment on column cache_browser.request_headers is '请求头';
comment on column cache_browser.response_headers is '响应头';
comment on column cache_browser.redirects is '重定向跳转';
comment on column cache_browser.response_body_type is '响应页面类型';
comment on column cache_browser.body is '响应体';
comment on column cache_browser.pattern_path is '路径模式';
comment on column cache_browser.pattern_query is 'query模式';
comment on column cache_browser.pattern_post is 'post模式';
comment on column cache_browser.event is '事件';
comment on column cache_browser.event_result is '事件结果';
comment on column cache_browser.start_at is '开始时间';
comment on column cache_browser.end_at is '结束时间';
comment on column cache_browser.expire_at is '过期时间';
comment on column cache_browser.create_at is '创建时间';


CREATE TABLE service_snapshot (
    id serial PRIMARY KEY,
    app_key varchar(20) not null default '',
    batch_no varchar(20) not null default '',
    uuid varchar(20) not null default '',
    type varchar(20) not null default '',
    url varchar(1000) not null default '',
    filename varchar(200) not null default '',
    words varchar(200) not null default '',
    proxy varchar(1000) not null default '',
    snapshot text not null default '',
    callback_url varchar(1000) not null default '',
    error text not null default '',
    status int not null default '0',
    create_at timestamp not null default LOCALTIMESTAMP(0),
    update_at timestamp not null default LOCALTIMESTAMP(0)
);
comment on table  service_snapshot is '图片快照服务';
comment on column service_snapshot.id is '主键，自增ID';
comment on column service_snapshot.app_key is '应用唯一标识符';
comment on column service_snapshot.batch_no is '批次号，一个批次中可以有多个截图';
comment on column service_snapshot.uuid is '任务的UUID';
comment on column service_snapshot.type is '类型：code(代码截图)/browser(浏览器截图)';
comment on column service_snapshot.url is '代码或要截屏的URL';
comment on column service_snapshot.filename is '文件名';
comment on column service_snapshot.words is '包含的敏感词';
comment on column service_snapshot.proxy is '代理地址';
comment on column service_snapshot.snapshot is '快照，图片路径';
comment on column service_snapshot.callback_url is '回调地址';
comment on column service_snapshot.status is '状态：0未处理 1处理中 2成功 3处理异常';
comment on column service_snapshot.error is '异常信息';
comment on column service_snapshot.create_at is '创建时间';
comment on column service_snapshot.update_at is '更新时间';

CREATE TABLE piping_darklink (
    id serial PRIMARY KEY,
    site_id int not null default '0',
    task_id int not null default '0',
    app_id int not null default '0',
    execute_id int not null default '0',
    browser_result text not null default '',
    regular_result text not null default '',
    result text not null default '',
    start_at timestamp not null default LOCALTIMESTAMP(0),
    end_at timestamp not null default LOCALTIMESTAMP(0),
    create_at timestamp not null default LOCALTIMESTAMP(0),
    update_at timestamp not null default LOCALTIMESTAMP(0),
);
comment on table  piping_darklink is '暗链处理表';
comment on column piping_darklink.id is '主键，自增ID';
comment on column piping_darklink.site_id is '应用唯一标识符';
comment on column piping_darklink.task_id is '批次号，一个批次中可以有多个截图';
comment on column piping_darklink.app_id is '任务的UUID';
comment on column piping_darklink.execute_id is '类型：code(代码截图)/browser(浏览器截图)';
comment on column piping_darklink.browser_result is '类型：code(代码截图)/browser(浏览器截图)';
comment on column piping_darklink.regular_result is '类型：code(代码截图)/browser(浏览器截图)';
comment on column piping_darklink.result_result is '类型：code(代码截图)/browser(浏览器截图)';
comment on column piping_darklink.result_result is '类型：code(代码截图)/browser(浏览器截图)';
*/

CREATE TABLE dk_black_list (
     id serial PRIMARY KEY ,
     domain varchar(255) not null default'',
     create_at timestamp not null default LOCALTIMESTAMP(0),
     update_at timestamp not null default LOCALTIMESTAMP(0)
);
COMMENT ON TABLE dk_black_list IS '暗链黑名单表';
COMMENT ON COLUMN dk_black_list.id IS '主键，自增ID期';
COMMENT ON COLUMN dk_black_list.domain IS '黑名单名称';
COMMENT ON COLUMN dk_black_list.create_at IS '创建时间';
COMMENT ON COLUMN dk_black_list.update_at IS '更新时间';

CREATE TABLE dk_white_list (
     id serial PRIMARY KEY ,
     domain varchar(1000) not null default'',
     scope varchar(20) not null default'',
     create_at timestamp not null default LOCALTIMESTAMP(0),
     update_at timestamp not null default LOCALTIMESTAMP(0)
);
COMMENT ON TABLE dk_white_list IS '暗链白名单表';
COMMENT ON COLUMN dk_white_list.id IS '主键，自增ID期';
COMMENT ON COLUMN dk_white_list.domain IS '白名单域名';
COMMENT ON COLUMN dk_white_list.scope IS '白名单类型';
COMMENT ON COLUMN dk_white_list.create_at IS '创建时间';
COMMENT ON COLUMN dk_white_list.update_at IS '更新时间';

CREATE TABLE sys_filterword (
     id serial PRIMARY KEY ,
     name varchar(255) not null default'',
     "type" varchar(100) not null default'',
     "level" varchar(20) not null default'',
     create_at timestamp not null default LOCALTIMESTAMP(0),
     update_at timestamp not null default LOCALTIMESTAMP(0)
);
COMMENT ON TABLE sys_filterword IS '系统敏感词表';
COMMENT ON COLUMN sys_filterword.id IS '主键，自增ID期';
COMMENT ON COLUMN sys_filterword.name IS '敏感词域名';
COMMENT ON COLUMN sys_filterword."type" IS '敏感词类型';
COMMENT ON COLUMN sys_filterword."level" IS '敏感程度';
COMMENT ON COLUMN sys_filterword.create_at IS '创建时间';
COMMENT ON COLUMN sys_filterword.update_at IS '更新时间';