--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.2
-- Dumped by pg_dump version 9.6.2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


--
-- Name: zhparser; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS zhparser WITH SCHEMA public;


--
-- Name: EXTENSION zhparser; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION zhparser IS 'a parser for full-text search of Chinese';


SET search_path = public, pg_catalog;

--
-- Name: testzhcfg; Type: TEXT SEARCH CONFIGURATION; Schema: public; Owner: postgres
--

CREATE TEXT SEARCH CONFIGURATION testzhcfg (
    PARSER = zhparser );

ALTER TEXT SEARCH CONFIGURATION testzhcfg
    ADD MAPPING FOR a WITH simple;

ALTER TEXT SEARCH CONFIGURATION testzhcfg
    ADD MAPPING FOR e WITH simple;

ALTER TEXT SEARCH CONFIGURATION testzhcfg
    ADD MAPPING FOR i WITH simple;

ALTER TEXT SEARCH CONFIGURATION testzhcfg
    ADD MAPPING FOR l WITH simple;

ALTER TEXT SEARCH CONFIGURATION testzhcfg
    ADD MAPPING FOR n WITH simple;

ALTER TEXT SEARCH CONFIGURATION testzhcfg
    ADD MAPPING FOR v WITH simple;


ALTER TEXT SEARCH CONFIGURATION testzhcfg OWNER TO postgres;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: app; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE app (
    id integer NOT NULL,
    unique_key character varying(100) DEFAULT ''::character varying NOT NULL,
    public_key text DEFAULT ''::text NOT NULL,
    token character varying(200) DEFAULT ''::character varying NOT NULL,
    token_expired timestamp without time zone DEFAULT ('now'::text)::timestamp(0) without time zone NOT NULL,
    create_at timestamp without time zone DEFAULT ('now'::text)::timestamp(0) without time zone NOT NULL,
    update_at timestamp without time zone DEFAULT ('now'::text)::timestamp(0) without time zone NOT NULL
);


ALTER TABLE app OWNER TO postgres;

--
-- Name: TABLE app; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE app IS '应用表';


--
-- Name: COLUMN app.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN app.id IS '主键，自增ID期';


--
-- Name: COLUMN app.unique_key; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN app.unique_key IS '唯一标识符';


--
-- Name: COLUMN app.public_key; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN app.public_key IS '公钥';


--
-- Name: COLUMN app.token; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN app.token IS '当前token';


--
-- Name: COLUMN app.token_expired; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN app.token_expired IS 'token过期时间';


--
-- Name: COLUMN app.create_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN app.create_at IS '创建时间';


--
-- Name: COLUMN app.update_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN app.update_at IS '更新时间';


--
-- Name: app_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE app_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE app_id_seq OWNER TO postgres;

--
-- Name: app_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE app_id_seq OWNED BY app.id;


--
-- Name: domain; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE domain (
    id integer NOT NULL,
    site_id integer DEFAULT 0 NOT NULL,
    domain character varying(50) DEFAULT ''::character varying NOT NULL,
    subdomain character varying(50) DEFAULT ''::character varying NOT NULL,
    create_at timestamp without time zone DEFAULT ('now'::text)::timestamp(0) without time zone NOT NULL,
    update_at timestamp without time zone DEFAULT ('now'::text)::timestamp(0) without time zone NOT NULL
);


ALTER TABLE domain OWNER TO postgres;

--
-- Name: TABLE domain; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE domain IS '子域名表，域名从属于站点';


--
-- Name: COLUMN domain.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN domain.id IS '主键，自增ID';


--
-- Name: COLUMN domain.site_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN domain.site_id IS '站点ID';


--
-- Name: COLUMN domain.domain; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN domain.domain IS '域名';


--
-- Name: domain_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE domain_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE domain_id_seq OWNER TO postgres;

--
-- Name: domain_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE domain_id_seq OWNED BY domain.id;


--
-- Name: namelist_link; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE namelist_link (
    id integer NOT NULL,
    domain character varying(100) DEFAULT ''::character varying NOT NULL,
    primary_domain character varying(100) DEFAULT ''::character varying NOT NULL,
    list_type character varying(10) DEFAULT ''::character varying NOT NULL,
    scope character varying(10) DEFAULT ''::character varying NOT NULL,
    url character varying(1000) DEFAULT ''::character varying NOT NULL,
    status integer DEFAULT 0 NOT NULL,
    create_at timestamp without time zone DEFAULT ('now'::text)::timestamp(0) without time zone NOT NULL,
    update_at timestamp without time zone DEFAULT ('now'::text)::timestamp(0) without time zone NOT NULL
);


ALTER TABLE namelist_link OWNER TO postgres;

--
-- Name: TABLE namelist_link; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE namelist_link IS '链接名单';


--
-- Name: COLUMN namelist_link.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN namelist_link.id IS '自增主键';


--
-- Name: COLUMN namelist_link.domain; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN namelist_link.domain IS '域名';


--
-- Name: COLUMN namelist_link.primary_domain; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN namelist_link.primary_domain IS '主域名';


--
-- Name: COLUMN namelist_link.list_type; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN namelist_link.list_type IS '连接类型: white(白名单)/black(黑名单)';


