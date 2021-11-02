import xml.etree.ElementTree as ET  # TODO: replace with better Lib, ET doesn't ignore WhiteSpaces --> 'xyz' != ' xyz '
from typing import Union

from core.connection import Connection
from core.geometry import centroid
from core.osm_helper import beautify_xml
from core.room import Room


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

    def __init__(self, file_name: str):
        self.root = ET.parse(file_name).getroot()
        self.rooms = []
        self.connections = []
        self.doors = {}
        self.ways = []
        self.nodes = {}
        self._read_data()

    def _read_data(self):
        """
        A helper method that parses the given data.
        Collects information about important nodes (doors), ways (rooms), and relations (connections and multipolygons).
        """
        # parse nodes
        for element in self.root.findall("./node[tag]"):
            if element.find("tag[@k='door']") is not None or element.find("tag[@k='entrance']") is not None:
                self._parse_door(element)

        # parse ways
        for element in self.root.findall("./way[tag]"):
            if element.find("tag[@k='door']") is not None or element.find("tag[@k='entrance']") is not None:
                self._parse_door(element, False)

            elif element.find("tag[@v='room']") is not None or element.find("tag[@v='corridor']") is not None:
                polygon, level = self._parse_room(element)
                self.rooms.append(Room(polygon, level))

        # parse relations
        for element in self.root.findall("./relation"):
            if element.find("tag[@v='connection']") is not None:  # find connections between different levels
                members, con_type = self._parse_connection(element)
                self.connections.append(Connection(members, con_type))

            elif element.find("tag[@v='multipolygon']") is not None:  # find multipolygons
                polygon, level, barriers = self._parse_multipolygon(element)
                if polygon is not None:
                    self.rooms.append(Room(polygon, level, barriers))

        # remove duplicate rooms (--> multipolygon)
        for room in self.rooms:
            for room2 in self.rooms:
                if room.level == room2.level and room.polygon == room2.polygon and room != room2:
                    if not room.barriers:
                        self.rooms.remove(room)
                    else:
                        self.rooms.remove(room2)

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
                node_ref = nd.get('ref')
                node = self.root.find("./node[@id='" + node_ref + "']")  # find referenced node
                coordinates.append((float(node.get('lat')), float(node.get('lon'))))
            door = centroid(coordinates)
        self.doors[level].append(door)

    def _parse_room(self, element: ET.Element) -> tuple[list[tuple[float, float]], str]:
        """
        A helper method that converts a room element (way) into its corresponding polygon (list of points).
        """
        polygon = []
        for nd in element.findall("nd")[:-1]:
            node_ref = nd.get('ref')
            node = (self.root.find("./node[@id='" + node_ref + "']"))
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
            connector_ref = member.get('ref')
            connector = self.root.find("./way[@id='" + connector_ref + "']")
            for nd in connector.findall("nd"):
                node_ref = nd.get('ref')
                node = self.root.find("./node[@id='" + node_ref + "']")
                x = float(node.get('lat'))
                y = float(node.get('lon'))
                polygon.append((x, y))
            connection = {'connector': polygon, 'level': connector.find("tag[@k='level']").get('v')}
            connections.append(connection)
            if element.find(
                    "tag[@v='stairs']") is not None:
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

        if element.find("tag[@k='level']") is not None:
            level = element.find("tag[@k='level']").get('v')
        elif outer.find("tag[@k='level']") is not None:
            level = outer.find("tag[@k='level']").get('v')
        else:
            raise ValueError('No level tag found in Multipolygon {} with Attributes {}'.format(element, element.attrib))

        if element.find("tag[@k='indoor']") is not None:
            building_element = element.find("tag[@k='indoor']").get('v')
        elif outer.find("tag[@k='indoor']") is not None:
            building_element = outer.find("tag[@k='indoor']").get('v')
        else:
            raise ValueError(
                'No indoor tag found in Multipolygon {} with Attributes {}'.format(element, element.attrib))

        if building_element == 'room' or building_element == 'corridor':
            for member in element.findall("member[@role='inner']"):
                barrier = []
                inner_ref = member.get('ref')
                inner = self.root.find("./way[@id='" + inner_ref + "']")
                for nd in inner.findall("nd")[:-1]:
                    node_ref = nd.get('ref')
                    node = self.root.find("./node[@id='" + node_ref + "']")
                    x = float(node.get('lat'))
                    y = float(node.get('lon'))
                    barrier.append((x, y))
                barriers.append(barrier)

            for nd in outer.findall("nd")[:-1]:
                node_ref = nd.get('ref')
                node = self.root.find("./node[@id='" + node_ref + "']")
                x = float(node.get('lat'))
                y = float(node.get('lon'))
                polygon.append((x, y))
            return polygon, level, barriers
        else:
            return None, None, None

    def find_ways(self, simplify_ways: bool, door_to_door: bool):
        """
        Calculates the ways for later navigation.
        """
        for room in self.rooms:
            room.add_doors(self.doors)
            self.ways += room.find_ways(simplify_ways, door_to_door)

        for connection in self.connections:
            self.ways += connection.find_ways(self.doors)

    def write_osm(self, file_name: str, beautify: bool):
        """
        Creates a new file with the given name in OSM format to save the calculates ways for navigation.
        """
        osm_root = ET.Element("osm", version='0.6', upload='false')
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
                for node in way['way']:
                    if node not in processed[level]:
                        if node not in self.nodes[level]:
                            self.nodes[level][node] = osm_node_id
                            osm_node_id -= 1
                        ET.SubElement(osm_root, "node", id=str(self.nodes[level][node]), lat=str(node[0]),
                                      lon=str(node[1]))
                        processed[level].append(node)
                    ET.SubElement(osm_way, "nd", ref=str(self.nodes[way['level']][node]))

            ET.SubElement(osm_way, "tag", k="indoor", v="yes")
            ET.SubElement(osm_way, "tag", k="level", v=way['level'])
            ET.SubElement(osm_way, "tag", k="highway", v=way['type'])
            osm_ways.append(osm_way)

        for osm_way in osm_ways:
            osm_root.append(osm_way)

        tree = ET.ElementTree(osm_root)
        tree.write(file_name, encoding='utf-8', xml_declaration=True)

        if beautify:
            beautify_xml(file_name)
