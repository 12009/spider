# -*- coding: utf-8 -*-

# black_list = '["www.xiaomi.com", "www.huawei.com"]'
# white_list = '["www.yundun.com", "www.apple.com"]'
# a = black_list+white_list
# b = eval(black_list)
# print(a,b,type(b))
# {"task_id": 1, "pipings": [{"type": "fingerprint", "status": 1}, {"filterwords": "不求\n闻达", "filterword_type": "mixed", "filterword_operate": "own", "type": "filterword", "status": 1}, {"keywords": [{"words": ["CDN", "云平台", "安全"], "url": "http://www.yundun.com/"}], "type": "keyword", "status": 1}, {"http_codes": "403\n404\n405\n406\n500\n501\n502\n503\n504", "type": "error_http_code", "status": 1}, {"type": "darklink", "white_list":[],"black_list":[],"status": 1}]}
# {"task_id": 1, "pipings": [{"type": "fingerprint", "status": 1}, {"filterwords": "不求\n闻达", "filterword_type": "mixed", "filterword_operate": "own", "type": "filterword", "status": 1}, {"keywords": [{"words": ["CDN", "云平台", "安全"], "url": "http://www.yundun.com/"}], "type": "keyword", "status": 1}, {"http_codes": "403\n404\n405\n406\n500\n501\n502\n503\n504", "type": "error_http_code", "status": 1}, {"type": "darklink", "white_list":["www.xiaomi.com","www.huawei.com"],"black_list":["www.yundun.com","www.apple.com"],"status": 1}]}
