import copy
from typing import Union

import core.polyskel2 as polyskel
from core.geometry import *
from core.osm_helper import write_python_way


class Room:
    """
    A class to store information about OSM rooms and corridors.

    Args
    ----
    polygon : list[tuple[float, float]]
        A list of points that defines the outer shell of the room's inner area.
    level : str
        The value of the floor on which the room is.
    barriers : list[list[tuple[float, float]]]
        The objects inside the room that represent obstacles like poles or bookcases.

    Attributes
    ----------
    polygon : list[tuple[float, float]]
        A list of points that defines the outer shell of the room's inner area.
    level : str
        The value of the floor on which the room is.
    doors : list[tuple[float, float]]
        The representations of doors as points.
    ways : list[dict[str, Union[list[tuple[float, float]], str]]]
        The calculated ways with their type and level information for later navigation.
    decision_nodes : list[tuple[float, float]]
        The points that connect more than 1 ways / 2 way segments.
    barriers : list[list[tuple[float, float]]]
        The objects inside the room that represent obstacles like poles or bookcases.

    Methods
    -------
    add_doors(all_doors: dict[str, list[tuple[float, float]]]) :
        Finds and adds the doors that belong to the room.
    find_ways(self, simplify_ways: bool, door_to_door: bool) : list[dict[str, Union[list[tuple[float, float]], str]]]
        Calculates the ways for navigation inside the room.
    """

    def __init__(self, polygon: list[tuple[float, float]], level: str,
                 barriers: list[list[tuple[float, float]]] = None):
        self.polygon = copy.copy(polygon)
        self.level = level
        self.doors = []
        self.ways = []
        self.decision_nodes = []
        self.barriers = []
        if barriers is not None:
            self.barriers = copy.deepcopy(barriers)
        simplify_room(self.polygon, self.barriers)
        if not anti_clockwise(self.polygon):
            self.polygon.reverse()

        for barrier in self.barriers:
            if anti_clockwise(barrier):  # the points of holes in the polygon must be passed in clockwise order
                barrier.reverse()

    def add_doors(self, all_doors: dict[str, list[tuple[float, float]]]):
        """
        Finds and adds the doors that belong to the room.
        """
        if self.level in all_doors:
            self.doors = add_doors_to_polygon(self.polygon, all_doors[self.level])
            for i in range(len(self.barriers)):
                doors = add_doors_to_polygon(self.barriers[i], all_doors[self.level])
                self.doors += doors

    def find_ways(self, simplify_ways: bool, door_to_door: bool) \
            -> list[dict[str, Union[list[tuple[float, float]], str]]]:
        """
        Calculates the ways for navigation inside the room.
        """
        skeleton = polyskel.skeletonize(self.polygon, self.barriers)
        for arc in skeleton:
            point1 = (arc.source.x, arc.source.y)
            for sink in arc.sinks:
                point2 = (sink.x, sink.y)
                if way_is_valid(point1, point2, self.polygon, self.doors, self.barriers):
                    self.ways.append(write_python_way([point1, point2], self.level))

        self._long_ways()
        self._remove_useless_ways()

        if simplify_ways:
            self._simplify_ways()

        self._add_supplementary_ways()

        if door_to_door:
            self._door_to_door()

        return self.ways

    def _long_ways(self):
        """
        A helper method that combines several short ways to fewer long ways.
        """
        self._find_decision_nodes()
        processed_ways = []
        new_ways = []
        i = 0
        while i < len(self.ways):
            new_way = []
            change = False
            while i < len(self.ways):
                if self.ways[i]['way'] in processed_ways:
                    i += 1
                else:
                    new_way += self.ways[i]['way']
                    processed_ways.append(self.ways[i]['way'])
                    change = True
                    i += 1
                    break

            while change:
                change = False
                for way in self.ways:
                    if way['way'] not in processed_ways:

                        if way['way'][0] == new_way[0]:
                            if new_way[0] not in self.decision_nodes:
                                way['way'].reverse()
                                processed_ways.append(way['way'])
                                new_way = way['way'][:-1] + new_way
                                change = True

                        elif way['way'][-1] == new_way[0]:
                            if new_way[0] not in self.decision_nodes:
                                processed_ways.append(way['way'])
                                new_way = way['way'][:-1] + new_way
                                change = True

                        elif way['way'][0] == new_way[-1]:
                            if new_way[-1] not in self.decision_nodes:
                                processed_ways.append(way['way'])
                                new_way += way['way'][1:]
                                change = True

                        elif way['way'][-1] == new_way[-1]:
                            if new_way[-1] not in self.decision_nodes:
                                way['way'].reverse()
                                new_way += way['way'][1:]
                                processed_ways.append(way['way'])
                                change = True

            if new_way:  # equals expression "if new_way != []:"
                new_ways.append(write_python_way(new_way, self.level))

        self.ways = new_ways

    def _find_decision_nodes(self):
        """
        A helper method that parses the current ways and finds all nodes that are connected to different ways.
        """
        self._remove_duplicate_ways()
        self.decision_nodes = []
        self.decision_nodes.extend(self.doors)
        for way in self.ways:
            for node in way['way']:
                if node not in self.decision_nodes:
                    count = 0
                    for way2 in self.ways:
                        for node2 in way2['way']:
                            if node == node2:
                                count += 1
                    if count > 2:
                        self.decision_nodes.append(node)

    def _simplify_ways(self):
        """
        A helper method that deletes all unnecessary parts of the current ways.

        Ways consisting of more than 1 segment are shortened if the result is valid.
        """
        self._remove_duplicate_ways()
        for way in self.ways:
            i = 0
            while i < len(way['way']) - 2:
                if way_inside_room([way['way'][i], way['way'][i + 2]], self.polygon, self.barriers):
                    del way['way'][i + 1]
                else:
                    i += 1
        self._remove_duplicate_ways()

    def _door_to_door(self):
        """
        A helper method that adds all possible direct ways that lead from door to door.
        """
        new_ways = []
        for i in range(len(self.doors) - 1):
            for j in range(i + 1, len(self.doors)):
                if way_inside_room([self.doors[i], self.doors[j]], self.polygon, self.barriers):
                    new_ways.append(write_python_way([self.doors[i], self.doors[j]], self.level))
        self.ways += new_ways
        self._split_intersecting_ways()

    def _split_intersecting_ways(self):
        """
        A helper method that searches all way pairs for intersections.
        If two ways intersect, four separate ways are created.
        """
        self._remove_duplicate_ways()
        i = 0
        change = True
        while change:
            change = False
            while i < len(self.ways) - 1:
                j = i + 1
                while j < len(self.ways):
                    node_index_way1 = 0
                    while node_index_way1 < len(self.ways[i]['way']) - 1:
                        way1_point1 = self.ways[i]['way'][node_index_way1]
                        way1_point2 = self.ways[i]['way'][node_index_way1 + 1]
                        m_way1, b_way1 = get_line(way1_point1, way1_point2)
                        node_index_way2 = 0
                        while node_index_way2 < len(self.ways[j]['way']) - 1:
                            way2_point1 = self.ways[j]['way'][node_index_way2]
                            way2_point2 = self.ways[j]['way'][node_index_way2 + 1]
                            m_way2, b_way2 = get_line(way2_point1, way2_point2)
                            intersection_point = intersection(m_way1, m_way2, b_way1, b_way2)
                            if intersection_point is not None \
                                    and in_interval(way1_point1, way1_point2, intersection_point) \
                                    and in_interval(way2_point1, way2_point2, intersection_point):
                                self.ways.append(write_python_way(
                                        [intersection_point] + self.ways[i]['way'][node_index_way1 + 1:], self.level))
                                self.ways.append(write_python_way(
                                        [intersection_point] + self.ways[j]['way'][node_index_way2 + 1:], self.level))
                                self.ways[i]['way'] = self.ways[i]['way'][:node_index_way1 + 1] + [intersection_point]
                                self.ways[j]['way'] = self.ways[j]['way'][:node_index_way2 + 1] + [intersection_point]
                                way1_point2 = intersection_point
                                m_way1, b_way1 = get_line(way1_point1, way1_point2)
                            node_index_way2 += 1
                        node_index_way1 += 1
                        change = True
                    j += 1
                i += 1

    def _remove_useless_ways(self):
        """
        A helper method that removes ways that aren't connected to doors or other ways.
        """
        self._find_decision_nodes()
        change = True
        while change:
            i = 0
            change = False
            while i < len(self.ways):
                if self.ways[i]['way'][0] not in self.decision_nodes \
                        and self.ways[i]['way'][-1] not in self.decision_nodes:
                    if self.ways[i]['way'][0] not in self.doors and self.ways[i]['way'][-1] not in self.doors:
                        del self.ways[i]
                        change = True
                    else:
                        i += 1
                else:
                    i += 1
                if change:
                    self._long_ways()  # update

    def _remove_duplicate_ways(self):
        """
        A helper method that deletes all ways that exist multiple times or have a length of 0.

        Necessary because otherwise some nodes might be mistaken for decision nodes.
        """
        i = 0
        while i < len(self.ways):
            if len(self.ways[i]['way']) == 2 and self.ways[i]['way'][0] == self.ways[i]['way'][1]:
                del self.ways[i]
            else:
                j = i + 1
                while j < len(self.ways):
                    if self.ways[i] == self.ways[j]:
                        del self.ways[j]
                    else:
                        j += 1
                i += 1

    def _add_supplementary_ways(self):
        """
        A helper method that adds valid ways between current ways.

        Finds connections between the ends of different ways and adds new ways in between.
        New ways that intersect with existing ways are excluded.

        This is a workaround for bad results from straight skeleton generation,
        e.g. some generated ways are not connected to a door or the doors are not connected at all.
        """
        new_ways = []
        excluded = []
        all_relevant_nodes = []
        all_relevant_nodes.extend(self.doors)

        for way in self.ways:
            first_node = way['way'][0]
            last_node = way['way'][-1]
            if (first_node, last_node) not in excluded:
                excluded.append((first_node, last_node))
                excluded.append((last_node, first_node))
                if first_node not in all_relevant_nodes:
                    all_relevant_nodes.append(first_node)
                if last_node not in all_relevant_nodes:
                    all_relevant_nodes.append(last_node)

        for i in range(len(all_relevant_nodes) - 1):
            first_node = all_relevant_nodes[i]
            for j in range(i + 1, len(all_relevant_nodes)):
                last_node = all_relevant_nodes[j]
                if (first_node, last_node) not in excluded:
                    if way_inside_room([first_node, last_node], self.polygon, self.barriers) and \
                            not way_intersects_with_way([first_node, last_node], self.ways):
                        new_ways.append(write_python_way([first_node, last_node], self.level))

        self.ways.extend(new_ways)
        self._split_intersecting_ways()
