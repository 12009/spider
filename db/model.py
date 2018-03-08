# coding: utf-8
from sqlalchemy.engine import Engine
from sqlalchemy import create_engine, select, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, Integer, MetaData, String, Table, Text, text
from config.config  import DB_PG_URL_SQL
from utils.logger import logger

metadata = MetaData()
engine = create_engine(DB_PG_URL_SQL)
#metadata = MetaData(engine)
Base = declarative_base()
Base.metadata.reflect(engine)
tables = Base.metadata.tables


t_app = Table(
    'app', metadata,
    Column('id', Integer, primary_key=True, server_default=text("nextval('app_id_seq'::regclass)")),
    Column('unique_key', String(100), nullable=False, server_default=text("''::character varying")),
    Column('public_key', Text, nullable=False, server_default=text("''::text")),
    Column('token', String(200), nullable=False, server_default=text("''::character varying")),
    Column('token_expired', DateTime, nullable=False, server_default=text("('now'::text)::timestamp(0) without time zone")),
    Column('create_at', DateTime, nullable=False, server_default=text("('now'::text)::timestamp(0) without time zone")),
    Column('update_at', DateTime, nullable=False, server_default=text("('now'::text)::timestamp(0) without time zone"))
)


t_domain = Table(
    'domain', metadata,
    Column('id', Integer, primary_key=True, server_default=text("nextval('domain_id_seq'::regclass)")),
    Column('site_id', Integer, nullable=False, server_default=text("0")),
    Column('domain', String(50), nullable=False, server_default=text("''::character varying")),
    Column('subdomain', String(50), nullable=False, server_default=text("''::character varying")),
    Column('create_at', DateTime, nullable=False, server_default=text("('now'::text)::timestamp(0) without time zone")),
    Column('update_at', DateTime, nullable=False, server_default=text("('now'::text)::timestamp(0) without time zone"))
)


t_namelist_link = Table(
    'namelist_link', metadata,
    Column('id', Integer, primary_key=True, server_default=text("nextval('namelist_link_id_seq'::regclass)")),
    Column('domain', String(100), nullable=False, server_default=text("''::character varying")),
    Column('primary_domain', String(100), nullable=False, server_default=text("''::character varying")),
    Column('list_type', String(10), nullable=False, server_default=text("''::character varying")),
    Column('scope', String(10), nullable=False, server_default=text("''::character varying")),
    Column('url', String(1000), nullable=False, server_default=text("''::character varying")),
    Column('status', Integer, nullable=False, server_default=text("0")),
    Column('create_at', DateTime, nullable=False, server_default=text("('now'::text)::timestamp(0) without time zone")),
    Column('update_at', DateTime, nullable=False, server_default=text("('now'::text)::timestamp(0) without time zone"))
)


t_piping_extend = Table(
    'piping_extend', metadata,
    Column('id', Integer, primary_key=True, server_default=text("nextval('piping_extend_id_seq'::regclass)")),
    Column('app_id', Integer, nullable=False, server_default=text("0")),
    Column('site_id', Integer, nullable=False, server_default=text("0")),
    Column('task_id', Integer, nullable=False, server_default=text("0")),
    Column('piping_type', String(20), nullable=False, server_default=text("''::character varying")),
    Column('data', Text, nullable=False, server_default=text("''::text")),
    Column('status', Integer, nullable=False, server_default=text("0")),
    Column('create_at', DateTime, nullable=False, server_default=text("('now'::text)::timestamp(0) without time zone")),
    Column('update_at', DateTime, nullable=False, server_default=text("('now'::text)::timestamp(0) without time zone"))
)


t_proxy = Table(
    'proxy', metadata,
    Column('id', Integer, primary_key=True, server_default=text("nextval('proxy_id_seq'::regclass)")),
    Column('ip', String(15), nullable=False, server_default=text("'spider'::bpchar")),
    Column('port', Integer, nullable=False, server_default=text("0")),
    Column('username', String(50), nullable=False, server_default=text("''::character varying")),
    Column('passwd', String(50), nullable=False, server_default=text("''::character varying")),
    Column('status', Integer, nullable=False, server_default=text("0")),
    Column('create_at', DateTime, nullable=False, server_default=text("('now'::text)::timestamp(0) without time zone")),
    Column('update_at', DateTime, nullable=False, server_default=text("('now'::text)::timestamp(0) without time zone"))
)


