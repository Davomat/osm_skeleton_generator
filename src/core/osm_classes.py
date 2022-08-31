
# In dieser Datei sind einige Hilfsklassen für OSM-Objekte definiert, mit denen sich der Code besser lesen lässt

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

class Barrier():
	def __init__(self, Point, desc):
		self.Point = Point
		self.desc = desc

	def __str__(self):
		return "Barrier at " + str(self.Point) + ": " + self.desc
	
class Edge():
	def __init__(self, Point1, Point2):
		# check if points are an instance of Point class or of tuple
		if not isinstance(Point1, Point):
			Point1 = Point(Point1[0], Point1[1])
		if not isinstance(Point2, Point):
			Point2 = Point(Point2[0], Point2[1])
		self.Point1 = Point1
		self.Point2 = Point2

	def __str__(self):
		return "Edge from " + str(self.Point1) + " to " + str(self.Point2) + ": " + self.desc

class Line():
	"""
	Eine Abstraktion für eine Linie der Form y = mx + n
	"""
	def __init__(self, m, n):
		self.m = m
		self.n = n

	def __str__(self):
		return "Line " + str(self.m) + "x + " + str(self.n)


class Polygon():
	# A polygon is a list of Points
	def __init__(self, Points):
		self.Points = Points
	

	def __str__(self):
		pointstr = "("
		for point in self.Points:
			pointstr += str(point) + ", "
		return "Polygon with " + str(len(self.Points)) + " Points" + pointstr + ")"

