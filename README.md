# 昵称抢注导出sql工具

## 使用方法

1. 将要导出的xlsx/csv/txt文件放到`./asserts`目录下
2. 修改`config.yml`
	1. 输入文件
	2. 过期时间
	3. 数据起始行(略过表头)
	4. 服务器, 名字, CDKey所在列
3. 运行`./docker-dump.sh`
4. 结果在`./asserts/`中的与数据文件同名的sql文件中
