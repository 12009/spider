package main

import (
	"./dfsutil"
	"bytes"
	"flag"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"net/http"
	"net/url"
	"os"
	"path"
	"strconv"
)

var configMap map[string]string
var logger *log.Logger

func Upload(w http.ResponseWriter, r *http.Request) {
	var response bytes.Buffer
	var filekey bytes.Buffer
	filekeyRaw := r.FormValue("filekey")
	filekey.WriteString(configMap["dfs_root"])
	filekey.WriteString(filekeyRaw)

	_, err := os.Open(filekey.String())
	if os.IsNotExist(err) {
		os.MkdirAll(path.Dir(filekey.String()), 0755)
	}

	r.ParseMultipartForm(32 << 20)
	srcFile, _, err := r.FormFile("file_upload")
	if err != nil {
		logger.Println("201," + err.Error())
		fmt.Fprintln(w, "201,"+err.Error())
		return
	}
	defer srcFile.Close()

	destFile, err := os.OpenFile(filekey.String(), os.O_WRONLY|os.O_CREATE, 0644)
	if err != nil {
		logger.Println("201," + err.Error())
		fmt.Fprintln(w, "201,"+err.Error())
		return
	}
	defer destFile.Close()
	io.Copy(destFile, srcFile)
	response.WriteString("000,")
	response.WriteString(filekeyRaw)
	fmt.Fprintln(w, response.String())
	return
}

//文件下载
func Download(w http.ResponseWriter, req *http.Request) {
	queryForm, err := url.ParseQuery(req.URL.RawQuery)
	if err != nil {
		w.WriteHeader(701)
		logger.Println("201," + err.Error())
		fmt.Fprintln(w, "201,"+err.Error())
		return
	}
	if _, ok := queryForm["filekey"]; !ok {
		w.WriteHeader(701)
		logger.Println("201, filekey is requirement!")
		fmt.Fprintln(w, "201, filekey is requirement!")
		return
	}
	filekey := queryForm["filekey"][0]
	filepath := configMap["dfs_root"] + filekey
	if !dfsutil.File_exists(filepath) {
		w.WriteHeader(701)
		fmt.Fprintln(w, "201,file is not exists,"+filekey)
	} else {
		w.Header().Set("Content-type", "image/jpeg")
		w.Header().Set("Content-Disposition", "attachment; filename="+path.Base(filepath))
		w.Header().Set("Filekey", filekey)
		http.ServeFile(w, req, filepath)
	}
	return
}

//文件信息
func Info(w http.ResponseWriter, req *http.Request) {
	queryForm, err := url.ParseQuery(req.URL.RawQuery)
	if err != nil {
		logger.Println("201," + err.Error())
		fmt.Fprintln(w, "201,"+err.Error())
		return
	}
	filekey := req.FormValue("filekey")
	filepath := configMap["dfs_root"] + filekey
	file, _ := os.Open(filepath)
	body, _ := ioutil.ReadAll(file)
	md5Hash := dfsutil.Md5_sum(body)
	response := map[string]string{
		"filekey":  queryForm["filekey"][0],
		"hash":     md5Hash,
		"filesize": strconv.Itoa(len(body)),
	}
	fmt.Fprintln(w, dfsutil.Json_encode(response))
	return
}

func InitConfig() {
	//变量初始化
	configMap = map[string]string{"dfs_root": "/tmp", "host": "0.0.0.0", "port": "8058", "debug": "no", "listen_address": "", "logdir": ""}

	//
	cli_configfile := flag.String("config", "", "config file")
	cli_host := flag.String("host", "", "host")
	cli_port := flag.String("port", "", "port")
	cli_dfs_root := flag.String("dfs_root", "", "data path")
	cli_debug := flag.String("debug", "no", "debug mode: yes/no")
	cli_logdir := flag.String("logdir", "no", "thd path of log")
	flag.Parse()

	if *cli_configfile != "" {
		jsonConfig, _ := dfsutil.Json_decode_file(*cli_configfile)
		for key, value := range jsonConfig {
			if _, ok := configMap[key]; ok {
				configMap[key] = value
			}
		}
	}
	if *cli_host != "" {
		configMap["host"] = *cli_host
	}
	if *cli_port != "" {
		configMap["port"] = *cli_port
	}
	if *cli_dfs_root != "" {
		configMap["dfs_root"] = *cli_dfs_root
	}
	if *cli_debug != "no" {
		configMap["debug"] = "yes"
	}
	if *cli_logdir != "" {
		configMap["logdir"] = *cli_logdir
	}
	configMap["dfs_root"] = dfsutil.FormatPathSuffix(configMap["dfs_root"])
	configMap["listen_address"] = configMap["host"] + ":" + configMap["port"]
}

func main() {
	logger = dfsutil.GetLogger("/tmp/dfs_server.log")
	InitConfig()

	logger.Println(dfsutil.Json_encode(configMap))
	http.HandleFunc("/upload", Upload)
	http.HandleFunc("/download", Download)
	http.HandleFunc("/info", Info)
	http.ListenAndServe(configMap["listen_address"], nil)
}
