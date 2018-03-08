/*添加索引*/

var configs = {
    'autoids':   {'unique':{'name':1},                 'index':[]},
    'execute':   {'unique':{'id':1},                   'index':[]},
    'spiderurl': {'unique':{'id':1},                   'index':[{'task_id':1}, {'execute_id' :1}, {'app_id'   :1}]},
    'snapshot':  {'unique':{'id':1},                   'index':[{'app_key':1}, {'batch'      :1}, {'uuid'     :1}]},
    'parse':     {'unique':{'id':1},                   'index':[{'task_id':1}, {'execute_id' :1}, {'md5_url'  :1}]},
    'outlink':   {'unique':{},                         'index':[{'domain' :1}, {'md5_referer':1}, {'md5_url'  :1}, {'md5_body':1}, {'date':1}]},
    'static':    {'unique':{'domain':1, 'md5_body':1}, 'index':[{'domain' :1}, {'md5_url'    :1}, {'md5_body' :1}]},
}

for(var key in configs) {
    config = configs[key];
    db[key].ensureIndex(config['unique'], {"unique":true});
    for(var j in config['index']) {
        db[key].ensureIndex(config['index'][j]);
    }
}


