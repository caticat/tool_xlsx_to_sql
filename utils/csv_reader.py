import csv
from typing import Any

from utils.ireader import IReader


class CSVReader(IReader):

	def __init__(self, file_path: str):
		self.data = []
		with open(file_path, 'r', newline='', encoding='utf-8') as file:
			reader = csv.reader(file)
			self.data = [row for row in reader]

	def is_open(self) -> bool:
		"""判断文件是否打开。"""
		return True

	def get_value(self, row_index: int, col_index: int) -> Any:
		"""
        获取指定行和列的值，行列索引从1开始。
        """
		try:
			return self.data[row_index - 1][col_index - 1] # 修改索引从1开始
		except IndexError:
			return None

	def get_max_row(self) -> int:
		"""
        获取最大行数。
        """
		return len(self.data)

	def get_max_column(self) -> int:
		"""
        获取最大列数。
        """
		if self.data:
			return max(len(row) for row in self.data)
		return 0
