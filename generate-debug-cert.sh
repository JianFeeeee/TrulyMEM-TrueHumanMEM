#!/bin/bash
set -e
DIR="/home/program/.harmonyos"
mkdir -p "$DIR"
cd "$DIR"

KEYSTORE_PASS="123456"
ALIAS="debug"
ALIAS_PASS="123456"
DNAME="CN=Debug,OU=Debug,O=TrulyMEM,L=Beijing,ST=Beijing,C=CN"

# 生成私钥
openssl ecparam -genkey -name prime256v1 -out private.pem 2>/dev/null

# 生成 CSR
openssl req -new -key private.pem -out cert.csr -subj "$DNAME" 2>/dev/null

# 自签名证书
openssl req -x509 -days 3650 -key private.pem -in cert.csr -out debug.cer 2>/dev/null

# 创建 PKCS12
openssl pkcs12 -export -out debug.p12 -inkey private.pem -in debug.cer -password pass:$KEYSTORE_PASS -name $ALIAS 2>/dev/null

echo "Debug cert generated at $DIR"
ls -la "$DIR"
