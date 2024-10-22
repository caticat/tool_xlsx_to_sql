import time


class PerfTimer:
	"""调用间隔计算器"""

	def __init__(self) -> None:
		self.__tick: float = time.perf_counter()

	def tick(self) -> float:
		now = time.perf_counter()
		interval = round(now - self.__tick, 3)
		self.__tick = now
		return interval
