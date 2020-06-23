"""
Nicholas Archer
2020/06/09

Roads are made of segments, and I nearly exploded with frustration writing code to work with overlapping or touching intervals.
"""

from __future__ import annotations

import itertools
import math
from typing import Iterable, Union, List, Any


class Interval:
	def __init__(self, start: float, end: float):
		"""To initialise self.start & self.end with a type other than float, make a subclass of Interval().
		This will give the best auto-completion and type checking results in pycharm.
		The subclass of interval only needs to provide a replacement for this __init__()

		Custom types used for self.start and self.end must:
		 - define __float__ AND
		 - define __lt__, __gt__, __le__, __ge__, __eq__, __ne__ AND
		 - these dunder methods must accept any argument type that has a __float__ method

		Optionally, the subclass must
			 - override @classmethod Interval.make_infinite_full(), and Interval.make_infinite_empty() otherwise a float('inf') value will be used
		"""
		self.start: float = start
		self.end: float = end
		
	@classmethod
	def make_infinite_full(cls) -> Interval:
		"""
		:return: full Interval, starting at negative infinity and ending at infinity
		"""
		# not using cls to construct; if cls using something SupportsFloat instead of float, there is no way for us to get the maximum and minimum value
		return Interval(-float('inf'), float('inf'))
	
	@classmethod
	def make_infinite_empty(cls) -> Interval:
		"""
		:return: empty Interval, starting at infinity and ending at negative infinity
		"""
		# not using cls to construct; if cls using something SupportsFloat instead of float, there is no way for us to get the maximum and minimum value
		return Interval(float('inf'), float('-inf'))

	def print(self):
		"""
		prints intervals and multi intervals like this for debugging (only works for integer intervals):
		  ├─────┤
			├──────┤    ├────┤
		"""
		out = f"{self.start: 5.0f} {self.end: 5.0f} :"
		for i in range(int(self.end) + 1):
			if i < self.start:
				out += " "
			elif self.start == i == self.end:
				out += "│"
			elif i == self.start:
				out += "├"
			elif i == self.end:
				out += "┤"
			else:
				out += "─"
		print(out)
	
	def __repr__(self):
		return f"{self.__class__.__name__}({self.start:.2f}, {self.end:.2f})"
	
	def __getitem__(self, item):
		if item == 0:
			return self.start
		elif item == 1:
			return self.end
		else:
			raise IndexError(f"Interval has only index [0] and [1]. tried to access {item}")
	
	def copy(self):
		return type(self)(self.start, self.end)
	
	def interpolate(self, ratio: float) -> Any:
		return (self.end - self.start) * ratio + self.start
	
	@property
	def is_valid(self) -> bool:
		"""
		:return: True, if interval start <= end, False otherwise
		"""
		return self.start <= self.end
	
	@property
	def is_infinitesimal(self) -> bool:
		"""
		:return: True, if interval start isclose to end, False otherwise
		"""
		return math.isclose(self.start, self.end)
	
	@property
	def length(self) -> Any:
		return self.end - self.start
	
	def point_is_within(self, point: Any) -> bool:
		return self.start < point < self.end
	
	def point_touches(self, point: Any) -> bool:
		return not self.point_is_within(point) and (math.isclose(self.start, point) or math.isclose(self.end, point))
	
	def positive(self) -> Interval:
		return Interval(
			min(self.start, self.end),
			max(self.start, self.end)
		)
	
	def intersect(self, other: Union[Interval, Multi_Interval]) -> Union[Interval, Multi_Interval, None]:
		"""
		No floating point weirdness is accounted for. Will return zero-length and 'infinitesimal' intersections
		if a multi_interval is passed in, the structure of the original multi interval is preserved;
		 we will simply return a new multi_interval where every sub_interval is the result of intersecting the old sub_intervals with this interval
		:param other:
		:return:
		"""
		if isinstance(other, Multi_Interval):
			result = Multi_Interval([])
			for sub_interval in other.intervals:
				f = self.intersect(sub_interval)
				if f is not None:
					result.add_overlapping(f)
			if not result.intervals:
				return None
			else:
				return result
		elif isinstance(other, Interval):
	
			#  |---|
			#        |---|
			if self.end < other.start:  # less than but not equal; zero length intersection will pass over
				return None
			
			#        |---|
			#  |---|
			if self.start > other.end:  # greater than but not equal; zero length intersection will pass over
				return None
			
			if self.start <= other.start:  # accepts equality; in the case of zero length intersections both return statements below are equivalent
				#  |---|
				#    |---|
				if self.end < other.end:
					return type(self)(other.start, self.end)
				
				#  |-------|
				#    |---|
				return type(self)(other.start, other.end)
			
			if self.start <= other.end:
				#    |---|
				#  |-------|
				if self.end < other.end:
					return type(self)(self.start, self.end)
				
				#    |---|
				#  |---|
				return type(self)(self.start, other.end)
	
	def union(self, other: Interval) -> Union[Interval, Multi_Interval]:
		if self.intersect(other) is not None:
			return self.hull(other)
		else:
			return Multi_Interval((self, other))
	
	def hull(self, other: Interval) -> Interval:
		return type(self)(min(self.start, other.start), max(self.end, other.end))
	
	def touches(self, other: Interval):
		"""
		:return: True if touching but not intersecting; ie self.start>=other.end and self.start isclose to other.end
		touches will return True if two adjacent intervals should be merged, but intersects() has returned False.
		"""
		if self.start >= other.end and math.isclose(self.start, other.end):
			return True
		if self.end <= other.start and math.isclose(self.end, other.start):
			return True
		return False
	
	def intersects(self, other: Interval) -> bool:
		return self.intersect(other) is not None
	
	def subtract(self, other: Union[Interval, Multi_Interval]) -> Union[Interval, Multi_Interval, None]:
		if isinstance(other, Multi_Interval):
			result = self.copy()
			for sub_interval in other.intervals:
				result = result.subtract(sub_interval)
			return result
		elif isinstance(other, Interval):
			
			#  |---|
			#        |---|
			if self.end <= other.start:
				return self.copy()
			
			#        |---|
			#  |---|
			if self.start >= other.end:
				return self.copy()
			
			if self.start <= other.start:
				#  |---|
				#    |---|
				if self.end < other.end:
					return type(self)(self.start, other.start)
				
				#  |-------|
				#    |---|
				return Multi_Interval((type(self)(self.start, other.start), type(self)(other.end, self.end)))
			
			if self.start < other.end:
				#    |---|
				#  |-------|
				if self.end < other.end:
					return None
				
				#    |---|
				#  |---|
				return type(self)(other.end, self.end)
			
			raise ValueError("Interval.subtract() had some kind of malfunction and did not find a result")
		else:
			raise NotImplementedError("Cannot subtract unknown type")
	