--
-- Name: COLUMN namelist_link.scope; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN namelist_link.scope IS '作用范围: global(全局) domain(域名)';


--
-- Name: COLUMN namelist_link.url; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN namelist_link.url IS '链接';


--
-- Name: COLUMN namelist_link.status; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN namelist_link.status IS '状态';


--
-- Name: COLUMN namelist_link.create_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN namelist_link.create_at IS '创建时间';


--
-- Name: COLUMN namelist_link.update_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN namelist_link.update_at IS '更新时间';


--
-- Name: namelist_link_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE namelist_link_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE namelist_link_id_seq OWNER TO postgres;

--
-- Name: namelist_link_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE namelist_link_id_seq OWNED BY namelist_link.id;


--
-- Name: piping_extend; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE piping_extend (
    id integer NOT NULL,
    app_id integer DEFAULT 0 NOT NULL,
    site_id integer DEFAULT 0 NOT NULL,
    task_id integer DEFAULT 0 NOT NULL,
    piping_type character varying(20) DEFAULT ''::character varying NOT NULL,
    data text DEFAULT ''::text NOT NULL,
    status integer DEFAULT 0 NOT NULL,
    create_at timestamp without time zone DEFAULT ('now'::text)::timestamp(0) without time zone NOT NULL,
    update_at timestamp without time zone DEFAULT ('now'::text)::timestamp(0) without time zone NOT NULL
);


ALTER TABLE piping_extend OWNER TO postgres;

--
-- Name: TABLE piping_extend; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE piping_extend IS '词库表';


--
-- Name: COLUMN piping_extend.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN piping_extend.id IS '主键，自增ID';


--
-- Name: COLUMN piping_extend.app_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN piping_extend.app_id IS '应用ID';


--
-- Name: COLUMN piping_extend.site_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN piping_extend.site_id IS '站点ID';


--
-- Name: COLUMN piping_extend.task_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN piping_extend.task_id IS '任务ID';


--
-- Name: COLUMN piping_extend.status; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN piping_extend.status IS '状态：0停用 1启用';


--
-- Name: COLUMN piping_extend.create_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN piping_extend.create_at IS '创建时间';


--
-- Name: COLUMN piping_extend.update_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN piping_extend.update_at IS '更新时间';


--
-- Name: piping_extend_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE piping_extend_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE piping_extend_id_seq OWNER TO postgres;

--
-- Name: piping_extend_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE piping_extend_id_seq OWNED BY piping_extend.id;


--
-- Name: proxy; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE proxy (
    id integer NOT NULL,
    ip character(15) DEFAULT 'spider'::bpchar NOT NULL,
    port integer DEFAULT 0 NOT NULL,
    username character varying(50) DEFAULT ''::character varying NOT NULL,
    passwd character varying(50) DEFAULT ''::character varying NOT NULL,
    status integer DEFAULT 0 NOT NULL,
    create_at timestamp without time zone DEFAULT ('now'::text)::timestamp(0) without time zone NOT NULL,
    update_at timestamp without time zone DEFAULT ('now'::text)::timestamp(0) without time zone NOT NULL
);


ALTER TABLE proxy OWNER TO postgres;

--
-- Name: TABLE proxy; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE proxy IS '代理表';


--
-- Name: COLUMN proxy.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN proxy.id IS '主键，自增ID';


--
-- Name: COLUMN proxy.ip; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN proxy.ip IS '代理IP';


--
-- Name: COLUMN proxy.port; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN proxy.port IS '代理端口';


--
-- Name: COLUMN proxy.username; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN proxy.username IS '用户名';


--
-- Name: COLUMN proxy.passwd; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN proxy.passwd IS '密码';


--
-- Name: COLUMN proxy.status; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN proxy.status IS '状态:0停用 1启用';


--
-- Name: COLUMN proxy.create_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN proxy.create_at IS '创建时间';


--
-- Name: COLUMN proxy.update_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN proxy.update_at IS '更新时间';


--
-- Name: proxy_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE proxy_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE proxy_id_seq OWNER TO postgres;

--
-- Name: proxy_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE proxy_id_seq OWNED BY proxy.id;


--
-- Name: scheduler; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE scheduler (
    id character varying(191) NOT NULL,
    name character varying(100),
    func character varying(500),
    args character varying(500),
    kwargs character varying(500),
    version character varying(10),
    trigger_type text,
    crontab character varying(1000),
    "interval" integer,
    run_date timestamp with time zone,
    "coalesce" integer,
    start_date timestamp with time zone,
    end_date timestamp with time zone,
    next_run_time timestamp with time zone,
    max_instances integer,
    executor character varying(50),
    misfire_grace_time integer
);


ALTER TABLE scheduler OWNER TO postgres;

--
-- Name: setting; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE setting (
    id integer NOT NULL,
    name character varying(50) DEFAULT ''::character varying NOT NULL,
    key character varying(200) DEFAULT ''::character varying NOT NULL,
    value text NOT NULL,
    note text NOT NULL,
    create_at timestamp without time zone DEFAULT ('now'::text)::timestamp(0) without time zone NOT NULL,
    update_at timestamp without time zone DEFAULT ('now'::text)::timestamp(0) without time zone NOT NULL,
    data_type character varying(10) DEFAULT 'str'::character varying NOT NULL
);


