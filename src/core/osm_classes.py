
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

	def simplify(self):
		index = 0
		index_prev = len(self.points) - 1
		index_next = 1
		while index_next < len(self.points):
			point = self.points[index]
			print(self.points[index])
			point_prev = self.points[index_prev]
			point_next = self.points[index_next]
			if point_is_on_edge(point, Edge(point_prev, point_next)):
				del self.points[index]
				if index == 0:
					index_prev -= 1
			else:
				index_prev = index
				index += 1
				index_next += 1

def __str__(self):
	return "Polygon(points = {}, level = {})".format(self.points, self.level)

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