class Multi_Interval:

	def __init__(self, iter_intervals: Iterable[Interval]):
		""" Intervals provided to this initialiser are added without further processing.
		"""
		self.intervals: List[Interval] = []
		
		for interval in iter_intervals:
			self.intervals.append(interval)
	
	def __repr__(self):
		return f"Multi_Interval({self.intervals.__repr__()})"
		
	def print(self):
		print("Multi_Interval:")
		for sub_interval in self.intervals:
			sub_interval.print()
		print("")
	
	def __bool__(self):
		return bool(self.intervals)
	
	@property
	def start(self):
		if self.intervals:
			min_so_far = self.intervals[0].start
			for item in self.intervals:
				min_so_far = min(min_so_far, item.start)
			return min_so_far
		else:
			return None
	
	@property
	def end(self):
		if self.intervals:
			max_so_far = self.intervals[0].end
			for item in self.intervals:
				max_so_far = max(max_so_far, item.end)
			return max_so_far
		else:
			return None
	
	@property
	def is_valid(self) -> Union[bool, None]:
		if self.intervals:
			for item in self.intervals:
				if not item.is_valid:
					return False
			return True
		else:
			return None
	
	def subtract(self, interval_to_subtract: Interval):
		new_interval_list = []
		for interval in self.intervals:
			if interval.intersect(interval_to_subtract):
				f = interval.subtract(interval_to_subtract)
				if f is not None:
					try:
						# assume f is a Multi_Interval
						for pieces in f.intervals:
							new_interval_list.append(pieces)
					except:
						# f is an Interval
						new_interval_list.append(f)
			else:
				new_interval_list.append(interval)
		self.intervals = new_interval_list
		return self
	
	def add_overlapping(self, interval: Union[Interval, Multi_Interval]) -> Multi_Interval:
		"""Add to multi interval without further processing. Overlapping intervals will be preserved.
		this is the same as MultiInterval().intervals.append(Interval())
		:return: self
		"""
		if isinstance(interval, Interval):
			self.intervals.append(interval.copy())
		elif isinstance(interval, Multi_Interval):
			for sub_interval in interval.intervals:
				self.intervals.append(sub_interval.copy())
		else:
			raise ValueError()
		return self
	
	def add_hard(self, interval_to_add: Interval) -> Multi_Interval:
		"""Add to multi interval, truncating or deleting existing intervals to prevent overlaps with the new interval
		will result in touching intervals being maintained
		may result in infinitesimal interval being added
		:return: self
		"""
		# TODO: Make multi interval compatible
		self.subtract(interval_to_add)
		self.add_overlapping(interval_to_add)
		return self
	
	def add_soft(self, interval_to_add: Interval) -> Multi_Interval:
		"""Add Interval() to Multi_Interval(), truncating or ignoring the new interval to prevent overlaps with existing intervals
		will result in touching intervals being maintained
		may result in infinitesimal interval being added
		:return: self
		"""
		# TODO: Make multi interval compatible
		for interval in self.intervals:
			if interval.intersects(interval_to_add):
				interval_to_add = interval_to_add.subtract(interval)
				if interval_to_add is None:
					break
		
		if isinstance(interval_to_add, Multi_Interval):
			for sub_interval in interval_to_add.intervals:
				self.intervals.append(sub_interval.copy())
		elif isinstance(interval_to_add, Interval):
			self.add_overlapping(interval_to_add)
		elif interval_to_add is None:
			pass
		else:
			raise Exception("add soft failed")
		
		return self
		
	def add_merge(self, interval_to_add: Interval) -> Multi_Interval:
		"""Add Interval() to Multi_Interval(), merge with any overlapping or touching intervals to prevent overlaps
		preserves existing intervals that are touching, only merges existing intervals which touch or intersect with the new interval
		:return: self
		"""
		# TODO: Make multi interval compatible

		original_interval_to_add = interval_to_add
		
		must_restart = True
		while must_restart:
			must_restart = False
			for interval in self.intervals:
				if interval.intersects(original_interval_to_add) or interval.touches(original_interval_to_add):
					interval_to_add = interval_to_add.hull(interval)
					self.intervals.remove(interval)
					must_restart = True
					break
		self.intervals.append(interval_to_add)
		return self
	
	def merge_touching_and_intersecting(self) -> Multi_Interval:
		"""
		:return: eliminates all touching or intersecting intervals by merging
		"""
		must_restart = True
		while must_restart:
			must_restart = False
			for a, b in itertools.combinations(self.intervals, 2):
				if a.intersects(b) or a.touches(b):
					c = a.hull(b)
					self.intervals.remove(a)
					self.intervals.remove(b)
					self.intervals.append(c)
					must_restart = True
					break
		return self
	
	def delete_infinitesimal(self) -> Multi_Interval:
		self.intervals = [item for item in self.intervals if not item.is_infinitesimal]
		return self
	
	def make_all_positive(self):
		self.intervals = [interval.positive() for interval in self.intervals]
		return self
	
	def hull(self) -> Union[Interval, None]:
		if not self.intervals:
			return None
		else:
			result = None
			for sub_interval in self.intervals:
				if result is None:
					result = sub_interval.copy()
				else:
					result = result.hull(sub_interval)
			return result