ALTER TABLE setting OWNER TO postgres;

--
-- Name: TABLE setting; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE setting IS '配置表';


--
-- Name: COLUMN setting.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN setting.id IS '主键，自增ID期';


--
-- Name: COLUMN setting.name; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN setting.name IS '配置名称';


--
-- Name: COLUMN setting.key; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN setting.key IS 'k-v结构中的键名';


--
-- Name: COLUMN setting.value; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN setting.value IS 'k-v结构中的键值';


--
-- Name: COLUMN setting.note; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN setting.note IS '备注';


--
-- Name: COLUMN setting.create_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN setting.create_at IS '创建时间';


--
-- Name: COLUMN setting.update_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN setting.update_at IS '更新时间';


--
-- Name: COLUMN setting.data_type; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN setting.data_type IS '数据类型：str/json';


--
-- Name: setting_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE setting_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE setting_id_seq OWNER TO postgres;

--
-- Name: setting_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE setting_id_seq OWNED BY setting.id;


--
-- Name: site; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE site (
    id integer NOT NULL,
    domain character varying(50) DEFAULT ''::character varying NOT NULL,
    note text DEFAULT ''::text NOT NULL,
    create_at timestamp without time zone DEFAULT ('now'::text)::timestamp(0) without time zone NOT NULL,
    update_at timestamp without time zone DEFAULT ('now'::text)::timestamp(0) without time zone NOT NULL
);


ALTER TABLE site OWNER TO postgres;

--
-- Name: TABLE site; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE site IS '站点表，一个主域名是一个站点';


--
-- Name: COLUMN site.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN site.id IS '主键，自增ID';


--
-- Name: COLUMN site.domain; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN site.domain IS '域名';


--
-- Name: COLUMN site.note; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN site.note IS '备注';


--
-- Name: COLUMN site.create_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN site.create_at IS '创建时间';


--
-- Name: COLUMN site.update_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN site.update_at IS '更新时间';


--
-- Name: site_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE site_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE site_id_seq OWNER TO postgres;

--
-- Name: site_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE site_id_seq OWNED BY site.id;


--
-- Name: spider_url; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE spider_url (
    id integer NOT NULL,
    site_id integer DEFAULT 0 NOT NULL,
    task_id integer DEFAULT 0 NOT NULL,
    app_id integer DEFAULT 0 NOT NULL,
    execute_id integer DEFAULT 0 NOT NULL,
    task_type character varying(15) DEFAULT 'spider'::character varying NOT NULL,
    url character varying(2048) DEFAULT ''::character varying NOT NULL,
    md5_url character(32) DEFAULT ''::bpchar NOT NULL,
    method character varying(10) DEFAULT ''::character varying NOT NULL,
    depth integer DEFAULT 0 NOT NULL,
    status integer DEFAULT 0 NOT NULL,
    create_at timestamp without time zone DEFAULT ('now'::text)::timestamp(0) without time zone NOT NULL,
    update_at timestamp without time zone DEFAULT ('now'::text)::timestamp(0) without time zone NOT NULL,
    start_at timestamp without time zone DEFAULT ('now'::text)::timestamp(0) without time zone NOT NULL,
    end_at timestamp without time zone DEFAULT ('now'::text)::timestamp(0) without time zone NOT NULL
);


ALTER TABLE spider_url OWNER TO postgres;

--
-- Name: TABLE spider_url; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE spider_url IS 'URL抓取表';


--
-- Name: COLUMN spider_url.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN spider_url.id IS '主键，自增ID期';


--
-- Name: COLUMN spider_url.site_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN spider_url.site_id IS '站点ID';


--
-- Name: COLUMN spider_url.task_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN spider_url.task_id IS '任务ID';


--
-- Name: COLUMN spider_url.app_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN spider_url.app_id IS '第三方系统ID';


--
-- Name: COLUMN spider_url.execute_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN spider_url.execute_id IS '执行ID';


--
-- Name: COLUMN spider_url.task_type; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN spider_url.task_type IS '任务类型: spider(蜘蛛)/mirror(镜像)/monitor(监控)';


--
-- Name: COLUMN spider_url.url; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN spider_url.url IS '抓取的URL';


--
-- Name: COLUMN spider_url.md5_url; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN spider_url.md5_url IS 'url的md5值，url中包含query';


--
-- Name: COLUMN spider_url.method; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN spider_url.method IS '请求的方式';


--
-- Name: COLUMN spider_url.depth; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN spider_url.depth IS '请求的深度';


--
-- Name: COLUMN spider_url.status; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN spider_url.status IS '状态：0默认 1执行中 2结束';


--
-- Name: COLUMN spider_url.create_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN spider_url.create_at IS '创建时间';


--
-- Name: COLUMN spider_url.update_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN spider_url.update_at IS '更新时间';


--
-- Name: COLUMN spider_url.start_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN spider_url.start_at IS '开始时间';


--
-- Name: COLUMN spider_url.end_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN spider_url.end_at IS '结束时间';


--
-- Name: spider_url_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE spider_url_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE spider_url_id_seq OWNER TO postgres;

--
-- Name: spider_url_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE spider_url_id_seq OWNED BY spider_url.id;


