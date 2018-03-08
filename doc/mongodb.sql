spiderurl
{
    'id': NumberInt(0), 
    'site_id': NumberInt(0), 
    'task_id': NumberInt(0), 
    'app_id': NumberInt(0), 
    'execute_id': NumberInt(0), 
    'task_type': '', 
    'url': '', 
    'url_type': '', 
    'md5_url': '', 
    'file_name': '', 
    'file_path': '', 
    'file_extension': '', 
    'referer': '', 
    'method': '', 
    'exec_level': NumberInt(0), 
    'depth': NumberInt(0), 
    'query': '', 
    'post': '', 
    'http_code': '', 
    'nettime': '', 
    'request_headers': '', 
    'response_headers': '', 
    'redirects': '', 
    'response_body_type': '', 
    'body': '', 
    'md5_body': '', 
    'invisible': '', 
    'pattern_path': '', 
    'pattern_query': '', 
    'pattern_post': '', 
    'error': '', 
    'status': NumberInt(0), 
    'start_at': '', 
    'end_at': '', 
    'create_at': '', 
    'update_at': ''
}

spiderjsurl
{
    'id', 
    'url', 
    'md5_url', 
    'referer', 
    'method', 
    'http_code', 
    'request_headers ', 
    'response_headers', 
    'redirects', 
    'body', 
    'md5_body', 
    'parse_result', 
    'error', 
    'status', 
    'start_at', 
    'end_at', 
    'create_at'
}
execute
{
    'id', 
    'site_id', 
    'task_id', 
    'app_id', 
    'task_type', 
    'start_urls', 
    'exec_level', 
    'domain', 
    'limit_depth', 
    'limit_total', 
    'limit_time', 
    'limit_subdomain', 
    'limit_image', 
    'limit_js', 
    'limit_jsevent', 
    'exclude_urls', 
    'url_unique_mode', 
    'notify_url', 
    'source_ip', 
    'proxies',
    'status', 
    'start_at', 
    'end_at', 
    'create_at', 
    'update_at'
}
snapshot
{
    'id', 
    'app_key', 
    'batch_no', 
    'uuid', 
    'type', 
    'url', 
    'filename', 
    'proxy', 
    'notify_url', 
    'error', 
    'status', 
    'create_at', 
    'update_ad'
}

static
{
    'id', 
    'domain', 
    'url', 
    'md5_url', 
    'file_name', 
    'file_key', 
    'file_type', 
    'md5_body', 
    'create_at', 
    'update_at'
}

parse
{
    'id': NumberInt(0), 
    'site_id': NumberInt(0), 
    'task_id': NumberInt(0), 
    'app_id': NumberInt(0), 
    'execute_id': NumberInt(0), 
    'referer', 
    'url', 
    'md5_url', 
    'parse_type', 
    'result', 
    'create_at', 
    'update_at'
}

outlink
{
    'id': NumberInt(0), 
    'task_id': NumberInt(0), 
    'execute_id': NumberInt(0), 
    'domain': '', 
    'referer', 
    'md5_referer', 
    'url', 
    'md5_url', 
    'md5_body', 
    'invisible', 
    'filterwords', 
    'date', 
    'create_at', 
    'update_at'
}

piping
{
    'id': NumberInt(0), 
    'site_id': NumberInt(0), 
    'domain_id': NumberInt(0), 
    'task_id': NumberInt(0), 
    'execute_id': NumberInt(0), 
    'domain': '', 
    'url', 
    'md5_url', 
    'outlink', 
    'md5_outlink', 
    'invisible', 
    'filterwords', 
    'create_at', 
    'update_at'
}


