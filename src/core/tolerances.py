
""" a general uncertainty for not merged nodes """
general_sloppy_mapping = 0.00000001

""" the distance from a barrier to a room edge to consider the barrier not being part of the room """
barrier_to_room = 0.5

""" the distance from a door to a foom edge to consider the door belonging to the room """
door_to_room = 0.5

""" the part of a barrier that can be outside an inner polygon of a multipolygon
    and still be considered completely inside """
ratio_barrier_in_barrier = 0.25
