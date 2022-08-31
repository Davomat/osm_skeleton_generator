import xml.etree.ElementTree as ET  # TODO: replace with better Lib, ET doesn't ignore WhiteSpaces --> 'xyz' != ' xyz '
from typing import Union

from core.connection import Connection
from core.geometry import centroid, simplify_polygon
from core.osm_helper import beautify_xml
from core.room import Room
from core.osm_classes import *



class Parser:
    """
    A superordinate class that parses osm data, assigns subtasks, and save calculation results.

    Args
    ----
    file_name : str
        Defines the name (with absolute or relative path) of the osm file_name that shall be parsed.

    Attributes
    ----------
    rooms : list[Room]
        All rooms the can be found in the given osm file_name.
    potential_barriers : list[tuple[list[tuple[float, float]], str]]
        All walls, bookshelves and other obstacles that should be avoided.
    connections : list[Connection]
        The representations of all doors as points.
    doors : dict[str, list[tuple[float, float]]]
        The collection of all doors as points per level
    ways : list[dict[str, Union[list[tuple[float, float]], str]]]
        The calculated ways with their type and level information.
    nodes : dict[str, dict[tuple[float, float], int]]
        POIs with their level and id information for the osm file_name.

    Methods
    -------
    find_ways(simplify_ways: bool, door_to_door: bool)
        Calculates the ways for later navigation.
    def write_osm(file_name: str, beautify: bool)
        Creates a new file with the given name in OSM format to save the calculates ways for navigation.
    """

    tags: dict[str, list[str]] = {
        'barriers': ["tag[@v='wall']", "tag[@v='bench']", "tag[@v='table']"],
        'doors': ["tag[@k='door']", "tag[@k='entrance']"],
        'rooms': ["tag[@v='room']", "tag[@v='corridor']"],
        'connections': ["tag[@v='connection']"],
        'multipolygons': ["tag[@v='multipolygon']"]
    }

    def __init__(self, file_name: str):
        self.root: ET.Element = ET.parse(file_name).getroot()
        self.rooms: list[Room] = []
        self.connections: list[Connection] = []
        self.doors: dict[str, list[tuple[float, float]]] = {}
        self.potential_barriers: list[tuple[list[tuple[float, float]], str]] = []
        self.ways: list[dict[str, Union[list[tuple[float, float]], str]]] = []
        self.nodes: dict[str, dict[tuple[float, float], int]] = {}
        self._read_data()

    def _read_data(self):
        """
        A helper method that parses the given data.
        Collects information about important nodes (doors), ways (rooms), and relations (connections and multipolygons).
        """
        # parse nodes to find doors
        for element in self.root.findall("./node[tag]"):
            for tag in Parser.tags['doors']:
                if element.find(tag) is not None:
                    self._parse_door(element, is_node=True)
                    break

        # parse ways to find doors
        for element in self.root.findall("./way[tag]"):
            for tag in Parser.tags['doors']:
                if element.find(tag) is not None:
                    self._parse_door(element, is_node=False)
                    break

        # parse ways to find potential inner_barriers
        for element in self.root.findall("./way[tag]"):
            for tag in Parser.tags['barriers']:
                if element.find(tag) is not None:
                    self.potential_barriers.append(self._parse_polygon(element))
                    break

        for polygon in self.potential_barriers:
            simplify_polygon(polygon[0])

        # parse ways to find rooms
        for element in self.root.findall("./way[tag]"):
            for tag in Parser.tags['rooms']:
                if element.find(tag) is not None:
                    polygon, level = self._parse_polygon(element)
                    self.rooms.append(Room(polygon, level, self.potential_barriers))
                    break

        # parse relations to find multipolygons
        for element in self.root.findall("./relation"):
            for tag in Parser.tags['multipolygons']:
                if element.find(tag) is not None:
                    polygon, level, barriers = self._parse_multipolygon(element)
                    if polygon is not None:
                        self.rooms.append(Room(polygon, level, self.potential_barriers, inner_barriers=barriers))
                    break

        self._remove_duplicated_rooms()

        # parse relations to find connections between different levels
        for element in self.root.findall("./relation"):
            for tag in Parser.tags['connections']:
                if element.find(tag) is not None:
                    members, con_type = self._parse_connection(element)
                    self.connections.append(Connection(members, con_type))
                    break

    def _parse_door(self, element: ET.Element, is_node=True):
        """
        A helper method that adds a door element (a node or the centroid of a closed way) to the list of doors.
        This list is sorted by level.
        """
        level = element.find("tag[@k='level']").get('v')
        if level not in self.doors:
            self.doors[level] = []

        if is_node:
            door = (float(element.get('lat')), float(element.get('lon')))
        else:
            coordinates = []
            for nd in element.findall("nd")[:-1]:
                node = self.root.find("./node[@id='" + nd.get('ref') + "']")  # find referenced node
                coordinates.append((float(node.get('lat')), float(node.get('lon'))))
            door = centroid(coordinates)
        self.doors[level].append(door)

    def _parse_polygon(self, element: ET.Element) -> tuple[list[tuple[float, float]], str]:
        """
        A helper method that converts a room element (way) into its corresponding polygon (list of points).
        """
        polygon = []
        for nd in element.findall("nd")[:-1]:
            node = (self.root.find("./node[@id='" + nd.get('ref') + "']"))
            x = float(node.get('lat'))
            y = float(node.get('lon'))
            polygon.append((x, y))
        level = element.find("tag[@k='level']").get('v')
        return polygon, level

    def _parse_connection(self, element: ET.Element) \
            -> tuple[list[dict[str, Union[list[tuple[float, float]], str]]], str]:
        """
        A helper method that converts a connection element (relation) into a list of the corresponding polygons.
        """
        connections = []
        con_type = 'other'
        for member in element.findall("member"):
            polygon = []
            connector = self.root.find("./way[@id='" + member.get('ref') + "']")
            for nd in connector.findall("nd"):
                node = self.root.find("./node[@id='" + nd.get('ref') + "']")
                x = float(node.get('lat'))
                y = float(node.get('lon'))
                polygon.append((x, y))
            connection = {'connector': polygon, 'level': connector.find("tag[@k='level']").get('v')}
            connections.append(connection)
            if element.find("tag[@v='stairs']") is not None:
                con_type = 'stairs'
            else:  # edit if there are more types of connections
                con_type = 'elevator'
        return connections, con_type

    def _parse_multipolygon(self, element: ET.Element) \
            -> Union[tuple[list[tuple[float, float]], str, list[list[tuple[float, float]]]],
                     tuple[None, None, None]]:
        """
        A helper method that converts a multipolygon element (relation) into its corresponding outer polygon and inner
        barriers (also polygons).
        """
        polygon = []
        barriers = []

        # element is a Element 'relation' with attributes like {'id': '-57497', 'action': 'modify'}
        outer_ref = element.find("member[@role='outer']")
        # outer_ref is a Element 'member' with attributes like {'type': 'way', 'ref': '-56945', 'role': 'outer'}
        outer = self.root.find("./way[@id='" + outer_ref.get('ref') + "']")
        # outer is a Element 'way' with attributes like {'id': '-56945', 'action': 'modify'}

        # find the level and the indoor tag in either the multipolygon or the outer ways
        if element.find("tag[@k='level']") is not None:
            level = element.find("tag[@k='level']").get('v')
        elif outer.find("tag[@k='level']") is not None:
            level = outer.find("tag[@k='level']").get('v')
        else:
            raise ValueError(f"No level tag found in Multipolygon {element} with Attributes {element.attrib}")
        if element.find("tag[@k='indoor']") is not None:
            building_element = element.find("tag[@k='indoor']").get('v')
        elif outer.find("tag[@k='indoor']") is not None:
            building_element = outer.find("tag[@k='indoor']").get('v')
        else:
            raise ValueError(f"No indoor tag found in Multipolygon {element} with Attributes {element.attrib}")

        # parse the multipolygon
        if building_element == 'room' or building_element == 'corridor':
            for member in element.findall("member[@role='inner']"):
                barrier = []
                inner = self.root.find("./way[@id='" + member.get('ref') + "']")
                for nd in inner.findall("nd")[:-1]:
                    node = self.root.find("./node[@id='" + nd.get('ref') + "']")
                    x = float(node.get('lat'))
                    y = float(node.get('lon'))
                    barrier.append((x, y))
                barriers.append(barrier)

            for nd in outer.findall("nd")[:-1]:
                node = self.root.find("./node[@id='" + nd.get('ref') + "']")
                x = float(node.get('lat'))
                y = float(node.get('lon'))
                polygon.append((x, y))
            return polygon, level, barriers
        else:
            return None, None, None

    def _remove_duplicated_rooms(self):
        """
        A helper method that removes duplicate rooms due to parsing for rooms and multipolygons which can be rooms too.
        It is assumed that multipolygon-rooms are more precise and parsed after way-rooms.
        """
        n1 = len(self.rooms) - 2
        while n1 >= 0:
            room1 = self.rooms[n1]

            n2 = len(self.rooms) - 1
            while n2 > n1:
                room2 = self.rooms[n2]

                if room1 != room2 and room1.level == room2.level and room1.polygon == room2.polygon:
                    self.rooms.remove(room1)
                    break
                n2 -= 1
            n1 -= 1

    def find_ways(self, simplify_ways_much: bool, door_to_door: bool):
        """
        Calculates the ways for later navigation.
        """
        i = 0
        for room in self.rooms:
            i += 1
            print("room #", i, '/', len(self.rooms), end=' ', flush=True)
            room.add_doors(self.doors)
            self.ways += room.find_ways(simplify_ways_much, door_to_door)
            print("completed.")

        for connection in self.connections:
            self.ways += connection.find_ways(self.doors)

    def write_osm(self, file_name: str, beautify: bool):
        """
        Creates a new file with the given name in OSM format to save the calculates ways for navigation.
        """
        # create a root Element for the data
        osm_root = ET.Element("osm", version='0.6', upload='false')

        # add bounds information if given in the original file
        bounds_element = self.root.find("bounds")
        if bounds_element is not None:
            osm_root.append(bounds_element)

        # add points and cache ways
        processed = {}
        osm_node_id = -2
        osm_way_id = -2
        osm_ways = []
        for way in self.ways:
            osm_way = ET.Element("way", id=str(osm_way_id))
            osm_way_id -= 1
            level = way['level']
            if ';' in level:  # way connecting two levels --> only two nodes
                levels = level.split(';')
                if levels[0] not in self.nodes:
                    self.nodes[levels[0]] = {}
                    processed[levels[0]] = []
                if levels[1] not in self.nodes:
                    self.nodes[levels[1]] = {}
                    processed[levels[1]] = []

                if way['way'][0] not in self.nodes[levels[0]]:
                    self.nodes[levels[0]][way['way'][0]] = osm_node_id
                    osm_node_id -= 1
                    ET.SubElement(osm_root, "node", id=str(self.nodes[levels[0]][way['way'][0]]),
                                  lat=str(way['way'][0][0]),
                                  lon=str(way['way'][0][1]))
                    processed[levels[0]].append(way['way'][0])

                if way['way'][1] not in self.nodes[levels[1]]:
                    self.nodes[levels[1]][way['way'][1]] = osm_node_id
                    osm_node_id -= 1
                    ET.SubElement(osm_root, "node", id=str(self.nodes[levels[1]][way['way'][1]]),
                                  lat=str(way['way'][1][0]),
                                  lon=str(way['way'][1][1]))
                    processed[levels[1]].append(way['way'][1])

                ET.SubElement(osm_way, "nd", ref=str(self.nodes[levels[0]][way['way'][0]]))
                ET.SubElement(osm_way, "nd", ref=str(self.nodes[levels[1]][way['way'][1]]))

            else:
                if level not in self.nodes:
                    self.nodes[level] = {}
                    processed[level] = []
                print("self.nodes=" + str(self.nodes))
                for node in way['way']:
                    if node not in processed[level]:
                        if node not in self.nodes[level]:
                            self.nodes[level][node] = osm_node_id
                            osm_node_id -= 1
                        print("node:" + str(node))
                        #node = tupel_to_point(node)
                        ET.SubElement(osm_root, "node", id=str(self.nodes[level][node]), lat=str(tupel_to_point(node).x),
                                      lon=str(tupel_to_point(node).y))
                        processed[level].append(node)
                    ET.SubElement(osm_way, "nd", ref=str(self.nodes[way['level']][node]))

            ET.SubElement(osm_way, "tag", k="indoor", v="yes")
            ET.SubElement(osm_way, "tag", k="level", v=way['level'])
            ET.SubElement(osm_way, "tag", k="highway", v=way['type'])
            osm_ways.append(osm_way)

        # add ways after points
        for osm_way in osm_ways:
            osm_root.append(osm_way)

        # finalize tree
        tree = ET.ElementTree(osm_root)
        tree.write(file_name, encoding='utf-8', xml_declaration=True)

        # polish up xml file if flag is set
        if beautify:
            beautify_xml(file_name)
