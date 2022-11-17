from core.osm_classes.Point import Point
from typing import Union

class Line():
	"""
    An abstraction for a line of the form y = mx + n

    We need a Line() class and an Edge() class because converting 
    from an Edge to a Line is Possible but not the other way around.
    

	    not possible
	    --------->
    m, n           Point1, Point2
	    <---------
	    possible    
    """

	# TODO: M und N als eigenschaften der Edge-Klasse (property?)
	# Beim init der Edge-Klasse berechnen statt zu übergeben
	def __init__(self, m, n):
		self.m = m
		self.n = n

	def __str__(self):
		return "Line " + str(self.m) + "x + " + str(self.n)

	@staticmethod
	def get_orthogonal_line(m, point):
		"""
		Calculates an orthogonal line going through the given point.
		"""
		x = point.x
		y = point.y
		if m == 0:
			m2 = None
			n2 = x
		elif m is None:
			m2 = 0
			n2 = y
		else:
			m2 = -1 / m
			n2 = y - m2 * x
		return m2, n2

	@staticmethod
	def intersection(m1: float, m2: float, n1: float, n2: float) -> Union[None, Point]:
		"""
		Finds the intersection between two lines (if there is exactly one) given with y = mx + n.
		"""
		if m1 is None and m2 is None:
			return None  # either no intersection or infinite number of intersections

		if m1 is None:
			x2 = n1
			y2 = m2 * x2 + n2

		elif m2 is None:
			x2 = n2
			y2 = m1 * x2 + n1

		elif almost_same(m1, m2):
			return None

		else:
			x2 = (n2 - n1) / (m1 - m2)
			y2 = m1 * x2 + n1
		return Point(x2, y2)