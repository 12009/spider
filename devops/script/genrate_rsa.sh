#!/bin/bash
#生成 RSA 的公钥与私钥，python 中使用

openssl genrsa -out private_key.pem 2048
openssl rsa -in private_key.pem -RSAPublicKey_out -out public_key.pem