t_scheduler = Table(
    'scheduler', metadata,
    Column('id', String(191), primary_key=True),
    Column('name', String(100)),
    Column('func', String(500)),
    Column('args', String(500)),
    Column('kwargs', String(500)),
    Column('version', String(10)),
    Column('trigger_type', Text),
    Column('crontab', String(1000)),
    Column('interval', Integer),
    Column('run_date', DateTime(True)),
    Column('coalesce', Integer),
    Column('start_date', DateTime(True)),
    Column('end_date', DateTime(True)),
    Column('next_run_time', DateTime(True)),
    Column('max_instances', Integer),
    Column('executor', String(50)),
    Column('misfire_grace_time', Integer)
)


t_setting = Table(
    'setting', metadata,
    Column('id', Integer, primary_key=True, server_default=text("nextval('setting_id_seq'::regclass)")),
    Column('name', String(50), nullable=False, server_default=text("''::character varying")),
    Column('key', String(200), nullable=False, server_default=text("''::character varying")),
    Column('value', Text, nullable=False),
    Column('note', Text, nullable=False),
    Column('create_at', DateTime, nullable=False, server_default=text("('now'::text)::timestamp(0) without time zone")),
    Column('update_at', DateTime, nullable=False, server_default=text("('now'::text)::timestamp(0) without time zone")),
    Column('data_type', String(10), nullable=False, server_default=text("'str'::character varying"))
)


t_site = Table(
    'site', metadata,
    Column('id', Integer, primary_key=True, server_default=text("nextval('site_id_seq'::regclass)")),
    Column('domain', String(50), nullable=False, server_default=text("''::character varying")),
    Column('note', Text, nullable=False, server_default=text("''::text")),
    Column('create_at', DateTime, nullable=False, server_default=text("('now'::text)::timestamp(0) without time zone")),
    Column('update_at', DateTime, nullable=False, server_default=text("('now'::text)::timestamp(0) without time zone"))
)


t_task = Table(
    'task', metadata,
    Column('id', Integer, primary_key=True, server_default=text("nextval('task_id_seq'::regclass)")),
    Column('app_id', Integer, nullable=False, server_default=text("0")),
    Column('site_id', Integer, nullable=False, server_default=text("0")),
    Column('type', String(15), nullable=False, server_default=text("'spider'::character varying")),
    Column('start_urls', Text, nullable=False),
    Column('limit_depth', Integer, nullable=False, server_default=text("0")),
    Column('limit_total', Integer, nullable=False, server_default=text("0")),
    Column('limit_time', Integer, nullable=False, server_default=text("0")),
    Column('limit_subdomain', Integer, nullable=False, server_default=text("0")),
    Column('limit_image', Integer, nullable=False, server_default=text("0")),
    Column('limit_js', Integer, nullable=False, server_default=text("0")),
    Column('url_unique_mode', String(10), nullable=False, server_default=text("'url-query'::character varying")),
    Column('notify_url', String(300), nullable=False, server_default=text("''::character varying")),
    Column('source_ip', String(15), nullable=False, server_default=text("''::bpchar")),
    Column('proxies', Text, nullable=False, server_default=text("''::text")),
    Column('crontab', String(100), nullable=False, server_default=text("''::character varying")),
    Column('status', Integer, nullable=False, server_default=text("0")),
    Column('create_at', DateTime, nullable=False, server_default=text("('now'::text)::timestamp(0) without time zone")),
    Column('update_at', DateTime, nullable=False, server_default=text("('now'::text)::timestamp(0) without time zone")),
    Column('limit_jsevent', Integer, nullable=False, server_default=text("0")),
    Column('exclude_urls', Text, nullable=False, server_default=text("''::text"))
)


