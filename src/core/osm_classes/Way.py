import core.tolerances as tolerances
from typing import Union
import math
from core.osm_classes import *

class Way():
	def __init__(self, points, level=None):
		self.points = points
		self.level = level
	
	def __str__(self):
		return "Way(points = {}, level = {})".format(self.points, self.level)


