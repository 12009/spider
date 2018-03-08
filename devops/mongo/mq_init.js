db.process_config.insert([
    {'hostname':'master', 'status':'enable', 'spider':NumberInt(15), 'notify':NumberInt(3), 'piping':NumberInt(4), 'snapshot':NumberInt(1), 'ckready':NumberInt(1), 'ckfinish':NumberInt(1), 'ckcorrect':NumberInt(1), 'initexec':NumberInt(1), 'scheduler':NumberInt(1)},
]);

db.stats_mq.insert([
    {'mq_key':'spider',   'undo':NumberInt(0), 'ready':NumberInt(0), 'doing':NumberInt(0), 'done':NumberInt(0)},
    {'mq_key':'mirror',   'undo':NumberInt(0), 'ready':NumberInt(0), 'doing':NumberInt(0), 'done':NumberInt(0)},
    {'mq_key':'notify',   'undo':NumberInt(0), 'ready':NumberInt(0), 'doing':NumberInt(0), 'done':NumberInt(0)},
    {'mq_key':'piping',   'undo':NumberInt(0), 'ready':NumberInt(0), 'doing':NumberInt(0), 'done':NumberInt(0)},
    {'mq_key':'snapshot', 'undo':NumberInt(0), 'ready':NumberInt(0), 'doing':NumberInt(0), 'done':NumberInt(0)}
]);