--
-- Name: spiderjs_url; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE spiderjs_url (
    id integer NOT NULL,
    url character varying(2048) DEFAULT ''::character varying NOT NULL,
    md5_url character varying(32) DEFAULT ''::character varying NOT NULL,
    referer character varying(1000) DEFAULT ''::character varying NOT NULL,
    method character varying(10) DEFAULT ''::character varying NOT NULL,
    request_headers jsonb,
    status integer DEFAULT 0 NOT NULL,
    start_at timestamp without time zone DEFAULT ('now'::text)::timestamp(0) without time zone NOT NULL,
    end_at timestamp without time zone DEFAULT ('now'::text)::timestamp(0) without time zone NOT NULL,
    create_at timestamp without time zone DEFAULT ('now'::text)::timestamp(0) without time zone NOT NULL
);


ALTER TABLE spiderjs_url OWNER TO postgres;

--
-- Name: spiderjs_url_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE spiderjs_url_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE spiderjs_url_id_seq OWNER TO postgres;

--
-- Name: spiderjs_url_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE spiderjs_url_id_seq OWNED BY spiderjs_url.id;


--
-- Name: task; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE task (
    id integer NOT NULL,
    app_id integer DEFAULT 0 NOT NULL,
    site_id integer DEFAULT 0 NOT NULL,
    type character varying(15) DEFAULT 'spider'::character varying NOT NULL,
    start_urls text NOT NULL,
    limit_depth integer DEFAULT 0 NOT NULL,
    limit_total integer DEFAULT 0 NOT NULL,
    limit_time integer DEFAULT 0 NOT NULL,
    limit_subdomain integer DEFAULT 0 NOT NULL,
    limit_image integer DEFAULT 0 NOT NULL,
    limit_js integer DEFAULT 0 NOT NULL,
    url_unique_mode character varying(10) DEFAULT 'url-query'::character varying NOT NULL,
    notify_url character varying(300) DEFAULT ''::character varying NOT NULL,
    source_ip character(15) DEFAULT ''::bpchar NOT NULL,
    proxies text DEFAULT ''::text NOT NULL,
    crontab character varying(100) DEFAULT ''::character varying NOT NULL,
    status integer DEFAULT 0 NOT NULL,
    create_at timestamp without time zone DEFAULT ('now'::text)::timestamp(0) without time zone NOT NULL,
    update_at timestamp without time zone DEFAULT ('now'::text)::timestamp(0) without time zone NOT NULL,
    limit_jsevent integer DEFAULT 0 NOT NULL,
    exclude_urls text DEFAULT ''::text NOT NULL,
    exec_level integer DEFAULT 0 NOT NULL
);


ALTER TABLE task OWNER TO postgres;

--
-- Name: TABLE task; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE task IS '子域名表，域名从属于站点';


--
-- Name: COLUMN task.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task.id IS '主键，自增ID';


--
-- Name: COLUMN task.app_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task.app_id IS '第三方系统ID';


--
-- Name: COLUMN task.site_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task.site_id IS '站点ID';


--
-- Name: COLUMN task.type; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task.type IS '任务类型: spider(蜘蛛)/mirror(镜像)/monitor(监控)';


--
-- Name: COLUMN task.start_urls; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task.start_urls IS '入口URL';


--
-- Name: COLUMN task.limit_depth; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task.limit_depth IS '抓取深度';


--
-- Name: COLUMN task.limit_total; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task.limit_total IS '抓取数量';


--
-- Name: COLUMN task.limit_time; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task.limit_time IS '执行时长，单位：秒';


--
-- Name: COLUMN task.limit_subdomain; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task.limit_subdomain IS '是否抓取子域名：0否 1是';


--
-- Name: COLUMN task.limit_image; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task.limit_image IS '不抓取图片：1是 0否';


--
-- Name: COLUMN task.limit_js; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task.limit_js IS '是否执行JS：0否 1是';


--
-- Name: COLUMN task.url_unique_mode; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task.url_unique_mode IS 'URL去重模式：url只针对URL去重， url-query针对url及query去重';


--
-- Name: COLUMN task.notify_url; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task.notify_url IS '任务结束或产生异常时的通知 URL';


--
-- Name: COLUMN task.source_ip; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task.source_ip IS '源IP';


--
-- Name: COLUMN task.proxies; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task.proxies IS '代理';


--
-- Name: COLUMN task.crontab; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task.crontab IS '计划任务';


--
-- Name: COLUMN task.status; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task.status IS '执行状态:0默认 1执行中 101暂停 2完成 201中止 3异常';


--
-- Name: COLUMN task.create_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task.create_at IS '创建时间';


--
-- Name: COLUMN task.update_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task.update_at IS '更新时间';


--
-- Name: COLUMN task.limit_jsevent; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task.limit_jsevent IS '是否模拟JS事件：0否 1是';


--
-- Name: COLUMN task.exclude_urls; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task.exclude_urls IS '不抓取的url，以换行(\n)分隔';


--
-- Name: COLUMN task.exec_level; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task.exec_level IS '执行级别,默认为0，越大越先执行';


