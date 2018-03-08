/*添加索引*/

var configs = {
    'stats_mq':           {'unique':{'id':1},                'index':[]},
    'stats_batch_run':    {'unique':{'mqkey':1, 'batch':1},  'index':[]},
    'stats_batch_stage':  {'unique':{'mqkey':1, 'batch':1},  'index':[]},
    'process_list':       {'unique':{'hostname':1, 'title':1},  'index':[{'mqkey':1}, {'status':1}]},
    'process_config':     {'unique':{'hostname':1},  'index':[]},

    'mq_spider_undo':        {'unique':{'mq_id':1},             'index':[{'mq_batch':1}]},
    'mq_spider_ready':       {'unique':{'mq_id':1},             'index':[{'mq_batch':1}]},
    'mq_spider_doing':       {'unique':{'mq_id':1},             'index':[{'mq_batch':1}]},
    'mq_spider_done':        {'unique':{'mq_id':1},             'index':[{'mq_batch':1}]},

    'mq_mirror_undo':        {'unique':{'mq_id':1},             'index':[{'mq_batch':1}]},
    'mq_mirror_ready':       {'unique':{'mq_id':1},             'index':[{'mq_batch':1}]},
    'mq_mirror_doing':       {'unique':{'mq_id':1},             'index':[{'mq_batch':1}]},
    'mq_mirror_done':        {'unique':{'mq_id':1},             'index':[{'mq_batch':1}]},

    'mq_notify_undo':        {'unique':{'mq_id':1},             'index':[{'mq_batch':1}]},
    'mq_notify_ready':       {'unique':{'mq_id':1},             'index':[{'mq_batch':1}]},
    'mq_notify_doing':       {'unique':{'mq_id':1},             'index':[{'mq_batch':1}]},
    'mq_notify_done':        {'unique':{'mq_id':1},             'index':[{'mq_batch':1}]},

    'mq_piping_undo':        {'unique':{'mq_id':1},             'index':[{'mq_batch':1}]},
    'mq_piping_ready':       {'unique':{'mq_id':1},             'index':[{'mq_batch':1}]},
    'mq_piping_doing':       {'unique':{'mq_id':1},             'index':[{'mq_batch':1}]},
    'mq_piping_done':        {'unique':{'mq_id':1},             'index':[{'mq_batch':1}]},

    'mq_snapshot_undo':      {'unique':{'mq_id':1},             'index':[{'mq_batch':1}]},
    'mq_snapshot_ready':     {'unique':{'mq_id':1},             'index':[{'mq_batch':1}]},
    'mq_snapshot_doing':     {'unique':{'mq_id':1},             'index':[{'mq_batch':1}]},
    'mq_snapshot_done':      {'unique':{'mq_id':1},             'index':[{'mq_batch':1}]},
}
for(var key in configs) {
    config = configs[key];
    db[key].ensureIndex(config['unique'], {"unique":true});
    for(var j in config['index']) {
        db[key].ensureIndex(config['index'][j]);
    }
}

