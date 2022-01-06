import sys
import xml.etree.ElementTree as ET

from core.geometry import almost_same_point, centroid
from core.osm_helper import beautify_xml


def coords(node: ET.Element) -> tuple[float, float]:
    return float(node.get('lat')), float(node.get('lon'))


def rounded(point: tuple[float, float], digits: int = 11) -> tuple[float, float]:
    return round(point[0], digits), round(point[1], digits)


class Merger:
    """
    A class to concentrate information and functionality for level-wise point cluster merging.
    """

    def __init__(self, input_file_name: str):
        self.output_file_name = input_file_name[:-4] + '__merged' + input_file_name[-4:]
        self.root = ET.parse(input_file_name).getroot()
        self._parse()
        self._find_max_id()
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

    def _find_max_id(self):
        """
        A helper method to find the highest absolute value of the node id's.
        """
        self.max_id = 0
        for node in self.nodes:
            node_id = abs(int(node.attrib['id']))
            if node_id > self.max_id:
                self.max_id = node_id
        if int(self.nodes[-1].attrib['id']) < 0:
            self.max_id = -self.max_id

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

            # merge nodes at same position
            # todo

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

    def _get_cluster_points(self, current_point: tuple[float, float], unassigned_points: list[tuple[float, float]],
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
    merger.merge(merge_tolerance)
    merger.write_new_file()