--
-- Name: task_execute; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE task_execute (
    id integer NOT NULL,
    site_id integer DEFAULT 0 NOT NULL,
    task_id integer DEFAULT 0 NOT NULL,
    app_id integer DEFAULT 0 NOT NULL,
    task_type character varying(15) DEFAULT 'spider'::character varying NOT NULL,
    start_urls text NOT NULL,
    limit_depth integer DEFAULT 0 NOT NULL,
    limit_total integer DEFAULT 0 NOT NULL,
    limit_time integer DEFAULT 0 NOT NULL,
    limit_subdomain integer DEFAULT 0 NOT NULL,
    limit_image integer DEFAULT 0 NOT NULL,
    limit_js integer DEFAULT 0 NOT NULL,
    url_unique_mode character varying(10) DEFAULT 'url-query'::character varying NOT NULL,
    notify_url character varying(300) DEFAULT ''::character varying NOT NULL,
    source_ip character(15) DEFAULT ''::bpchar NOT NULL,
    proxies text DEFAULT ''::text NOT NULL,
    error text DEFAULT ''::text NOT NULL,
    status integer DEFAULT 0 NOT NULL,
    start_at timestamp without time zone,
    end_at timestamp without time zone,
    create_at timestamp without time zone DEFAULT ('now'::text)::timestamp(0) without time zone NOT NULL,
    update_at timestamp without time zone DEFAULT ('now'::text)::timestamp(0) without time zone NOT NULL,
    domain character varying(50) DEFAULT ''::character varying NOT NULL,
    limit_jsevent integer DEFAULT 0 NOT NULL,
    exclude_urls text DEFAULT ''::text NOT NULL,
    exec_level integer DEFAULT 0 NOT NULL
);


ALTER TABLE task_execute OWNER TO postgres;

--
-- Name: TABLE task_execute; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE task_execute IS '任务执行表';


--
-- Name: COLUMN task_execute.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_execute.id IS '主键，自增ID';


--
-- Name: COLUMN task_execute.site_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_execute.site_id IS '站点ID';


--
-- Name: COLUMN task_execute.task_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_execute.task_id IS '任务ID';


--
-- Name: COLUMN task_execute.app_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_execute.app_id IS '第三方系统ID';


--
-- Name: COLUMN task_execute.task_type; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_execute.task_type IS '任务类型: spider(蜘蛛)/mirror(镜像)/monitor(监控)';


--
-- Name: COLUMN task_execute.start_urls; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_execute.start_urls IS '入口URL';


--
-- Name: COLUMN task_execute.limit_depth; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_execute.limit_depth IS '抓取深度';


--
-- Name: COLUMN task_execute.limit_total; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_execute.limit_total IS '抓取数量';


--
-- Name: COLUMN task_execute.limit_time; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_execute.limit_time IS '执行时长，单位：秒';


--
-- Name: COLUMN task_execute.limit_subdomain; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_execute.limit_subdomain IS '是否抓取子域名: 0否 1是';


--
-- Name: COLUMN task_execute.limit_image; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_execute.limit_image IS '不抓取图片: 1是 0否';


--
-- Name: COLUMN task_execute.limit_js; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_execute.limit_js IS '是否执行JS: 0否 1是';


--
-- Name: COLUMN task_execute.url_unique_mode; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_execute.url_unique_mode IS 'URL去重模式: url只针对URL去重, url-query针对url及query去重';


--
-- Name: COLUMN task_execute.notify_url; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_execute.notify_url IS '任务结束或产生异常时的通知 URL';


--
-- Name: COLUMN task_execute.source_ip; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_execute.source_ip IS '源IP';


--
-- Name: COLUMN task_execute.proxies; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_execute.proxies IS '代理';


--
-- Name: COLUMN task_execute.error; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_execute.error IS '异常中止信息';


--
-- Name: COLUMN task_execute.status; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_execute.status IS '执行状态:0默认 1执行中 101暂停 2完成 201中止 3异常';


--
-- Name: COLUMN task_execute.start_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_execute.start_at IS '开始时间';


--
-- Name: COLUMN task_execute.end_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_execute.end_at IS '结束时间';


--
-- Name: COLUMN task_execute.create_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_execute.create_at IS '创建时间';


--
-- Name: COLUMN task_execute.update_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_execute.update_at IS '更新时间';


--
-- Name: COLUMN task_execute.domain; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_execute.domain IS '任务对应的域名';


--
-- Name: COLUMN task_execute.limit_jsevent; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_execute.limit_jsevent IS '是否模拟JS事件：0否 1是';


--
-- Name: COLUMN task_execute.exclude_urls; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_execute.exclude_urls IS '不抓取的url，以换行(\n)分隔';


--
-- Name: COLUMN task_execute.exec_level; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_execute.exec_level IS '执行级别,默认为0，越大越先执行';


--
-- Name: task_execute_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE task_execute_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE task_execute_id_seq OWNER TO postgres;

--
-- Name: task_execute_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE task_execute_id_seq OWNED BY task_execute.id;


--
-- Name: task_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE task_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE task_id_seq OWNER TO postgres;

--
-- Name: task_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE task_id_seq OWNED BY task.id;


