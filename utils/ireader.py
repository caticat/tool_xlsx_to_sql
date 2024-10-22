from abc import ABC, abstractmethod
from typing import Any


# 定义接口
class CSVInterface(ABC):

	@abstractmethod
	def is_open(self) -> bool:
		"""判断文件是否打开。"""
		pass

	@abstractmethod
	def get_value(self, row_index: int, col_index: int) -> Any:
		"""获取指定行和列的值，行列索引从1开始。"""
		pass

	@abstractmethod
	def get_max_row(self) -> int:
		"""获取最大行数。"""
		pass

	@abstractmethod
	def get_max_column(self) -> int:
		"""获取最大列数。"""
		pass
