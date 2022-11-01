import core.tolerances as tolerances
from typing import Union
import math
from core.osm_classes.Point import Point

print("================")
print(Point)
print("================")


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