--
-- Name: task_notify; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE task_notify (
    id integer NOT NULL,
    site_id integer DEFAULT 0 NOT NULL,
    task_id integer DEFAULT 0 NOT NULL,
    app_id integer DEFAULT 0 NOT NULL,
    execute_id integer DEFAULT 0 NOT NULL,
    task_type character varying(10) DEFAULT 'spider'::character varying NOT NULL,
    notify_url character varying(300) DEFAULT ''::character varying NOT NULL,
    request_data text DEFAULT ''::text NOT NULL,
    response_data text DEFAULT ''::text NOT NULL,
    retry_times integer DEFAULT 0 NOT NULL,
    error text DEFAULT ''::text NOT NULL,
    status integer DEFAULT 0 NOT NULL,
    create_at timestamp without time zone DEFAULT ('now'::text)::timestamp(0) without time zone NOT NULL,
    update_at timestamp without time zone DEFAULT ('now'::text)::timestamp(0) without time zone NOT NULL,
    event_type character varying(50) DEFAULT ''::character varying NOT NULL
);


ALTER TABLE task_notify OWNER TO postgres;

--
-- Name: TABLE task_notify; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE task_notify IS '任务通知表';


--
-- Name: COLUMN task_notify.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_notify.id IS '主键，自增ID';


--
-- Name: COLUMN task_notify.site_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_notify.site_id IS '站点ID';


--
-- Name: COLUMN task_notify.task_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_notify.task_id IS '任务ID';


--
-- Name: COLUMN task_notify.app_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_notify.app_id IS '第三方系统ID';


--
-- Name: COLUMN task_notify.execute_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_notify.execute_id IS '执行ID';


--
-- Name: COLUMN task_notify.task_type; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_notify.task_type IS '任务类型: spider(蜘蛛)/mirror(镜像)/monitor(监控)';


--
-- Name: COLUMN task_notify.notify_url; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_notify.notify_url IS '通知URL';


--
-- Name: COLUMN task_notify.request_data; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_notify.request_data IS '请求的参数，JSON存储';


--
-- Name: COLUMN task_notify.response_data; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_notify.response_data IS '返回的数据';


--
-- Name: COLUMN task_notify.retry_times; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_notify.retry_times IS '执行时长，单位：秒';


--
-- Name: COLUMN task_notify.error; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_notify.error IS '异常中止信息';


--
-- Name: COLUMN task_notify.status; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_notify.status IS '执行状态:0默认 1通知中 2完成 3异常';


--
-- Name: COLUMN task_notify.create_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_notify.create_at IS '创建时间';


--
-- Name: COLUMN task_notify.update_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_notify.update_at IS '更新时间';


--
-- Name: COLUMN task_notify.event_type; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_notify.event_type IS '事件类型:spider_ok,piping_filterword,piping_fingerprint,piping_keywor,piping_error_http_code,piping_ok';


--
-- Name: task_notify_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE task_notify_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE task_notify_id_seq OWNER TO postgres;

--
-- Name: task_notify_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE task_notify_id_seq OWNED BY task_notify.id;


--
-- Name: task_piping; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE task_piping (
    id integer NOT NULL,
    app_id integer DEFAULT 0 NOT NULL,
    site_id integer DEFAULT 0 NOT NULL,
    task_id integer DEFAULT 0 NOT NULL,
    type character varying(20) DEFAULT ''::character varying NOT NULL,
    filterword_type character varying(10) DEFAULT ''::character varying NOT NULL,
    extend_id integer DEFAULT 0 NOT NULL,
    status integer DEFAULT 0 NOT NULL,
    create_at timestamp without time zone DEFAULT ('now'::text)::timestamp(0) without time zone NOT NULL,
    update_at timestamp without time zone DEFAULT ('now'::text)::timestamp(0) without time zone NOT NULL
);


ALTER TABLE task_piping OWNER TO postgres;

--
-- Name: TABLE task_piping; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE task_piping IS '数据处理表';


--
-- Name: COLUMN task_piping.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_piping.id IS '主键，自增ID';


--
-- Name: COLUMN task_piping.app_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_piping.app_id IS '应用ID';


--
-- Name: COLUMN task_piping.site_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_piping.site_id IS '站点ID';


--
-- Name: COLUMN task_piping.task_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_piping.task_id IS '任务ID';


--
-- Name: COLUMN task_piping.type; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_piping.type IS '类型：fingerprint(指纹) trojan(木马) darklink(暗链) brokenlink(断链) filterwordword(敏感词) keyword(关键词)';


--
-- Name: COLUMN task_piping.filterword_type; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_piping.filterword_type IS '词库类型：system(系统词库) own(自有词库) mixed(混合词库)';


--
-- Name: COLUMN task_piping.extend_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_piping.extend_id IS '扩展ID';


--
-- Name: COLUMN task_piping.status; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_piping.status IS '状态：0停用 1启用';


--
-- Name: COLUMN task_piping.create_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_piping.create_at IS '创建时间';


--
-- Name: COLUMN task_piping.update_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_piping.update_at IS '更新时间';


--
-- Name: task_piping_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE task_piping_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE task_piping_id_seq OWNER TO postgres;

--
-- Name: task_piping_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE task_piping_id_seq OWNED BY task_piping.id;


