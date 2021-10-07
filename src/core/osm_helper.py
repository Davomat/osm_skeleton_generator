from xml.etree.ElementTree import Element

from core.geometry import *


def write_python_way(nodes: list[tuple[float, float]], level: str, way_type='footway') \
        -> dict[str, Union[list[tuple[float, float]], str]]:
    """
    Builds a project-standardized dict to work with.
    """
    return {'way': nodes, 'level': level, 'type': way_type}


def parse_door(element: Element, doors: dict[str, list[tuple[float, float]]], is_node=True, root: Element = None):
    """
    Takes a door element (node or way) and adds it (or its centroid) to the given sorted-by-level list of doors nodes.
    """
    level = element.find("tag[@k='level']").get('v')
    if level not in doors:
        doors[level] = []

    if is_node:
        door = (float(element.get('lat')), float(element.get('lon')))
    else:
        coords = []
        for nd in element.findall("nd")[:-1]:
            node = nd.get('ref')
            node = (root.find("./node[@id='" + node + "']"))  # find referenced node
            coords.append((float(node.get('lat')), float(node.get('lon'))))
        door = centroid(coords)
    doors[level].append(door)


def parse_room(element: Element, root: Element) -> tuple[list[tuple[float, float]], str]:
    """
    Converts a room element (way) into its corresponding polygon (list of points).
    """
    polygon = []
    for nd in element.findall("nd")[:-1]:
        node = nd.get('ref')
        node = (root.find("./node[@id='" + node + "']"))
        x = float(node.get('lat'))
        y = float(node.get('lon'))
        polygon.append((x, y))
    level = element.find("tag[@k='level']").get('v')
    return polygon, level


def parse_connection(element: Element, root: Element) \
        -> tuple[list[dict[str, Union[list[tuple[float, float]], str]]], str]:
    """
    Converts a connection element (relation) into a list of the corresponding polygons.
    """
    connections = []
    con_type = 'other'
    for member in element.findall("member"):
        polygon = []
        connector = member.get('ref')
        connector = root.find("./way[@id='" + connector + "']")
        for nd in connector.findall("nd"):
            node = nd.get('ref')
            node = root.find("./node[@id='" + node + "']")
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


def parse_multipolygon(element: Element, root: Element) \
        -> Union[tuple[list[tuple[float, float]], str, list[list[tuple[float, float]]]],
                 tuple[None, None, None]]:
    """
    Converts a multipolygon element (relation) into its corresponding outer polygon and inner barriers.
    """
    polygon = []
    barriers = []
    outer_ref = element.find("member[@role='outer']")
    outer = root.find("./way[@id='" + outer_ref.get('ref') + "']")
    level = outer.find("tag[@k='level']").get('v')
    building_element = outer.find("tag[@k='indoor']").get('v')
    if building_element == 'room' or building_element == 'corridor':
        for member in element.findall("member[@role='inner']"):
            barrier = []
            inner = member.get('ref')
            inner = root.find("./way[@id='" + inner + "']")
            for nd in inner.findall("nd")[:-1]:
                node = nd.get('ref')
                node = root.find("./node[@id='" + node + "']")
                x = float(node.get('lat'))
                y = float(node.get('lon'))
                barrier.append((x, y))
            barriers.append(barrier)

        for nd in outer.findall("nd")[:-1]:
            node = nd.get('ref')
            node = root.find("./node[@id='" + node + "']")
            x = float(node.get('lat'))
            y = float(node.get('lon'))
            polygon.append((x, y))
        return polygon, level, barriers
    else:
        return None, None, None
