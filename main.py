import os
import time
from pathlib import Path
from typing import List

from utils.csv_reader import CSVReader
from utils.file_storage import YamlStorage
from utils.ireader import CSVInterface
from utils.perf_timer import PerfTimer
from utils.xlsx import Xlsx


class Conf:

	def __init__(self):
		conf = YamlStorage(Path(os.getcwd()) / "config.yml")
		self.assets = conf.get("assets")
		self.__input_file_name = conf.get("in")
		self.expire_date = conf.get("expire_date")
		self.row_begin = conf.get("row.begin")
		self.col_server = conf.get("col.server")
		self.col_name = conf.get("col.name")
		self.col_cdkey = conf.get("col.cdkey")
		self.sql_table = conf.get("sql.table")
		self.sql_len = conf.get("sql.len")
		self.time = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())

	@property
	def input_file_name(self) -> str:
		return os.path.join(os.getcwd(), self.assets, self.__input_file_name)

	@property
	def output_file_name(self) -> str:
		return os.path.join(os.getcwd(), self.assets, f"{os.path.splitext(self.__input_file_name)[0]}.{self.time}.sql")


def open_input_file(c: Conf) -> CSVInterface:
	input_file_name = c.input_file_name
	if input_file_name.endswith(".xlsx") or input_file_name.endswith(".xls"):
		return Xlsx(c.input_file_name)
	else:
		return CSVReader(c.input_file_name)


def check_conf(c: Conf, x: CSVInterface) -> None:
	if not x.is_open():
		raise Exception(f"打开输入表格{c.input_file_name}失败")

	col_max = x.get_max_column()
	if col_max < max(c.col_server, c.col_name, c.col_cdkey):
		raise Exception(f"配置错误, 输入表格最大列数: {col_max}, 配置文件需要列数:{max(c.col_server, c.col_name, c.col_cdkey)}")


def create_table(c: Conf) -> str:
	return f"""
DROP TABLE IF EXISTS `{c.sql_table}`;
CREATE TABLE `{c.sql_table}` (
	`cd_key` varchar(32) COLLATE utf8mb4_bin NOT NULL COMMENT 'cdkey',
	`role_name` varchar(255) COLLATE utf8mb4_bin DEFAULT '' COMMENT '角色名字',
	`server_id` smallint(6) unsigned NOT NULL DEFAULT '0' COMMENT '服务器ID',
	`role_id` bigint(20) NOT NULL DEFAULT '0' COMMENT '角色ID',
	`score` bigint(20) NOT NULL DEFAULT '0' COMMENT '积分',
	`expire_date` datetime DEFAULT '{c.expire_date}' COMMENT '过期时间',
	`status` smallint(6) unsigned NOT NULL DEFAULT '0' COMMENT '标记是否被使用 0：cdkey未被使用 1:cdkey被使用',
	PRIMARY KEY (`cd_key`) USING BTREE,
	UNIQUE KEY `cd_key_index` (`role_name`,`server_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin ROW_FORMAT=DYNAMIC;
"""


def make_sqls(c: Conf, x: CSVInterface) -> List[str]:
	sqls: List[str] = []
	sqls.append(create_table(c))

	duplicate_datas: dict[str, List[str]] = {}
	values: List[str] = []
	row_max = x.get_max_row()
	for row_index in range(c.row_begin, row_max + 1):
		s = x.get_value(row_index, c.col_server)
		n = str(x.get_value(row_index, c.col_name)).replace(" ", "")
		k = x.get_value(row_index, c.col_cdkey)

		# 重复数据检查
		d_k = f"{s}-{n}"
		duplicate_datas.setdefault(d_k, [])
		if len(duplicate_datas[d_k]) > 0: # TODO: 这里先自动排除掉重复项
			print(f"重复的数据: serverID: {s}, name: {n}, cdkey: {k}")
			continue
		duplicate_datas[d_k].append(k)

		values.append(f'("{s}", "{n}", "{k}")')
		if len(values) >= c.sql_len:
			sqls.append(f"insert into {c.sql_table} (server_id, role_name, cd_key) values {', '.join(values)};")
			values.clear()

	if len(values) > 0:
		sqls.append(f"insert into {c.sql_table} (server_id, role_name, cd_key) values {', '.join(values)};")
		values.clear()

	return sqls


def write_sqls(c: Conf, sqls: List[str]) -> None:
	with open(c.output_file_name, "w", encoding="utf-8") as fp:
		fp.writelines("\n".join(sqls))


def import_msyql(filename: str) -> None:
	os.system(f"mysql -uroot -p{os.getenv('MYSQL_ROOT_PASSWORD')} {os.getenv('MYSQL_DATABASE')} -e \"source {filename}\"")


def export_mysql(filename: str) -> None:
	os.system(f"mysqldump -uroot -p{os.getenv('MYSQL_ROOT_PASSWORD')} --result-file={filename} {os.getenv('MYSQL_DATABASE')}")


def main():
	p = PerfTimer()
	c = Conf()
	x = open_input_file(c)
	check_conf(c, x)
	sqls = make_sqls(c, x)
	write_sqls(c, sqls)
	import_msyql(c.output_file_name)
	export_mysql(c.output_file_name)

	print(f"生成完成, 总耗时: {p.tick()} 秒")


if __name__ == "__main__":
	main()