--
-- Name: task_piping_result; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE task_piping_result (
    id integer NOT NULL,
    app_id integer DEFAULT 0 NOT NULL,
    site_id integer DEFAULT 0 NOT NULL,
    task_id integer DEFAULT 0 NOT NULL,
    execute_id integer DEFAULT 0 NOT NULL,
    piping_id integer DEFAULT 0 NOT NULL,
    type character varying(20) DEFAULT ''::character varying NOT NULL,
    url character varying(1000) DEFAULT ''::character varying NOT NULL,
    result text DEFAULT ''::text NOT NULL,
    status integer DEFAULT 0 NOT NULL,
    audit_status integer DEFAULT 0 NOT NULL,
    create_at timestamp without time zone DEFAULT ('now'::text)::timestamp(0) without time zone NOT NULL,
    update_at timestamp without time zone DEFAULT ('now'::text)::timestamp(0) without time zone NOT NULL
);


ALTER TABLE task_piping_result OWNER TO postgres;

--
-- Name: TABLE task_piping_result; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE task_piping_result IS '数据处理结果表';


--
-- Name: COLUMN task_piping_result.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_piping_result.id IS '主键，自增ID';


--
-- Name: COLUMN task_piping_result.app_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_piping_result.app_id IS '应用ID';


--
-- Name: COLUMN task_piping_result.site_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_piping_result.site_id IS '站点ID';


--
-- Name: COLUMN task_piping_result.task_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_piping_result.task_id IS '任务ID';


--
-- Name: COLUMN task_piping_result.piping_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_piping_result.piping_id IS '管理ID';


--
-- Name: COLUMN task_piping_result.type; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_piping_result.type IS '类型：fingerprint(指纹) trojan(木马) darklink(暗链) brokenlink(断链) filterword(敏感词,过滤词) keyword(>关键词)';


--
-- Name: COLUMN task_piping_result.url; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_piping_result.url IS 'URL';


--
-- Name: COLUMN task_piping_result.result; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_piping_result.result IS '处理结果，以json存储';


--
-- Name: COLUMN task_piping_result.status; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_piping_result.status IS '状态：0停用 1启用';


--
-- Name: COLUMN task_piping_result.audit_status; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_piping_result.audit_status IS '状态：-1审核未通过 0默认 1审核通过';


--
-- Name: COLUMN task_piping_result.create_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_piping_result.create_at IS '创建时间';


--
-- Name: COLUMN task_piping_result.update_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_piping_result.update_at IS '更新时间';


--
-- Name: task_piping_result_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE task_piping_result_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE task_piping_result_id_seq OWNER TO postgres;

--
-- Name: task_piping_result_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE task_piping_result_id_seq OWNED BY task_piping_result.id;


--
-- Name: task_piping_snapshot; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE task_piping_snapshot (
    id integer NOT NULL,
    app_id integer DEFAULT 0 NOT NULL,
    site_id integer DEFAULT 0 NOT NULL,
    task_id integer DEFAULT 0 NOT NULL,
    execute_id integer DEFAULT 0 NOT NULL,
    piping_id integer DEFAULT 0 NOT NULL,
    url_id integer DEFAULT 0 NOT NULL,
    type character varying(20) DEFAULT ''::character varying NOT NULL,
    url character varying(1000) DEFAULT ''::character varying NOT NULL,
    snapshot text DEFAULT ''::character varying NOT NULL,
    result text DEFAULT ''::text NOT NULL,
    status integer DEFAULT 0 NOT NULL,
    audit_status integer DEFAULT 0 NOT NULL,
    create_at timestamp without time zone DEFAULT ('now'::text)::timestamp(0) without time zone NOT NULL,
    update_at timestamp without time zone DEFAULT ('now'::text)::timestamp(0) without time zone NOT NULL
);


ALTER TABLE task_piping_snapshot OWNER TO postgres;

--
-- Name: TABLE task_piping_snapshot; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE task_piping_snapshot IS '快照表';


--
-- Name: COLUMN task_piping_snapshot.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_piping_snapshot.id IS '主键，自增ID';


--
-- Name: COLUMN task_piping_snapshot.app_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_piping_snapshot.app_id IS '应用ID';


--
-- Name: COLUMN task_piping_snapshot.site_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_piping_snapshot.site_id IS '站点ID';


--
-- Name: COLUMN task_piping_snapshot.task_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_piping_snapshot.task_id IS '任务ID';


--
-- Name: COLUMN task_piping_snapshot.piping_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_piping_snapshot.piping_id IS '管理ID';


--
-- Name: COLUMN task_piping_snapshot.type; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_piping_snapshot.type IS '类型：fingerprint(指纹) trojan(木马) darklink(暗链) brokenlink(断链) filterword(敏感词,过滤词) keyword(关键词)';


--
-- Name: COLUMN task_piping_snapshot.url; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_piping_snapshot.url IS 'URL';


--
-- Name: COLUMN task_piping_snapshot.snapshot; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_piping_snapshot.snapshot IS '快照，图片路径';


--
-- Name: COLUMN task_piping_snapshot.result; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_piping_snapshot.result IS '处理结果，以json存储';


--
-- Name: COLUMN task_piping_snapshot.status; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_piping_snapshot.status IS '状态：0停用 1启用';


--
-- Name: COLUMN task_piping_snapshot.audit_status; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_piping_snapshot.audit_status IS '状态：-1审核未通过 0默认 1审核通过';


--
-- Name: COLUMN task_piping_snapshot.create_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_piping_snapshot.create_at IS '创建时间';


