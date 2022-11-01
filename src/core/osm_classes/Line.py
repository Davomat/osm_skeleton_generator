import core.tolerances as tolerances
from typing import Union
import math
from core.osm_classes.Point import Point

print("================")
print(Point)
print("================")


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



