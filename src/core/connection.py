from typing import Union

from core.geometry import centroid, add_doors_to_polygon
from core.osm_helper import write_python_way
from core.osm_classes import *


class Connection:
    """
    A representation of a link between several floors saved as ways.

    Args
    ----
    members : list[dict[str, Union[list[tuple[float, float]], str]]]
        A list of polygons that are connected and their level.
    con_type : str
        The type of connection between the members (stairs/elevator).

    Attributes
    ----------
    members : list[
                    dict[
                        str, 
                        Union[
                            list[
                                tuple[float, float]
                                ],
                            str
                        ]
                    ]
                ]
            NEU -> list[Polygon]
        A list of polygons (that are connected) and their level.
    con_type : str
        The type of connection between the members (stairs/elevator).
    ways : list[dict[str, Union[list[tuple[float, float]], str]]]
        The calculated ways with their type and level information for later navigation.

    Methods
    -------
    find_ways(all_doors: dict[str, list[tuple[float, float]]]) : list[dict[str, Union[list[tuple[float, float]], str]]]
        Calculates the ways for navigation inside the room.
    """

    def __init__(self, members: list[Polygon], con_type: str):
        self.members: list[Polygon] = members
        self.type = con_type
        self.ways = []

    def find_ways(self, all_doors: dict[str, list[tuple[float, float]]]) \
            -> list[dict[str, Union[list[tuple[float, float]], str]]]:
        """
        Calculates the ways for navigation inside the room.
        """

        for member in self.members:
            tmpP = Polygon(member["connector"], member["level"])
            member = tmpP

        centres = []
        for connector in self.members:
            centre = centroid(connector['connector'][:-1])
            # use the centroid of the connector as representative point --> TODO: find better solution!!
            level = connector['level']
            centres.append({'level': level, 'centre': centre})

            if level in all_doors:  # check if there are any doors on the same level
                doors = add_doors_to_polygon(connector['connector'], all_doors[level])
                for door in doors:
                    self.ways.append(write_python_way([centre, door], level, self.type))

        if self.type == 'stairs':
            for i in range(len(centres) - 1):
                self.ways.append(write_python_way([centres[i]['centre'], centres[i + 1]['centre']],
                                                  centres[i]['level'] + ';' + centres[i + 1]['level'],
                                                  self.type))
        else:  # elevator
            for i in range(len(centres) - 1):
                for j in range(i + 1, len(centres)):
                    self.ways.append(write_python_way([centres[i]['centre'], centres[j]['centre']],
                                                      centres[i]['level'] + ';' + centres[j]['level'],
                                                      self.type))

        return self.ways
