import core.tolerances as tolerances
from typing import Union
import math
from core.osm_classes.Point import Point
from core.osm_classes.Line import Line

from core.osm_classes.debug import debugprint

class Edge():
	"""
	A class that represents a line with a fixed distance between two points.

	Attributes
	----------
	Point1 : Point
		The first point of the edge.
	Point2 : Point
		The second point of the edge.

	Args
	----------
	Point1 : Point
		The first point of the edge.
	Point2 : Point
		The second point of the edge.
	
	Methods
	-------
	is_point_on_edge(point, tolerance) -> bool
		Checks whether a point is on an edge (on the connection line between the two edge points).



    We need a Line() class and an Edge() class because converting 
    from an Edge to a Line is Possible but not the other way around.
	The "converting" from Edge to m and n is done on demand by the m and n properties.

    

         not possible
         --------->
    m, n           Point1, Point2
         <---------
         possible    

	"""
	def __init__(self, Point1, Point2):
		# check if points are an instance of Point class or of tuple
		if not isinstance(Point1, Point):
			Point1 = Point(Point1[0], Point1[1])
		if not isinstance(Point2, Point):
			Point2 = Point(Point2[0], Point2[1])
		self.Point1 = Point1
		self.Point2 = Point2
	
	@property
	def m(self):
		return (self.Point2.y - self.Point1.y) / (self.Point2.x - self.Point1.x)
	
	@property
	def n(self):
		return self.Point1.y - self.m * self.Point1.x


	def is_point_on_edge(self, point, tolerance: float = tolerances.general_mapping_uncertainty) -> bool:
		"""
		Checks whether a point is on an edge (on the connection line between the two edge points).
		"""
		if almost_same_point(point, self.Point1) or almost_same_point(point, self.Point2):
			return True
		debugprint("EdgePoint1: " + str(self.Point1))
		debugprint("EdgePoint2: " + str(self.Point2))
		tmpL = get_line(self.Point1, self.Point2)
		m, b = tmpL.m, tmpL.n
		m_orthogonal, b_orthogonal = get_orthogonal_line(m, point)
		intersection_point = intersection(m, m_orthogonal, b, b_orthogonal)
		if almost_same_point(point, intersection_point, tolerance) \
				and min(self.Point1.x, self.Point2.x) <= intersection_point.x <= max(self.Point1.x, self.Point2.x) \
				and min(self.Point1.y, self.Point2.y) <= intersection_point.y <= max(self.Point1.y, self.Point2.y):
			return True
		return False
	
	def __str__(self):
		return "Edge from {} to {}".format(self.Point1, self.Point2)



import core.tolerances as tolerances
from typing import Union
import math



def almost_same_point(point_a: Point, point_b: Point,
					  tolerance: float = tolerances.general_mapping_uncertainty) -> bool:
	"""
	Checks whether 2 points have almost the same coordinates
	"""


	if point_a is None or point_b is None:
		return False
	return almost_same(point_a.x, point_b.x, tolerance) and almost_same(point_a.y, point_b.y, tolerance)


def almost_same(value1: float, value2: float, tolerance: float = tolerances.general_mapping_uncertainty) -> bool:
	"""
	Checks whether 2 values are in the same range within a specific tolerance.
	"""
	return math.isclose(value1, value2, abs_tol=tolerance)

def get_orthogonal_line(m: Union[float, None], point: tuple[float, float]) -> Union[tuple[float, float],
																					tuple[None, float]]:
	"""
	Calculates an orthogonal line going through the given point.
	"""
	# TODO: warum gibt diese Funktion ein tupel zurück und es funktioniert trotzdem?
	# Wer benutzt das?
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

def get_line(point1: Point, point2: Point) -> Line: #TODO: Was zum fick!?
	"""
	Finds the values of the linear equation (y = mx + n) for 2 given points.
	"""
	# TODO: eigentlich brauche ich das gar nicht, die Edge, die hier rauskommt kann man nach ihrem
	# m und n fragen

	x1 = point1.x
	y1 = point1.y
	x2 = point2.x
	y2 = point2.y
	if almost_same(x1, x2):  # Bei Senkrechten für b stattdessen den gemeinsamen x-Wert speichern
		return Line(None, x1)
	m = (y1 - y2) / (x1 - x2)
	n = y1 - m * x1
	return Line(m, n)