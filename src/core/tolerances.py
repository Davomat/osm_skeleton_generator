""" This file contains the editable tolerances used for finding a cleaner output """


general_mapping_uncertainty = 0.00000001
""" a general uncertainty for not merged nodes """

point_to_point = 0.05
""" the distance between two way points at which they will still be combined into a single way point"""

barrier_to_room = 0.5
""" the distance from a barrier to a room edge to consider the barrier not being part of the room """

door_to_room = 0.5
""" the distance from a door to a from edge to consider the door belonging to the room """

ratio_barrier_in_barrier = 0.25
""" the part of a barrier that can be outside an inner polygon of a multipolygon
    and still be considered completely inside """
