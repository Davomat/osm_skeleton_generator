import math
import sys
import xml.etree.ElementTree as ET

# Take almost_same_point from core.osm_classes.Point and not from geometry.py

from core.geometry import centroid
from core.osm_helper import beautify_xml


def coords(node: ET.Element) -> tuple[float, float]:
    """ Extracts the latitude and longitude information of a node element. """
    return float(node.get('lat')), float(node.get('lon'))


def rounded(point: tuple[float, float], digits: int = 11) -> tuple[float, float]:
    """ Rounds two floats to n digits in a tuple. """
    return round(point[0], digits), round(point[1], digits)


def angle(slope: tuple[float, float]) -> float:
    """ Calculates the absolute angle of a way segment given as a tuple (dx, dy). """
    dx = slope[0]
    dy = slope[1]
    div = math.sqrt(dx ** 2 + dy ** 2)
    if div > 0:
        dx /= div
        dy /= div
    return math.copysign(math.acos(dx) * 180 / math.pi, dy) % 360


def almost_same_angle(alpha: float, beta: float, tolerance: float) -> bool:
    """ Checks if two mathematical angles are almost equal. """
    diff1 = alpha - beta
    diff2 = (alpha + 180.) % 360 - (beta + 180.) % 360  # for angles around 0 and 360
    return abs(diff1) <= tolerance or abs(diff2) <= tolerance