--
-- Name: COLUMN task_piping_snapshot.update_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN task_piping_snapshot.update_at IS '更新时间';


--
-- Name: task_piping_snapshot_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE task_piping_snapshot_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE task_piping_snapshot_id_seq OWNER TO postgres;

--
-- Name: task_piping_snapshot_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE task_piping_snapshot_id_seq OWNED BY task_piping_snapshot.id;


--
-- Name: app id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY app ALTER COLUMN id SET DEFAULT nextval('app_id_seq'::regclass);


--
-- Name: domain id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY domain ALTER COLUMN id SET DEFAULT nextval('domain_id_seq'::regclass);


--
-- Name: namelist_link id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY namelist_link ALTER COLUMN id SET DEFAULT nextval('namelist_link_id_seq'::regclass);


--
-- Name: piping_extend id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY piping_extend ALTER COLUMN id SET DEFAULT nextval('piping_extend_id_seq'::regclass);


--
-- Name: proxy id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY proxy ALTER COLUMN id SET DEFAULT nextval('proxy_id_seq'::regclass);


--
-- Name: setting id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY setting ALTER COLUMN id SET DEFAULT nextval('setting_id_seq'::regclass);


--
-- Name: site id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY site ALTER COLUMN id SET DEFAULT nextval('site_id_seq'::regclass);


--
-- Name: spider_url id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY spider_url ALTER COLUMN id SET DEFAULT nextval('spider_url_id_seq'::regclass);


--
-- Name: spiderjs_url id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY spiderjs_url ALTER COLUMN id SET DEFAULT nextval('spiderjs_url_id_seq'::regclass);


--
-- Name: task id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY task ALTER COLUMN id SET DEFAULT nextval('task_id_seq'::regclass);


--
-- Name: task_execute id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY task_execute ALTER COLUMN id SET DEFAULT nextval('task_execute_id_seq'::regclass);


--
-- Name: task_notify id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY task_notify ALTER COLUMN id SET DEFAULT nextval('task_notify_id_seq'::regclass);


--
-- Name: task_piping id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY task_piping ALTER COLUMN id SET DEFAULT nextval('task_piping_id_seq'::regclass);


--
-- Name: task_piping_result id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY task_piping_result ALTER COLUMN id SET DEFAULT nextval('task_piping_result_id_seq'::regclass);


--
-- Name: task_piping_snapshot id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY task_piping_snapshot ALTER COLUMN id SET DEFAULT nextval('task_piping_snapshot_id_seq'::regclass);


--
-- Name: app app_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY app
    ADD CONSTRAINT app_pkey PRIMARY KEY (id);


--
-- Name: domain domain_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY domain
    ADD CONSTRAINT domain_pkey PRIMARY KEY (id);


--
-- Name: namelist_link namelist_link_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY namelist_link
    ADD CONSTRAINT namelist_link_pkey PRIMARY KEY (id);


--
-- Name: piping_extend piping_extend_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY piping_extend
    ADD CONSTRAINT piping_extend_pkey PRIMARY KEY (id);


--
-- Name: proxy proxy_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY proxy
    ADD CONSTRAINT proxy_pkey PRIMARY KEY (id);


--
-- Name: scheduler scheduler_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY scheduler
    ADD CONSTRAINT scheduler_pkey PRIMARY KEY (id);


--
-- Name: setting setting_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY setting
    ADD CONSTRAINT setting_pkey PRIMARY KEY (id);


--
-- Name: site site_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY site
    ADD CONSTRAINT site_pkey PRIMARY KEY (id);


--
-- Name: spider_url spider_url_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY spider_url
    ADD CONSTRAINT spider_url_pkey PRIMARY KEY (id);


--
-- Name: spiderjs_url spiderjs_url_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY spiderjs_url
    ADD CONSTRAINT spiderjs_url_pkey PRIMARY KEY (id);


--
-- Name: task_execute task_execute_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY task_execute
    ADD CONSTRAINT task_execute_pkey PRIMARY KEY (id);


--
-- Name: task_notify task_notify_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY task_notify
    ADD CONSTRAINT task_notify_pkey PRIMARY KEY (id);


--
-- Name: task_piping task_piping_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY task_piping
    ADD CONSTRAINT task_piping_pkey PRIMARY KEY (id);


--
-- Name: task_piping_result task_piping_result_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY task_piping_result
    ADD CONSTRAINT task_piping_result_pkey PRIMARY KEY (id);


--
-- Name: task_piping_snapshot task_piping_snapshot_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY task_piping_snapshot
    ADD CONSTRAINT task_piping_snapshot_pkey PRIMARY KEY (id);


--
-- Name: task task_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY task
    ADD CONSTRAINT task_pkey PRIMARY KEY (id);


--
-- Name: index_depth; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX index_depth ON spider_url USING btree (depth);


--
-- Name: index_executeid; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX index_executeid ON spider_url USING btree (execute_id);


--
-- Name: index_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX index_status ON spider_url USING btree (status);


--
-- Name: index_taskid; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX index_taskid ON spider_url USING btree (task_id);


--
-- PostgreSQL database dump complete
--