t_task_execute = Table(
    'task_execute', metadata,
    Column('id', Integer, primary_key=True, server_default=text("nextval('task_execute_id_seq'::regclass)")),
    Column('site_id', Integer, nullable=False, server_default=text("0")),
    Column('task_id', Integer, nullable=False, server_default=text("0")),
    Column('app_id', Integer, nullable=False, server_default=text("0")),
    Column('task_type', String(15), nullable=False, server_default=text("'spider'::character varying")),
    Column('start_urls', Text, nullable=False),
    Column('limit_depth', Integer, nullable=False, server_default=text("0")),
    Column('limit_total', Integer, nullable=False, server_default=text("0")),
    Column('limit_time', Integer, nullable=False, server_default=text("0")),
    Column('limit_subdomain', Integer, nullable=False, server_default=text("0")),
    Column('limit_image', Integer, nullable=False, server_default=text("0")),
    Column('limit_js', Integer, nullable=False, server_default=text("0")),
    Column('url_unique_mode', String(10), nullable=False, server_default=text("'url-query'::character varying")),
    Column('notify_url', String(300), nullable=False, server_default=text("''::character varying")),
    Column('source_ip', String(15), nullable=False, server_default=text("''::bpchar")),
    Column('proxies', Text, nullable=False, server_default=text("''::text")),
    Column('error', Text, nullable=False, server_default=text("''::text")),
    Column('status', Integer, nullable=False, server_default=text("0")),
    Column('start_at', DateTime),
    Column('end_at', DateTime),
    Column('create_at', DateTime, nullable=False, server_default=text("('now'::text)::timestamp(0) without time zone")),
    Column('update_at', DateTime, nullable=False, server_default=text("('now'::text)::timestamp(0) without time zone")),
    Column('domain', String(50), nullable=False, server_default=text("''::character varying")),
    Column('limit_jsevent', Integer, nullable=False, server_default=text("0")),
    Column('exclude_urls', Text, nullable=False, server_default=text("''::text"))
)


t_task_notify = Table(
    'task_notify', metadata,
    Column('id', Integer, primary_key=True, server_default=text("nextval('task_notify_id_seq'::regclass)")),
    Column('site_id', Integer, nullable=False, server_default=text("0")),
    Column('task_id', Integer, nullable=False, server_default=text("0")),
    Column('app_id', Integer, nullable=False, server_default=text("0")),
    Column('execute_id', Integer, nullable=False, server_default=text("0")),
    Column('task_type', String(10), nullable=False, server_default=text("'spider'::character varying")),
    Column('notify_url', String(300), nullable=False, server_default=text("''::character varying")),
    Column('request_data', Text, nullable=False, server_default=text("''::text")),
    Column('response_data', Text, nullable=False, server_default=text("''::text")),
    Column('retry_times', Integer, nullable=False, server_default=text("0")),
    Column('error', Text, nullable=False, server_default=text("''::text")),
    Column('status', Integer, nullable=False, server_default=text("0")),
    Column('create_at', DateTime, nullable=False, server_default=text("('now'::text)::timestamp(0) without time zone")),
    Column('update_at', DateTime, nullable=False, server_default=text("('now'::text)::timestamp(0) without time zone")),
    Column('event_type', String(50), nullable=False, server_default=text("''::character varying"))
)


t_task_piping = Table(
    'task_piping', metadata,
    Column('id', Integer, primary_key=True, server_default=text("nextval('task_piping_id_seq'::regclass)")),
    Column('app_id', Integer, nullable=False, server_default=text("0")),
    Column('site_id', Integer, nullable=False, server_default=text("0")),
    Column('task_id', Integer, nullable=False, server_default=text("0")),
    Column('type', String(20), nullable=False, server_default=text("''::character varying")),
    Column('filterword_type', String(10), nullable=False, server_default=text("''::character varying")),
    Column('extend_id', Integer, nullable=False, server_default=text("0")),
    Column('status', Integer, nullable=False, server_default=text("0")),
    Column('create_at', DateTime, nullable=False, server_default=text("('now'::text)::timestamp(0) without time zone")),
    Column('update_at', DateTime, nullable=False, server_default=text("('now'::text)::timestamp(0) without time zone"))
)


t_task_piping_result = Table(
    'task_piping_result', metadata,
    Column('id', Integer, primary_key=True, server_default=text("nextval('task_piping_result_id_seq'::regclass)")),
    Column('app_id', Integer, nullable=False, server_default=text("0")),
    Column('site_id', Integer, nullable=False, server_default=text("0")),
    Column('task_id', Integer, nullable=False, server_default=text("0")),
    Column('execute_id', Integer, nullable=False, server_default=text("0")),
    Column('piping_id', Integer, nullable=False, server_default=text("0")),
    Column('type', String(20), nullable=False, server_default=text("''::character varying")),
    Column('url', String(1000), nullable=False, server_default=text("''::character varying")),
    Column('result', Text, nullable=False, server_default=text("''::text")),
    Column('status', Integer, nullable=False, server_default=text("0")),
    Column('audit_status', Integer, nullable=False, server_default=text("0")),
    Column('create_at', DateTime, nullable=False, server_default=text("('now'::text)::timestamp(0) without time zone")),
    Column('update_at', DateTime, nullable=False, server_default=text("('now'::text)::timestamp(0) without time zone"))
)