class Merger:
    """
    A class to concentrate information and functionality for level-wise point cluster merging.
    """

    def __init__(self, input_file_name: str):
        self.output_file_name = input_file_name[:-4] + '__merged' + input_file_name[-4:]
        self.root = ET.parse(input_file_name).getroot()
        self._parse()
        self.level_elements: dict[str, dict[str, list[ET.Element]]] = {}
        self._fill_level_elements(self.nodes, 'nodes')
        self._fill_level_elements(self.ways, 'ways')

    def _parse(self):
        """
        A helper method that parses the given data and collects all relevant elements.
        """
        self.bounds = self.root.findall('bounds')
        self.nodes = self.root.findall('node')
        self.ways = self.root.findall('way')
        self.relations = self.root.findall('relation')

    def _fill_level_elements(self, elements: list[ET.Element], name: str):
        """
        Collects all parsed elements with a level tag.
        """
        for elem in elements:
            level_tag = elem.find("tag[@k='level']")
            if level_tag is not None:
                level = level_tag.get('v')
                if level not in self.level_elements:
                    self.level_elements[level] = {name: [elem]}
                elif name not in self.level_elements[level]:
                    self.level_elements[level][name] = [elem]
                else:
                    self.level_elements[level][name].append(elem)

    def remove_unnecessary_nodes(self, tolerance=2.0):
        """
        Finds and deletes nodes within a straight line.
        """
        for way in self.ways:
            # collect information
            node_refs = way.findall('nd')
            nodes = [self.root.find("./node[@id='" + node_ref.get('ref') + "']") for node_ref in node_refs]
            node_coords = [coords(node) for node in nodes]
            # check for double points
            for i in range(len(nodes) - 1, 0, -1):
                if node_coords[i-1] == node_coords[i]:
                    way.remove(node_refs[i])
                    node_refs.pop(i)
                    nodes.pop(i)
                    node_coords.pop(i)
            # check for straight lines
            slopes = [(node_coords[i+1][0] - node_coords[i][0], node_coords[i+1][1] - node_coords[i][1])
                      for i in range(len(node_coords) - 1)]
            slope_angles = [angle(slope) for slope in slopes]
            # remove middle point of two adjacent edges if their slope angle is almost equal
            for j in range(len(slope_angles)-1, 0, -1):
                if almost_same_angle(slope_angles[j-1], slope_angles[j], tolerance):
                    way.remove(node_refs[j])

        # also delete points with no use
        self._delete_solitaires()

    def _node_has_ref(self, node: ET.Element) -> bool:
        """
        Checks whether a node has a reference in any way element.
        """
        for way in self.ways:
            if node in way.findall('nd'):
                return True
        return False

    def _delete_solitaires(self):
        """
        Deletes all nodes without information and reference.
        """
        # collect all nodes with tags or reference
        important_nodes = [node for node in self.nodes if node.find("tag") is not None]
        for way in self.ways:
            for node_ref in way.findall('nd'):
                node = self.root.find("./node[@id='" + node_ref.get('ref') + "']")
                if node not in important_nodes:
                    important_nodes.append(node)
        # delete all other nodes
        for node in self.nodes:
            if node not in important_nodes:
                self.nodes.remove(node)

    def merge(self, tolerance: float):
        """
        Finds point clusters in every level and merges them into a single point.
        """
        for level in self.level_elements:
            # find all points that belong to the level
            level_nodes = self._find_all_level_points(level)
            level_points = [coords(node) for node in level_nodes]

            # find the clusters with their points
            clusters = self._find_clusters(level_points, tolerance)

            # get the centroids of the corresponding cluster; the centroid of clusters[k] is centroids[k]
            centroids: list[tuple[float, float]] = [rounded(centroid(cluster)) for cluster in clusters]

            # check clusters for important points and set them as cluster center
            important_level_points = [coords(node) for node in level_nodes
                                      if node.find("tag[@k='level']") is not None]
            for cluster_idx in range(len(clusters)):
                for point in clusters[cluster_idx]:
                    if point in important_level_points:
                        centroids[cluster_idx] = point
                        break

            # overwrite cluster points in ways
            for way in self.level_elements[level]['ways']:
                for node_ref in way.findall('nd'):
                    node = self.root.find("./node[@id='" + node_ref.get('ref') + "']")
                    for cluster_idx in range(len(clusters)):
                        if coords(node) in clusters[cluster_idx]:
                            node.attrib['lat'] = str(centroids[cluster_idx][0])
                            node.attrib['lon'] = str(centroids[cluster_idx][1])
                            break

            # merge nodes at same position by deleting nodes and re-reference way points
            for node_idx in range(len(self.nodes)-1, 0, -1):
                # leave out important nodes like doors
                if self.nodes[node_idx].find("tag[@k='level']") is not None:
                    continue
                # don't look at point that were not in a cluster
                if coords(self.nodes[node_idx]) not in centroids:
                    continue
                # delete node and ref if its on an important position (like under a door) and therefore useless
                # !!! this causes problems if a door is on an edge (e.g. below stairs)
                # if coords(self.nodes[node_idx]) in important_level_points:
                    # self._del_ref(self.nodes[node_idx].get('id'))
                    # del self.nodes[node_idx]
                    # continue
                # otherwise search for other points with same position and re-reference the id
                for other_idx in range(node_idx):
                    if coords(self.nodes[node_idx]) == coords(self.nodes[other_idx]):
                        self._re_ref(self.nodes[node_idx].get('id'), self.nodes[other_idx].get('id'))
                        del self.nodes[node_idx]
                        break

    def _find_all_level_points(self, level: str) -> list[ET.Element]:
        """
        Collects the points that belong to the elements of the given level.
        """
        points = []
        for node in self.level_elements[level]['nodes']:
            points.append(node)
        for way in self.level_elements[level]['ways']:
            for node_ref in way.findall("nd")[:-1]:
                node = self.root.find("./node[@id='" + node_ref.get('ref') + "']")  # find referenced node
                if node not in points:
                    points.append(node)
        return points

    def _find_clusters(self, level_points: list[tuple[float, float]], tolerance: float) \
            -> list[list[tuple[float, float]]]:
        """
        A helper method that finds all point clusters from a list of points.
        """
        clusters: list[list[tuple[float, float]]] = []  # a list of point lists
        while level_points:
            current_point = level_points.pop(0)
            # check if point has close points
            cluster = self._get_cluster_points(current_point, level_points, tolerance)
            # if yes, add to a new clusters entry and check close points for the same cluster entry
            if cluster:
                cluster.append(current_point)
                clusters.append(cluster)
        return clusters

    def _get_cluster_points(self, current_point: Point, unassigned_points: list[Point],
                            tolerance: float) -> list:
        """
        A helper method that finds a point cluster from a single given point recursively.
        """
        # init new cluster for current point
        cluster = []
        # check all points that belong to no cluster yet
        i = 0
        while i < len(unassigned_points):
            # add point to current cluster and remove them from list of searchable points
            if almost_same_point(current_point, unassigned_points[i], tolerance):
                cluster.append(unassigned_points.pop(i))
                i -= 1
            i += 1
        # repeat recursively with new found points and add result to current cluster
        for point in cluster:
            cluster.extend(self._get_cluster_points(point, unassigned_points, tolerance))
        # return found cluster with sub-clusters
        return cluster

    def _del_ref(self, node_id: str):
        """
        A helper method to delete the referenced node out of self.ways.
        """
        for way in self.ways:
            for node_ref in way.findall('nd'):
                if node_ref.get('ref') == node_id:
                    way.remove(node_ref)

    def _re_ref(self, orig_id: str, new_id: str):
        """
        A helper method to change the referenced node ids in self.ways.
        """
        for way in self.ways:
            for node_ref in way.findall('nd'):
                if node_ref.get('ref') == orig_id:
                    node_ref.set('ref', new_id)

    def write_new_file(self):
        """
        Creates a new file with the merged points in OSM format.
        """
        # create a root Element for the data
        osm_root = ET.Element("osm", version='0.6', upload='false')

        # add bounds, nodes, ways and relations
        for bound in self.bounds:
            osm_root.append(bound)
        for node in self.nodes:
            osm_root.append(node)
        for way in self.ways:
            osm_root.append(way)
        for relation in self.relations:
            osm_root.append(relation)

        # finalize tree
        tree = ET.ElementTree(osm_root)
        tree.write(self.output_file_name, encoding='utf-8', xml_declaration=True)

        # polish up xml file
        beautify_xml(self.output_file_name)


if __name__ == '__main__':
    # check for correct input
    if len(sys.argv) < 2:
        raise AttributeError("You need to specify an input file!")

    merge_tolerance = 0.1

    merger = Merger(sys.argv[1])
    merger.remove_unnecessary_nodes()
    merger.merge(merge_tolerance)
    merger.write_new_file()
