/* 删除文档 */
var configs = [
    'stats_mq', 'stats_batch_run', 'stats_batch_stage',
    'execute_undo', 'execute_ready', 'execute_doing', 'execute_done',
    'spider_undo', 'spider_ready', 'spider_doing', 'spider_done',
    'mirror_undo', 'mirror_ready', 'mirror_doing', 'mirror_done',
    'notify_undo', 'notify_ready', 'notify_doing', 'notify_done',
    'piping_undo', 'piping_ready', 'piping_doing', 'piping_done',
    'snapshot_undo', 'snapshot_ready', 'snapshot_doing', 'snapshot_done',
];

for(var j in  configs) {
    key = configs[i];
    db[key].drop();
}