t_task_piping_snapshot = Table(
    'task_piping_snapshot', metadata,
    Column('id', Integer, primary_key=True, server_default=text("nextval('task_piping_snapshot_id_seq'::regclass)")),
    Column('app_id', Integer, nullable=False, server_default=text("0")),
    Column('site_id', Integer, nullable=False, server_default=text("0")),
    Column('task_id', Integer, nullable=False, server_default=text("0")),
    Column('execute_id', Integer, nullable=False, server_default=text("0")),
    Column('piping_id', Integer, nullable=False, server_default=text("0")),
    Column('url_id', Integer, nullable=False, server_default=text("0")),
    Column('type', String(20), nullable=False, server_default=text("''::character varying")),
    Column('url', String(1000), nullable=False, server_default=text("''::character varying")),
    Column('snapshot', Text, nullable=False, server_default=text("''::character varying")),
    Column('result', Text, nullable=False, server_default=text("''::text")),
    Column('status', Integer, nullable=False, server_default=text("0")),
    Column('audit_status', Integer, nullable=False, server_default=text("0")),
    Column('create_at', DateTime, nullable=False, server_default=text("('now'::text)::timestamp(0) without time zone")),
    Column('update_at', DateTime, nullable=False, server_default=text("('now'::text)::timestamp(0) without time zone"))
)

# t_dk_filterword = Table(
#     'dk_filterword', metadata,
#     Column('id', Integer, primary_key=True, server_default=text("nextval('dk_filterword_id_seq'::regclass)")),
#     Column('url', String(255), nullable=False, server_default=text("''::character varying")),
#     Column('type', String(100), nullable=False, server_default=text("''::character varying")),
#     Column('level', String(20), nullable=False, server_default=text("''::character varying")),
#     Column('create_at', DateTime, nullable=False, server_default=text("('now'::text)::timestamp(0) without time zone")),
#     Column('update_at', DateTime, nullable=False, server_default=text("('now'::text)::timestamp(0) without time zone"))
# )


def insert_batch(table, records):
    ins = tables[table].insert().values(records)
    result = engine.execute(ins)
    return result.rowcount


def getbyid(table, id):
    wheres = {}
    if type(id) == tuple:
        field = id[0]
        wheres[id[0]] = id[1]
    else:
        field = 'id'
        wheres['id'] = id
    sql = 'select * from %s where %s=:%s' % (table, field, field)
    result = engine.execute(text(sql), wheres)
    row = result.first()
    return dict(row.items()) if row else None


def fetchone(sql, params = {}):
    result = engine.execute(text(sql), params)
    row = result.first()
    return dict(row.items()) if row else None

def fetchall(sql, params = {}):
    result = engine.execute(text(sql), params)
    rows = [dict(row.items()) for row in result]
    return rows


def insert(table, record):
    ins = tables[table].insert()

    result = engine.execute(ins, **record)

    return result.inserted_primary_key[0]


def exec(sql, params = {}):
    result = engine.execute(text(sql), params)
    return result.rowcount


def updatebyid(table, sets, id):
    wheres = {}
    if type(id) == tuple:
        field = id[0]
        wheres[id[0]] = id[1]
    else:
        field = 'id'
        wheres['id'] = id
    setStrs = [k + '=:' + k for k,v in sets.items()]
    sql = 'update ' + table + ' set ' + ','.join(setStrs) + ' where %s=:%s' % (field, field)
    result = engine.execute(text(sql), dict(sets, **wheres))
    return result.rowcount


def updatebyids(table, sets, ids):
    sqlIn = ''
    if type(ids) == tuple:
        field = ids[0]
        sqlIn = ",".join([str(i) for i in ids[1]])
    else:
        field = 'id'
        sqlIn = ",".join([str(i) for i in ids])
    setStrs = [k + '=:' + k for k,v in sets.items()]

    sql = 'update ' + table + ' set ' + ','.join(setStrs) + ' where %s in (%s)' % (field, sqlIn)
    result = engine.execute(text(sql), sets)
    return result.rowcount


