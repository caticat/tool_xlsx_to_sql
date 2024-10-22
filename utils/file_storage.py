# 文件存储, 简单数据存取通用数据结构封装

import json
import os
from typing import Any, Optional, Union

import yaml


class FileStorage:

	def __init__(self, source: str, from_file: bool = True) -> None:
		"""
		文件存储, 简单数据存取通用数据结构封装

        初始化 FileStorage 实例，并加载数据

        参数:
        source (str): 存储数据的文件名或字符串
        from_file (bool): 指定 source 是文件名还是字符串

		说明:
			支持:
				文件格式: json, yaml
			使用方式:
				# kvs.a.b.c = []
				kvs.set("a.b.c", [])
				kvs.get("a.b.c")
				kvs.set_value([], "a", "b", "c")
				kvs.get_value("a", "b", "c")
				# kvs.a.b.c.0 = 1
				# kvs.a.b.c.d = "abc"
        """
		self.from_file = from_file
		if from_file:
			self.filename: str = source
			self.data: dict = {} # 初始化空字典，用于存储数据
			self.load_from_file() # 在初始化时加载数据
		else:
			self.data = self.load_from_string(source) # 从字符串加载数据

	def load_from_file(self) -> None:
		"""
        加载文件中的数据
        如果文件不存在或无法解析，则初始化为空字典
        """
		raise NotImplementedError("This method should be overridden by subclasses.")

	def load_from_string(self, data_string: str) -> dict:
		"""
        从字符串加载数据

        参数:
        data_string (str): 数据格式的字符串

        返回:
        dict: 解析后的字典数据，如果解析失败则返回空字典
        """
		raise NotImplementedError("This method should be overridden by subclasses.")

	def save(self) -> None:
		"""
        保存数据到文件
        如果保存过程中发生错误，将输出错误信息
        """
		raise NotImplementedError("This method should be overridden by subclasses.")

	def clear(self) -> None:
		"""数据清理"""
		self.filename = ""
		self.data.clear()

	def get_value(self, *args: Union[str, int]) -> Optional[Any]:
		return self.get(self.__make_key(*args))

	def get(self, key: str) -> Optional[Any]:
		"""
        获取指定路径下的字段值

        参数:
        key (str): 点分隔的路径字符串，用于指定要获取的字段

        返回:
        Any: 字段值，如果路径不存在则返回 None
        """
		parts = key.split('.')
		current = self.data
		for part in parts:
			if isinstance(current, list):
				try:
					part_index = int(part)
					current = current[part_index]
				except (ValueError, IndexError):
					return None # 如果 part 不是数字或索引超出范围，则返回 None
			elif isinstance(current, dict):
				if part in current:
					current = current[part]
				else:
					return None
			else:
				return None
		return current

	def set_value(self, value: Any, *args: Union[str, int]) -> None:
		self.set(self.__make_key(*args), value)

	def set(self, key: str, value: Any) -> None:
		"""
        设置指定路径下的字段值

        参数:
        key (str): 点分隔的路径字符串，用于指定要设置的字段
        value (Any): 要设置的值

        返回:
        None
        """
		parts = key.split('.')
		current = self.data
		for part in parts[:-1]:
			if isinstance(current, list):
				try:
					part_index = int(part)
					while part_index >= len(current):
						current.append({})
					current = current[part_index]
				except ValueError:
					return # 如果 part 不是数字，无法设置值
			elif isinstance(current, dict):
				if part not in current:
					current[part] = {}
				current = current[part]
			else:
				return # 如果 current 不是 list 或 dict，无法设置值

		# 处理最后一个部分
		last_part = parts[-1]
		if isinstance(current, list):
			try:
				part_index = int(last_part)
				while part_index >= len(current):
					current.append(None)
				current[part_index] = value
			except ValueError:
				return # 如果 part 不是数字，无法设置值
		elif isinstance(current, dict):
			current[last_part] = value
		else:
			return # 如果 current 不是 list 或 dict，无法设置值

	def __make_key(self, *args: Union[str, int]) -> str:
		l_args: list[str] = [str(s) for s in args]
		return ".".join(l_args)


class JsonStorage(FileStorage):

	def load_from_file(self) -> None:
		"""
        加载 JSON 文件中的数据
        如果文件不存在或无法解析，则初始化为空字典
        """
		if os.path.exists(self.filename):
			try:
				with open(self.filename, 'r', encoding='utf-8') as f:
					self.data = json.load(f)
			except json.JSONDecodeError:
				self.data = {} # 处理 JSON 解码错误，初始化为空字典

	def load_from_string(self, data_string: str) -> dict:
		"""
        从 JSON 字符串加载数据

        参数:
        data_string (str): JSON 格式的字符串

        返回:
        dict: 解析后的字典数据，如果解析失败则返回空字典
        """
		try:
			return json.loads(data_string)
		except json.JSONDecodeError:
			return {} # 处理 JSON 解码错误，初始化为空字典

	def save(self) -> None:
		"""
        保存数据到 JSON 文件
        如果保存过程中发生错误，将输出错误信息
        """
		if self.from_file:
			try:
				with open(self.filename, 'w', encoding='utf-8') as f:
					json.dump(self.data, f, indent=4)
			except IOError as e:
				print(f"Error saving data to file: {e}")
		else:
			print("Cannot save to string, instance was initialized with a JSON string.")


