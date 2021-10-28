import xml.etree.ElementTree as ET
# TODO: replace with better Library ET doesn't ignore WhiteSpace --> 'xyz' != ' xyz '
from bs4 import BeautifulSoup

from core.connection import *
from core.room import *


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
    """

    def __init__(self, file_name: str):
        self.rooms = []
        self.connections = []
        self.doors = {}
        self.ways = []
        self.nodes = {}
        self.read_data(file_name)

    def read_data(self, file_name: str):
        """
        Parses the given file_name and collects information about important doors, rooms, and connections.
        """
        tree = ET.parse(file_name)
        root = tree.getroot()

        # parse nodes
        for element in root.findall("./node[tag]"):
            if element.find("tag[@k='door']") is not None or element.find("tag[@k='entrance']") is not None:
                parse_door(element, self.doors)

        # parse ways
        for element in root.findall("./way[tag]"):
            if element.find("tag[@k='door']") is not None or element.find("tag[@k='entrance']") is not None:
                parse_door(element, self.doors, False, root)

            elif element.find("tag[@v='room']") is not None or element.find("tag[@v='corridor']") is not None:
                polygon, level = parse_room(element, root)
                self.rooms.append(Room(polygon, level))

        # parse relations
        for element in root.findall("./relation"):
            if element.find("tag[@v='connection']") is not None:  # find connections between different levels
                members, con_type = parse_connection(element, root)
                self.connections.append(Connection(members, con_type))

            elif element.find("tag[@v='multipolygon']") is not None:  # find multipolygons
                polygon, level, barriers = parse_multipolygon(element, root)
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
        Creates a new file_name with the given name in OSM format to save the calculates ways for navigation.
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
            self._beautify(file_name)

    def _beautify(self, file_name: str):
        """
        Takes the generated file_name and inserts newlines as well as indentation.
        """
        # open xml file_name and parse it with BeautifulSoup
        with open(file_name, 'r') as file:
            soup: str = BeautifulSoup(file, "lxml-xml").prettify()

        # re-build all lines with doubled indentation space
        lines = []
        for line in soup.splitlines(keepends=True):
            lines.append(self._preceding_spaces(line) * " " + line)

        # re-open xml file_name and write modified lines
        with open(file_name, 'w') as file:
            file.writelines(lines)

    @staticmethod
    def _preceding_spaces(line: str) -> int:
        """
        Calculate the number of preceding spaces in a string.
        """
        counter = 0
        while counter < len(line) and line[counter] == ' ':
            counter += 1
        return counter
