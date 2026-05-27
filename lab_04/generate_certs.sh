#!/bin/bash

# Создаём папку для сертификатов
mkdir -p certs
cd certs

# 1. Создаём корневой CA
openssl req -x509 -newkey rsa:4096 -days 365 -nodes \
  -keyout ca_key.pem -out ca_cert.pem \
  -subj "/C=RU/ST=Moscow/L=Moscow/O=MyLab/CN=MyCA"

# 2. Создаём сертификат сервера с SAN
cat > server.conf << 'EOF'
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C = RU
ST = Moscow
L = Moscow
O = MyLab
CN = localhost

[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth, clientAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = *.localhost
IP.1 = 127.0.0.1
IP.2 = 10.0.2.15
EOF

openssl genrsa -out server_key.pem 2048
openssl req -new -key server_key.pem -out server.csr -config server.conf
openssl x509 -req -in server.csr -CA ca_cert.pem -CAkey ca_key.pem \
  -CAcreateserial -out server_cert.pem -days 365 -extensions v3_req -extfile server.conf

# 3. Создаём клиентский сертификат
openssl genrsa -out client_key.pem 2048
openssl req -new -key client_key.pem -out client.csr \
  -subj "/C=RU/ST=Moscow/L=Moscow/O=MyLab/CN=client"
openssl x509 -req -in client.csr -CA ca_cert.pem -CAkey ca_key.pem \
  -CAcreateserial -out client_cert.pem -days 365

# Очистка временных файлов
rm server.csr client.csr server.conf

echo "Сертификаты созданы в папке certs/"
