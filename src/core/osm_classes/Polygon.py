import core.tolerances as tolerances
from typing import Union
import math

from core.osm_classes.Point import Point
from core.osm_classes.Line import Line
from core.osm_classes.Edge import Edge

from core.osm_classes.debug import debugprint


class Polygon():
	"""
	A polygon is a closed way with at least 3 points

	Args
	----
	points : list[tuple[float, float]]
		A list of points that form the polygon.
	level : str
		The level of the polygon.

	Attributes
	----------
	points : list[Point]
		A list of points that form the polygon.
	level : str
		The level of the polygon.
	
	Methods
	-------
	centroid()
		Calculate the centroid of a polygon.
	area()
		Calculate the area of a polygon.
	simplify()
		Simplify the polygon by removing points that are on a straight line.
	to_tuples()
		Convert the polygon to a list of tuples. (This is needed for some functions in other modules (polyskel))
	is_closed()
		Check if the polygon is closed. (We can only calculate the area of a closed polygon)

	"""
	def __init__(self, points, level=None):
		self.points = points
		self.level = level
	
	# Wenn das Polygon nach seiner Länge gefragt wird, ist die Anzahl der Punkte gemeint
	def __len__(self):
		return len(self.points)

	def __getitem__(self, index):
		return self.points[index]

	def insert(self, index, point):
		self.points.insert(index, point)

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
			debugprint(self.points[index])
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
