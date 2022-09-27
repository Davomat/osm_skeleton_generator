
import core.tolerances as tolerances
from typing import Union
import math

# In dieser Datei sind einige Hilfsklassen für OSM-Objekte definiert, mit denen sich der Code besser lesen lässt

# TODO: Jede Klasse sollte eine Datei sein

def wzip(a,b):
	r = min(len(a), len(b))
	result = []
	for i in range(r):
		result.append((a[i], b[i]))

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

class Point():
	def __init__(self, x = 0, y = 0):
		self.x = x
		self.y = y
	
	def __str__(self):
		return "Point(x = {}, y = {})".format(self.x, self.y)

# Da ist noch irgendwas whack dran, eigenlich sind Barrieren Polygone
class Barrier():
	def __init__(self, polygon, name):
		self.polygon = polygon
		self.name = name
	
	def simplify(self):
		# Exposed das simplify des Polygons nach draussen, 
		# damit für jedes Objekt, egal ob polygon oder höhere abstraktionsform
		# einfach objekt.simplify() aufgerufen werden kann
		self.polygon.simplify()

	def __str__(self):
		return "Barrier(polygon = {}, name = {})".format(self.polygon, self.name)
	
	def __repr__(self):
		return self.__str__()

class Polygon():
	def __init__(self, points, level=None):
		self.points = points
		self.level = level
	
	# Calculate the centroid of a polygon. brew: Das war Copilot, testen, ob das Funktioniert
	def centroid(self):
		x = 0
		y = 0
		for point in self.points:
			x += point.x
			y += point.y
		x /= len(self.points)
		y /= len(self.points)
		return Point(x, y)
	
	# Calculate the area of a polygon. brew: Das war Copilot, testen, ob das Funktioniert
	def area(self):
		area = 0
		for i in range(len(self.points)):
			j = (i + 1) % len(self.points)
			area += self.points[i].x * self.points[j].y
			area -= self.points[j].x * self.points[i].y
		area /= 2
		return area

	# Übernimmt die Funktion von simplify_polygons aus der Parser-Klasse
	def simplify(self):
		index = 0
		index_prev = len(self.points) - 1
		index_next = 1
		while index_next < len(self.points):
			point = self.points[index]
			print(self.points[index])
			point_prev = self.points[index_prev]
			point_next = self.points[index_next]
			if Edge(point_prev, point_next).is_point_on_edge(point):
				del self.points[index]
				if index == 0:
					index_prev -= 1
			else:
				index_prev = index
				index += 1
				index_next += 1

	# Obwohl wir eigentlich von Tuples wegwollten, könnte es sein dass einige Funktionen 
	# von anderen Modulen noch auf Tuples angewiesen sind, deswegen hier eine Funktion
	def to_tuples(self):
		tuples = []
		for point in self.points:
			tuples.append((point.x, point.y))
		return tuples

	def is_closed(self):
		return self.points[0] == self.points[-1]

	def __str__(self):
		return "Polygon(points = {}, level = {})".format(self.points, self.level)


class Way():
	def __init__(self, points, level=None):
		self.points = points
		self.level = level
	
	def __str__(self):
		return "Way(points = {}, level = {})".format(self.points, self.level)


class Edge():
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
		print("EdgePoint1: " + str(self.Point1))
		print("EdgePoint2: " + str(self.Point2))
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
	

class Line():
	"""
	Eine Abstraktion für eine Linie der Form y = mx + n
	"""

	# TODO: M und N als eigenschaften der Edge-Klasse (property?)
	# Beim init der Edge-Klasse berechnen statt zu übergeben
	def __init__(self, m, n):
		self.m = m
		self.n = n

	def __str__(self):
		return "Line " + str(self.m) + "x + " + str(self.n)



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

    # !! Extrem dreckiger code, der entfernt werden sollte, wenn alle Klassen konvertiert sind
    # convert Polygon to list[Point] if it isnt already
    if not isinstance(point1, Point):
        print("get_line konvertiert tupel zu Point")
        point1 = Point(point1[0], point1[1])
    if not isinstance(point2, Point):
        point2 = Point(point2[0], point2[1])
    


    x1 = point1.x
    y1 = point1.y
    x2 = point2.x
    y2 = point2.y
    if almost_same(x1, x2):  # Bei Senkrechten für b stattdessen den gemeinsamen x-Wert speichern
        return Line(None, x1)
    m = (y1 - y2) / (x1 - x2)
    n = y1 - m * x1
    return Line(m, n)