class YamlStorage(FileStorage):

	def load_from_file(self) -> None:
		"""
        加载 YAML 文件中的数据
        如果文件不存在或无法解析，则初始化为空字典
        """
		if os.path.exists(self.filename):
			try:
				with open(self.filename, 'r', encoding='utf-8') as f:
					self.data = yaml.safe_load(f)
			except yaml.YAMLError:
				self.data = {} # 处理 YAML 解码错误，初始化为空字典

	def load_from_string(self, data_string: str) -> dict:
		"""
        从 YAML 字符串加载数据

        参数:
        data_string (str): YAML 格式的字符串

        返回:
        dict: 解析后的字典数据，如果解析失败则返回空字典
        """
		try:
			return yaml.safe_load(data_string)
		except yaml.YAMLError:
			return {} # 处理 YAML 解码错误，初始化为空字典

	def save(self) -> None:
		"""
        保存数据到 YAML 文件
        如果保存过程中发生错误，将输出错误信息
        """
		if self.from_file:
			try:
				with open(self.filename, 'w', encoding='utf-8') as f:
					yaml.safe_dump(self.data, f)
			except IOError as e:
				print(f"Error saving data to file: {e}")
		else:
			print("Cannot save to string, instance was initialized with a YAML string.")


# 示例用法
if __name__ == "__main__":
	# # JSON 文件示例
	# storage_from_file = JsonStorage("data.json", from_file=True)
	# storage_from_file.set("person.name", "Alice")
	# storage_from_file.set("person.age", 30)
	# storage_from_file.set("address.city", "Wonderland")
	# storage_from_file.set("address.contacts", ["123456789", "987654321"])
	# storage_from_file.save()

	# print("Read data from JSON file:")
	# print("Name:", storage_from_file.get("person.name"))
	# print("Age:", storage_from_file.get("person.age"))
	# print("City:", storage_from_file.get("address.city"))
	# print("Contacts:", storage_from_file.get("address.contacts"))

	# # JSON 字符串示例
	# json_string = '{"person": {"name": "Bob", "age": 25}, "address": {"city": "Dreamland", "contacts": ["123123123", "321321321"]}}'
	# storage_from_string = JsonStorage(json_string, from_file=False)
	# print("Read data from JSON string:")
	# print("Name:", storage_from_string.get("person.name"))
	# print("Age:", storage_from_string.get("person.age"))
	# print("City:", storage_from_string.get("address.city"))
	# print("Contacts:", storage_from_string.get("address.contacts"))

	# # YAML 文件示例
	# yaml_storage_from_file = YamlStorage("data.yaml", from_file=True)
	# yaml_storage_from_file.set("person.name", "Charlie")
	# yaml_storage_from_file.set("person.age", 40)
	# yaml_storage_from_file.set("address.city", "Yamland")
	# yaml_storage_from_file.set("address.contacts", ["444444444", "555555555"])
	# yaml_storage_from_file.save()

	# print("Read data from YAML file:")
	# print("Name:", yaml_storage_from_file.get("person.name"))
	# print("Age:", yaml_storage_from_file.get("person.age"))
	# print("City:", yaml_storage_from_file.get("address.city"))
	# print("Contacts:", yaml_storage_from_file.get("address.contacts"))

	# # YAML 字符串示例
	# yaml_string = """
	# person:
	#   name: Dave
	#   age: 35
	# address:
	#   city: Wonderland
	#   contacts:
	#     - 987654321
	#     - 123456789
	# """
	# yaml_storage_from_string = YamlStorage(yaml_string, from_file=False)
	# print("Read data from YAML string:")
	# print("Name:", yaml_storage_from_string.get("person.name"))
	# print("Age:", yaml_storage_from_string.get("person.age"))
	# print("City:", yaml_storage_from_string.get("address.city"))
	# print("Contacts:", yaml_storage_from_string.get("address.contacts"))

	kvs = JsonStorage("", False)
	# kvs.set_value([], "a", "b", "c")
	# kvs.set_value(1, "a", "b", "c", "0")
	# kvs.set("a.b.c.1", 2)
	# kvs.set("a.b.c.2", 3)
	kvs.set_value(True, "a", "b", "c", 10)
	kvs.set_value("a.b.c.12", True)
	kvs.set("a.b.c.ddd", True)
	kvs.set("a.b.c.e", None)
	print(kvs.get_value("a", "b", "c"))
	print(kvs.get_value("a", "b", "c", "ddd"))
	print(kvs.get("a.b.c.e"))
	print(json.dumps(kvs.data))
