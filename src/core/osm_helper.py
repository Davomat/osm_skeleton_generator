from typing import Union

from bs4 import BeautifulSoup


def write_python_way(nodes: list[tuple[float, float]], level: str, way_type='footway') \
        -> dict[str, Union[list[tuple[float, float]], str]]:
    """
    Builds a project-standardized dict to work with.
    """
    return {'way': nodes, 'level': level, 'type': way_type}


def beautify_xml(file_name: str):
    """
    Takes the generated file_name and inserts newlines as well as indentation.
    """
    # open xml file_name and parse it with BeautifulSoup
    with open(file_name, 'r') as file:
        soup: str = BeautifulSoup(file, "lxml-xml").prettify()

    # re-build all lines with doubled indentation space
    lines = []
    for line in soup.splitlines(keepends=True):
        counter = 0
        while counter < len(line) and line[counter] == ' ':
            counter += 1
        lines.append(counter * " " + line)

    # re-open xml file_name and write modified lines
    with open(file_name, 'w') as file:
        file.writelines(lines)
