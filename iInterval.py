"""
Nicholas Archer
2020-10-08

Roads are made of segments, and I nearly exploded with frustration writing code to work with overlapping or touching intervals.
Also I am using this to process midi files.
"""

from __future__ import annotations

import itertools
import math
from typing import Iterable
from typing import Tuple

from .Linked_iBound import Linked_iBound
from .iBound import PART_OF_LEFT
from .iBound import PART_OF_RIGHT
from .iBound import iBound
from .iBound import iBound_Negative_Infinity
from .iBound import iBound_Positive_Infinity

import NicksIntervals._operators as ops
import NicksIntervals.iMulti_iInterval


class iInterval:
	"""Immutable Interval based on python's built in floats. Nothing fancy."""
	
	@classmethod
	def complete(cls):
		"""returns an interval spaning the complete real number line. Or at least all representable python floats."""
		return iInterval(
			lower_bound=iBound_Negative_Infinity,
			upper_bound=iBound_Positive_Infinity
		)
	
	@classmethod
	def degenerate(cls, value: float = 0.0):
		"""returns a zero-length 'degenerate' interval"""
		return iInterval(
			lower_bound=iBound(value, PART_OF_RIGHT),
			upper_bound=iBound(value, PART_OF_LEFT)
		)
	
	@classmethod
	def closed(cls, lower_bound: float, upper_bound: float):
		return iInterval(iBound(lower_bound, PART_OF_RIGHT), iBound(upper_bound, PART_OF_LEFT))
	
	@classmethod
	def open(cls, lower_bound: float, upper_bound: float):
		return iInterval(iBound(lower_bound, PART_OF_LEFT), iBound(upper_bound, PART_OF_RIGHT))
	
	@classmethod
	def open_closed(cls, lower_bound: float, upper_bound: float):
		return iInterval(iBound(lower_bound, PART_OF_LEFT), iBound(upper_bound, PART_OF_LEFT))
	
	@classmethod
	def closed_open(cls, lower_bound: float, upper_bound: float):
		return iInterval(iBound(lower_bound, PART_OF_RIGHT), iBound(upper_bound, PART_OF_RIGHT))
	
	@classmethod
	def inf_open(cls, upper_bound: float):
		return iInterval(iBound_Negative_Infinity, iBound(upper_bound, PART_OF_RIGHT))
	
	@classmethod
	def open_inf(cls, lower_bound: float):
		return iInterval(iBound(lower_bound, PART_OF_LEFT), iBound_Positive_Infinity)
	
	@classmethod
	def closed_inf(cls, lower_bound: float):
		return iInterval(iBound(lower_bound, PART_OF_RIGHT), iBound_Positive_Infinity)
	
	@classmethod
	def inf_closed(cls, upper_bound: float):
		return iInterval(iBound_Negative_Infinity, iBound(upper_bound, PART_OF_LEFT))
	
	@classmethod
	def inf(cls):
		"""Alias of .complete()"""
		return iInterval(iBound_Negative_Infinity, iBound_Positive_Infinity)
	
	@classmethod
	def empty(cls):
		"""returns a null or non-interval which is still of the type Iterable[iInterval] but will yield no items"""
		return NicksIntervals.iMulti_iInterval.iMulti_iInterval([])
	
	def __init__(self, lower_bound: iBound, upper_bound: iBound):
		try:
			assert isinstance(lower_bound, iBound)
			assert isinstance(upper_bound, iBound)
		except AssertionError:
			raise TypeError("Bounds must be an instance of iBound")
		
		self.__lower_bound: iBound = lower_bound
		self.__upper_bound: iBound = upper_bound
		
		self.__is_infinitesimal: bool = False
		self.__is_degenerate: bool = False
		
		if lower_bound.value == upper_bound.value:
			if self.__lower_bound.part_of_right and self.__upper_bound.part_of_left:
				self.__is_degenerate = True
			else:
				raise Exception(f"Degenerate intervals (lower_bound==upper_bound) are only permitted when both bounds are closed.")
		elif math.isclose(lower_bound.value, upper_bound.value):
			self.__is_infinitesimal = True
			# TODO: emit warning? infinitesimal intervals will cause havoc with other algorithms
			#  im really on the fence about this one. i think i need to do more research about precision models
			#  ima raise an exception here until i have a better idea.
			raise Exception(f"Infinitesimal intervals are not cool: {lower_bound} <= {upper_bound} == {lower_bound<=upper_bound}")
		elif lower_bound.value > upper_bound.value:
			raise Exception(f"reversed intervals are not permitted. lower_bound.value must be less than or equal to upper_bound.value: {lower_bound} <= {upper_bound} == {lower_bound.value<=upper_bound.value}")
		
	def __format__(self, format_spec):
		char_left = f"{format(float(self.__lower_bound.value), format_spec)}"
		char_right = f"{format(float(self.__upper_bound.value), format_spec)}"
		
		if self.__lower_bound == iBound_Negative_Infinity:
			char_left = "-∞"
		
		if self.__upper_bound == iBound_Positive_Infinity:
			char_right = "+∞"
		
		if self.__lower_bound.part_of_right:
			char_left = "≤"+char_left  # ≤ [
		else:
			char_left = "<" + char_left  # < (
		
		if self.__upper_bound.part_of_left:
			char_right = char_right+"≥"  # ≥ ]
		else:
			char_right = char_right+">"  # > )
		return f"{char_left}, {char_right}"
		
	def __repr__(self):
		return format(self, ".3f")
	
	def __iter__(self):
		return iter((self,))
	
	def __bool__(self):
		return True
	
	def print(self):
		"""
		prints intervals and multi intervals like this for debugging (only works for integer intervals):
		╠═════╣
			╠═════╣    ╞═══╣
		"""
		lbv = round(self.__lower_bound.value) if math.isfinite(self.__lower_bound.value) else (-999 if self.__lower_bound.value == float('-inf') else 999)
		ubv = round(self.__upper_bound.value) if math.isfinite(self.__upper_bound.value) else (-999 if self.__upper_bound.value == float('-inf') else 999)
		out = f"{self:2.0f} :"
		for i in range(0, min(50, ubv) + 1):
			if i < lbv:
				out += " "
			elif lbv == i == ubv:
				out += "║"
			elif i == lbv:
				if self.__lower_bound.part_of_right:
					out += "╠"
				else:
					out += "╞"
			elif i == ubv:
				if self.__upper_bound.part_of_left:
					out += "╣"
				else:
					out += "╡"
			else:
				out += "═"
		print(out)
		return self
	
	@property
	def lower_bound(self) -> iBound:
		return self.__lower_bound
	
	@property
	def upper_bound(self) -> iBound:
		return self.__upper_bound
	
	def get_linked_bounds(self) -> Tuple[Linked_iBound, Linked_iBound]:
		return (
			self.__lower_bound.get_Linked_iBound(linked_interval=self, is_lower_bound=True),
			self.__upper_bound.get_Linked_iBound(linked_interval=self, is_lower_bound=False)
		)
	
	@property
	def is_degenerate(self) -> bool:
		return self.__is_degenerate
	
	@property
	def is_infinitesimal(self) -> bool:
		return self.__is_infinitesimal
	
	@property
	def is_complete(self) -> bool:
		return self.__lower_bound.value == float('-inf') and self.__upper_bound.value == float('inf')
	
	@ property
	def length(self) -> float:
		return self.__upper_bound.value - self.__lower_bound.value
	
	def interpolate(self, ratio: float) -> float:
		return self.__lower_bound.value + (self.__upper_bound.value - self.__lower_bound.value) * ratio
	
	def contains_value(self, value: float) -> bool:
		return ops.contains_value_atomic(self, value)
	
	def contains_upper_bound(self, bound: iBound) -> bool:
		return ops.contains_upper_bound_atomic(self, bound)
	
	def contains_lower_bound(self, bound: iBound) -> bool:
		return ops.contains_lower_bound_atomic(self, bound)
		
	def contains_interval(self, other: Iterable[iInterval]) -> bool:
		return ops.contains_interval(self, other)
	 
	# @property
	# def left_exterior(self) -> Iterable[iInterval]:
	# 	return ops.left_exterior_atomic(self)
	#
	# @property
	# def right_exterior(self) -> Iterable[iInterval]:
	# 	return ops.right_exterior_atomic(self)
		
	@property
	def exterior(self) -> Iterable[iInterval]:
		return NicksIntervals.iMulti_iInterval.iMulti_iInterval(ops.exterior_atomic(self))
	
	def touches(self, other: Iterable[iInterval]) -> bool:
		for other_interval in other:
			if math.isclose(self.__lower_bound.value, other_interval.__upper_bound.value) and (self.__lower_bound.part_of_right == other_interval.__upper_bound.part_of_right):
				return True
			if math.isclose(self.__upper_bound.value, other_interval.__lower_bound.value) and (self.__upper_bound.part_of_left == other_interval.__lower_bound.part_of_left):
				return True
		return False
	
	def intersects(self, other: Iterable[iInterval]) -> bool:
		return ops.intersects(self, other)
	
	def disjoint(self, other: Iterable[iInterval]):
		return not ops.intersects(self, other)
	
	def intersect(self, other: Iterable[iInterval]) -> Iterable[iInterval]:
		return ops.intersect(self, other)
		
	
	def subtract(self, other_intervals: Iterable[iInterval]) -> NicksIntervals.iMulti_iInterval.iMulti_iInterval:
		result = [self]
		for other_interval in other_intervals:
			
			interim_result = []
			for self_interval in result:
				
				other_contains_self_lower_bound = other_interval.contains_lower_bound(self_interval.__lower_bound)
				other_contains_self_upper_bound = other_interval.contains_upper_bound(self_interval.__upper_bound)
				
				#   self:        ╠════╣
				#  other:  ╠════════════╣
				# result:
				if other_contains_self_lower_bound and other_contains_self_upper_bound:
					continue
				
				self_contains_other_lower_bound = self_interval.contains_lower_bound(other_interval.__lower_bound)
				self_contains_other_upper_bound = self_interval.contains_upper_bound(other_interval.__upper_bound)
				
				#   self:  ╠════════════╣
				#  other:        ╠════╣
				# result:  ╠═════╡    ╞═╣
				if self_contains_other_lower_bound and self_contains_other_upper_bound:
					if self_interval.__lower_bound != other_interval.__lower_bound:
						interim_result.append(iInterval(self_interval.__lower_bound, other_interval.__lower_bound))
					if other_interval.__upper_bound != self_interval.__upper_bound:
						interim_result.append(iInterval(other_interval.__upper_bound, self_interval.__upper_bound))
					continue
				
				#   self:        ╠══════════╣
				#  other:  ╠════════════╣
				# result:               ╞═══╣
				if other_contains_self_lower_bound:
					if other_interval.__upper_bound != self_interval.__upper_bound:
						interim_result.append(iInterval(other_interval.__upper_bound, self_interval.__upper_bound))
					continue
				
				#   self:        ╠════╣
				#  other:  ╠════════════╣
				# result:
				# if other_contains_self_lower_bound and other_contains_self_upper_bound:
				# 	pass
				#   continue
				
				#   self:    ╠══════════╣
				#  other:        ╠════════════╣
				# result:    ╠═══╡
				if other_contains_self_upper_bound:
					if self_interval.__lower_bound != other_interval.__lower_bound:
						interim_result.append(iInterval(self_interval.__lower_bound, other_interval.__lower_bound))
					continue
					
				# if execution makes it past all above continues, the only remaining possibility is that the intervals are disjoint
				# in this case the entire self interval is output
				interim_result.append(self_interval)
			result = interim_result
			
		return NicksIntervals.iMulti_iInterval.iMulti_iInterval(result)
	
	def hull(self, other: Iterable[iInterval]) -> Iterable[iInterval]:
		result_lower_bound = self.__lower_bound
		result_upper_bound = self.__upper_bound
		for other_interval in other:
			if other_interval.__lower_bound < result_lower_bound:
				result_lower_bound = other_interval.__lower_bound
			if other_interval.__lower_bound > result_upper_bound:
				result_upper_bound = other_interval.__upper_bound
		return iInterval(result_lower_bound, result_upper_bound)
	
	def union(self, other: Iterable[iInterval]) -> Iterable[iInterval]:
		return NicksIntervals.iMulti_iInterval.iMulti_iInterval(itertools.chain(self, other))
