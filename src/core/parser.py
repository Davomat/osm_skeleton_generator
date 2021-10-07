import xml.etree.ElementTree as ET # TODO: replace with better Library ET doesn't ignore WhiteSpace --> 'xyz' != ' xyz '

from core.connection import *
from core.room import *


class Parser:
    def __init__(self, file):
        self.rooms = []
        self.connections = []
        self.doors = {}
        self.ways = []
        self.nodes = {}
        self.read_data(file)

    def read_data(self, file):
        tree = ET.parse(file)
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
                polygon,level = parse_room(element, root)
                room = Room(polygon, level)
                self.rooms.append(room)

        # parse relations
        for element in root.findall("./relation"):
            if element.find("tag[@v='connection']") is not None:  # find connections between different levels
                members,type = parse_connection(element,root)
                connection = Connection(members, type)
                self.connections.append(connection)

            elif element.find("tag[@v='multipolygon']") is not None:  # Multipolygone finden
                polygon,level,barriers = parse_multipolygon(element,root)
                if polygon is not None:
                    room = Room(polygon, level, barriers)
                    self.rooms.append(room)


        # remove duplicate rooms(---> Multipolygon)
        for room in self.rooms:
            for room2 in self.rooms:
                if room.level == room2.level and room.polygon == room2.polygon and room != room2:
                    if not room.barriers:
                        self.rooms.remove(room)
                    else:
                        self.rooms.remove(room2)

    def find_ways(self, simplify_ways, door_to_door):
        for room in self.rooms:
            room.add_doors(self.doors)
            self.ways += room.find_ways(simplify_ways, door_to_door)

        for connection in self.connections:
            self.ways += connection.find_ways(self.doors)

    # save genereated ways in OSM format
    def write_osm(self, file):
        osm_root = ET.Element("osm", version='0.6', upload='false')
        processed = {}
        osm_node_id = -2
        osm_way_id = -2
        osm_ways = []
        for way in self.ways:
            osm_way = ET.Element("way", id=str(osm_way_id))
            osm_way_id -= 1
            level = way['level']
            if ';' in level: #way connecting two levels --> only two nodes
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
        tree.write(file, encoding='utf-8', xml_declaration=True)
