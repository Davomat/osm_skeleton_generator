import sys
import xml.etree.ElementTree as ET

from core.geometry import almost_same_point, centroid
from core.osm_helper import beautify_xml


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
        # get all relevant elements
        self.bounds = self.root.find('bounds')
        self.nodes = self.root.findall('node')
        self.ways = self.root.findall('way')
        self.relations = self.root.findall('relation')

    def _fill_level_elements(self, elements: list[ET.Element], name: str):
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
        for level in self.level_elements:
            # find all points at the level
            level_nodes = self._find_all_level_points(level)
            level_points = [(float(node.get('lat')), float(node.get('lon'))) for node in level_nodes]

            # find the clusters with their points
            clusters = self._find_clusters(level_points, tolerance)

            # get the centroids of the corresponding cluster; the centroid of clusters[k] is centroids[k]
            centroids: list[tuple[float, float]] = [centroid(cluster) for cluster in clusters]

            # overwrite cluster points in ways

            # delete zero-length way parts

            # delete zero-length ways

    def _find_all_level_points(self, level: str) -> list[ET.Element]:
        points = []
        for node in self.level_elements[level]['nodes']:
            points.append(node)
        for way in self.level_elements[level]['ways']:
            for node_ref in way.findall("nd")[:-1]:
                node = self.root.find("./node[@id='" + node_ref.get('ref') + "']")  # find referenced node
                if node not in points:
                    points.append(node)
        return points

    def _find_clusters(self, level_points: list[tuple[float, float]], tolerance: float) -> list[list]:
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
        # create a root Element for the data
        osm_root = ET.Element("osm", version='0.6', upload='false')

        # add bounds information if given in the original file
        if self.bounds is not None:
            osm_root.append(self.bounds)

        # add nodes, ways and relations
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
    # merger.write_new_file()
