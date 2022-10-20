
from core.osm_classes.helper import *
import core.tolerances as tolerances
from typing import Union
import math

class Point():
	def __init__(self, x = 0, y = 0):
		self.x = x
		self.y = y
	
	def __str__(self):
		return "Point(x = {}, y = {})".format(self.x, self.y)



import core.tolerances as tolerances
from typing import Union
import math

def wzip(a: list, b: list):
	# TODO: Umbenennen, aussagekräftigere Var namen
	r = min(len(a), len(b))
	result = [(a[i], b[i]) for i in range(r)]
	#for i in range(r):
	#	result.append((a[i], b[i]))

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

def almost_same_point(point_a: Point, point_b: Point,
                      tolerance: float = tolerances.general_mapping_uncertainty) -> bool:
    """
    Checks whether 2 points have almost the same coordinates
    """
    # Wir sind hier noch nicht fertig!

    # check if the points are of class Point or tuple
    # if tuple, convert to Point
    if not isinstance(point_a, Point):
        point_a = Point(point_a[0], point_a[1])
    if not isinstance(point_b, Point):
        point_b = Point(point_b[0], point_b[1])


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
