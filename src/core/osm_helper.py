from core.geometry import *


def write_python_way(nodes, level, type='footway'):
    way = {'way': nodes, 'level': level}
    way['type'] = type
    return way


def parse_door(element, doors, is_node=True, root=None):
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


def parse_room(element, root):
    polygon = []
    for nd in element.findall("nd")[:-1]:
        node = nd.get('ref')
        node = (root.find("./node[@id='" + node + "']"))
        x = float(node.get('lat'))
        y = float(node.get('lon'))
        polygon.append((x, y))
    level = element.find("tag[@k='level']").get('v')
    return polygon,level


def parse_connection(element,root):
    connections = []
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
        connection = {'connector': polygon}
        connection['level'] = connector.find("tag[@k='level']").get('v')
        connections.append(connection)
        if element.find(
                "tag[@v='stairs']") is not None:
            type = 'stairs'
        else:  # edit if there are more types of connections
            type = 'elevator'
    return connections,type


def parse_multipolygon(element, root):
    polygon = []
    barriers = []
    outer = element.find("member[@role='outer']")
    outer = root.find("./way[@id='" + outer.get('ref') + "']")
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
        return polygon,level,barriers
    else:
        return None,None,None

