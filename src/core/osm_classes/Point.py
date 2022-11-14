"""
Abstraction of a (geographical) Point with x and y coordinates

Args
    x (float): x coordinate
    y (float): y coordinate

Attributes
    x (float): x coordinate
    y (float): y coordinate

"""


class Point():
	def __init__(self, x = 0, y = 0):
		self.x = x
		self.y = y
	
	def __str__(self):
		return "Point(x = {}, y = {})".format(self.x, self.y)



import core.tolerances as tolerances
from typing import Union
import math


def tupel_to_point(tupelsuspect):
	"""
	Converts a tupel to a Point instance if it isnt one already
	"""
	if not isinstance(tupelsuspect, Point):
		if isinstance(tupelsuspect, tuple):
			newp = Point(tupelsuspect[0], tupelsuspect[1])
			return newp
		else:
			raise ValueError('The function got something that is not a tupel nor a Point instance')
	else:
		return tupelsuspect
