package main

import (
	"./dfsutil"
	"bytes"
	"flag"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"mime/multipart"
	"net/http"
	"os"
	"path"
)

var configMap = map[string]string{}
var logger *log.Logger

func Upload(filename string, filekey string, targetUrl string) string {
	var response bytes.Buffer
	bodyBuf := &bytes.Buffer{}
	bodyWriter := multipart.NewWriter(bodyBuf)
	bodyWriter.WriteField("filekey", filekey)

	//关键的一步操作
	fileWriter, err := bodyWriter.CreateFormFile("file_upload", filename)
	if err != nil {
		response.WriteString("101,")
		response.WriteString(err.Error())
		logger.Println(response.String())
		return response.String()
	}

	//打开文件句柄操作
	fh, err := os.Open(filename)
	if err != nil {
		response.WriteString("101,")
		response.WriteString(err.Error())
		logger.Println(response.String())
		return response.String()
	}

	//iocopy
	_, err = io.Copy(fileWriter, fh)
	if err != nil {
		response.WriteString("101,")
		response.WriteString(err.Error())
		logger.Println(response.String())
		return response.String()
	}

	contentType := bodyWriter.FormDataContentType()
	bodyWriter.Close()

	resp, err := http.Post(targetUrl, contentType, bodyBuf)
	if err != nil {
		response.WriteString("101,")
		response.WriteString(err.Error())
		logger.Println(response.String())
		return response.String()
	}
	defer resp.Body.Close()
	resp_body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		response.WriteString("101,")
		response.WriteString(err.Error())
		logger.Println(response.String())
		return response.String()
	}
	return string(resp_body)
}

func Download(filekey string, targetUrl string, config map[string]string) string {
	var response bytes.Buffer
	resp, err := http.Get(targetUrl + "?filekey=" + filekey)
	if err != nil {
		response.WriteString("101,")
		response.WriteString(err.Error())
		logger.Println(response.String())
		return response.String()
	}
	defer resp.Body.Close()
	resp_body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		response.WriteString("101,")
		response.WriteString(err.Error())
		logger.Println(response.String())
		return response.String()
	}
	if resp.StatusCode == 701 {
		response.WriteString("701,")
		response.WriteString(string(resp_body))
		logger.Println(response.String())
		return response.String()
	}
	var destfile string
	if config["destfile"] == "" {
		destfile = config["destdir"] + "/" + filekey
	} else {
		destfile = config["destfile"]
	}
	destdir := path.Dir(destfile)
	if !dfsutil.File_exists(destdir) {
		os.MkdirAll(destdir, 0755)
	}
	fh, err := os.OpenFile(destfile, os.O_CREATE|os.O_WRONLY, 0644)
	defer fh.Close()
	if err != nil {
		response.WriteString("101,")
		response.WriteString(err.Error())
		logger.Println(response.String())
		return response.String()
	}
	fmt.Println(len(resp_body))
	_, err = fh.Write(resp_body)
	if err != nil {
		response.WriteString("101,")
		response.WriteString(err.Error())
		logger.Println(response.String())
		return response.String()
	}
	return ""
}

func Info(filekey string, targetUrl string) string {
	var response bytes.Buffer
	url := targetUrl + "?filekey=" + filekey

	resp, err := http.Get(url)
	if err != nil {
		response.WriteString("101,")
		response.WriteString(err.Error())
		return response.String()
	}
	defer resp.Body.Close()
	resp_body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		response.WriteString("101,")
		response.WriteString(err.Error())
		return response.String()
	}
	return string(resp_body)
}

func InitConfig() {
	//定义默认配置
	configMap = map[string]string{
		"server": "http://127.0.0.1:8058", "action": "", "filekey": "",
		"file": "", "destdir": "", "destfile": "", "debug": "no", "logdir": "/tmp",
	}
	actions := map[string]string{"upload": "1", "download": "1", "info": "1"}

	//定义命令行参数
	cli_configfile := flag.String("config", "", "the json file for config")
	cli_action := flag.String("action", "", "action, eq:upload/download/info")
	cli_server := flag.String("server", "", "server, eq:http://192.168.1.10:8058")
	cli_file := flag.String("file", "", "the file for upload")
	cli_filekey := flag.String("filekey", "", "the path that file saved")
	cli_destdir := flag.String("destdir", "", "the dir  that download to")
	cli_destfile := flag.String("destfile", "", "the file that download to")
	cli_logdir := flag.String("logdir", "", "the dir of the log")
	cli_debug := flag.String("debug", "no", "open the debug mode: yes/no")
	flag.Parse()

	//解析配置文件
	if *cli_configfile != "" {
		jsonConfig, _ := dfsutil.Json_decode_file(*cli_configfile)
		for key, value := range jsonConfig {
			if _, ok := configMap[key]; ok {
				configMap[key] = value
			}
		}
	}
	//命令行参数优先级高于配置文件
	if *cli_server != "" {
		configMap["server"] = *cli_server
	}
	if *cli_action != "" {
		configMap["action"] = *cli_action
	}
	if *cli_file != "" {
		configMap["file"] = *cli_file
	}
	if *cli_filekey != "" {
		configMap["filekey"] = *cli_filekey
	}
	if *cli_destdir != "" {
		configMap["destdir"] = *cli_destdir
	}
	if *cli_destfile != "" {
		configMap["destfile"] = *cli_destfile
	}
	if *cli_logdir != "" {
		configMap["logdir"] = *cli_logdir
	}
	if *cli_debug != "no" {
		configMap["debug"] = "yes"
	}

	//限制动作为 upload/download/info
	if _, ok := actions[configMap["action"]]; !ok {
		logger.Println("101, action is error!")
		return
	}
	//限制upload动作的参数
	if configMap["action"] == "upload" {
		if configMap["filekey"] == "" || configMap["file"] == "" {
			logger.Println("101,the filekey and file is requirement")
			return
		}
	}
	//限制download动作的参数
	if configMap["action"] == "download" {
		if configMap["filekey"] == "" {
			logger.Println("101,the filekey is requirement")
			return
		}
		if configMap["destfile"] == "" && configMap["destdir"] == "" {
			logger.Println("101,the destfile or destdir is requirement")
			return
		}
	}
	//限制info动作的参数
	if configMap["action"] == "info" {
		if configMap["filekey"] == "" {
			logger.Println("101,the filekey is requirement")
			return
		}
	}
	configMap["server"] = dfsutil.FormatPathSuffix(configMap["server"])
}

// sample usage
func main() {
	logger = dfsutil.GetLogger("/tmp/dfs_client.log")
	InitConfig()

	if configMap["debug"] == "yes" {
		logger.Println(dfsutil.Json_encode(configMap))
	}
	if configMap["action"] == "upload" {
		result := Upload(configMap["file"], configMap["filekey"], configMap["server"]+"upload")
		fmt.Print(result)
	} else if configMap["action"] == "download" {
		result := Download(configMap["filekey"], configMap["server"]+"download", configMap)
		fmt.Println(result)
	} else if configMap["action"] == "info" {
		result := Info(configMap["filekey"], configMap["server"]+"info")
		fmt.Println(result)
	} else {
		fmt.Println("")
	}
}
