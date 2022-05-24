""" This file contains the editable tolerances used for finding a cleaner output """


general_mapping_uncertainty = 0.0000001  # 0.0000001
""" a general uncertainty for not merged nodes """

point_to_point = 0.000002  # 0.000002
""" the maximum distance between two way points at which they will be combined into a single way point"""

barrier_to_room = 0.000002  # 0.000002
""" the minimum distance from a barrier to a room edge to be considered as part of the room """

door_to_room = 0.000005  # 0.000005
""" the maximum distance from a door to an edge to belong to the room """

ratio_barrier_in_barrier = 0.25  # 0.25
""" the part of a barrier that can be outside an inner polygon of a multipolygon
    and still be considered completely inside """
