### 文件上传服务

```
本程序是一个文件上传服务
启动server端后，会监听端口，由client端将文件上传到远程的服务器
本程序使用json作为配置文件
本程序可直接打包成二进制文件，放到服务器上通过命令行执行即可
```

#编译二进制文件
go build -ldflags "-s -w" dfs_client.go
go build -ldflags "-s -w" dfs_server.go

#启动服务端
nohup ./dfs_server -config server.json &

#查看帮助
./dfs_client -h

./dfs_client -config client.json 
