#!/bin/bash
#同步文件并删除目录
#rsync同步并删除，危险，请勿修改
 
path_base=/data/ydfs/ 
cd ${path_base} 
for host in `ls ${path_base}` 
do 
    for name in `ls ${path_base}${host}` 
    do 
        dirname=${path_base}${host}/${name} 
        eid=${dirname#*_} 
        if [[ $eid < 350244 ]]; then 
            echo rsync -avRte ssh ./${host}/${name}/ root@172.16.100.213:/data/ydfs_raw 
            rsync -avRte ssh ./${host}/${name}/ root@172.16.100.213:/data/ydfs_raw 
            #rm -rf ${dirname}
        fi
    done
done
