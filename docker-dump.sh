#!/bin/bash

set -a  # 自动导出所有变量
source docker-compose.env
set +a  # 关闭自动导出

set -u

RED="\033[0;31m"
GREEN="\033[0;32m"
END="\033[0;00m"

echo "启动容器"
mkdir -p ./tmp
docker-compose up -d
echo -e "${GREEN}启动容器完成${END}"

echo -n "等待数据库准备完毕"
container_name="xlsx_to_sql-app-1"
docker exec $container_name sh -c '
while ! mysqladmin ping --silent; do
    echo -n "."
    sleep 1
done
sleep 10
'
echo ""
echo -e "${GREEN}数据库准备完毕${END}"

echo "开始导入表格数据到数据库"
docker exec $container_name python3 main.py
if [ $? -ne 0 ]; then
	echo -e "${RED}导入数据库失败${END}"
else
	echo -e "${GREEN}导入数据库完成${END}"
fi

echo "停止容器"
docker-compose stop
echo -e "${GREEN}停止容器完成${END}"
