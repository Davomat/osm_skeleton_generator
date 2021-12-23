import sys
import xml.etree.ElementTree as ET

from core.osm_helper import beautify_xml


class Merger:
    """
    A class to concentrate information and functionality for level-wise point cluster merging.
    """

    tolerance = 0.1

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

    def merge(self):
        for level in self.level_elements:
            continue

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

    merger = Merger(sys.argv[1])
    merger.merge()
    merger.write_new_file()
