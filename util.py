from itertools import chain
from itertools import islice
from itertools import tee
from typing import Any
from typing import Iterable
from typing import Iterator
from typing import Tuple


# credit to nosklo https://stackoverflow.com/questions/1011938/python-loop-that-also-accesses-previous-and-next-values
def iter_previous_and_next(some_iterable: Iterable, none_value: Any = None) -> Iterator[Tuple[Any, Any, Any]]:
	previous_items, current_items, next_items = tee(some_iterable, 3)
	previous_items = chain([none_value], previous_items)
	next_items = chain(islice(next_items, 1, None), [none_value])
	return zip(previous_items, current_items, next_items)


def first_and_last(iterable: Iterator) -> Tuple[Any, Any]:
	is_first = True
	last_item = None
	for item in iterable:
		if is_first:
			is_first = False
			yield item
		last_item = item
	yield last_item


# My recent dive into Haskell youtube videos is haunting my codebase:
# def iter_iBound_from_iter_Linked_iBound(iter_Linked_iBound:Iterable[Linked_iBound]) -> Iterator[iBound]:
# 	return (linked_bound.bound for linked_bound in iter_Linked_iBound)
#
#
# def iter_iBounds_with_infinities(iter_bounds: Iterable[iBound]) -> Iterator[Tuple[iBound, iBound, bool]]:
# 	""" returns an iterator yielding a tuple;
# 		(
# 			the last bound : iBound | None,
# 			the current bound : iBound,
# 			interior=True or exterior=False : bool
# 		)
# 	"""
# 	INTERIOR = True
# 	EXTERIOR = False
# 	previous_bound_and_current_bound_form_interior_interval = INTERIOR
# 	for previous_bound, bound, next_bound in iter_previous_and_next(iter_bounds):
# 		if previous_bound is None:
# 			if bound != iBound_Negative_Infinity:
# 				yield iBound_Negative_Infinity, bound, EXTERIOR
# 				previous_bound_and_current_bound_form_interior_interval = INTERIOR
# 			else:
# 				yield iBound_Negative_Infinity, bound, INTERIOR
# 				previous_bound_and_current_bound_form_interior_interval = EXTERIOR
# 		else:
# 			yield previous_bound, bound, previous_bound_and_current_bound_form_interior_interval
# 			previous_bound_and_current_bound_form_interior_interval = not previous_bound_and_current_bound_form_interior_interval
# 			if next_bound is None:
# 				if bound != iBound_Positive_Infinity:
# 					yield bound, iBound_Positive_Infinity, EXTERIOR