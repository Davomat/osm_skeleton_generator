from osm_helper import *


class Connection:
    def __init__(self, members, type):
        self.members = members
        self.type = type
        self.ways = []

    def find_ways(self, all_doors):
        centres = []
        for connector in self.members:
            centre = centroid(connector['connector'][:-1])  # use the centroid of the connector as representative point --> find better solution!!
            level = connector['level']
            centres.append({'level': level, 'centre': centre})


            if level in all_doors:  # check if there are any doors on the same level
                doors = add_doors_to_polygon(connector['connector'], all_doors[level])
                for door in doors:
                    self.ways.append(write_python_way([centre, door], level,self.type))

        if self.type == 'stairs':
            for i in range(len(centres) - 1):
                self.ways.append(write_python_way([centres[i]['centre'], centres[i + 1]['centre']],centres[i]['level'] + ';' + centres[i + 1]['level'], self.type))
        else:  # elevator
            i = 0
            while i < len(centres) - 1:
                j = i + 1
                while j < len(centres):
                    self.ways.append(write_python_way([centres[i]['centre'], centres[j]['centre']],
                                                      centres[i]['level'] + ';' + centres[j]['level'], self.type))
                    j = j + 1
                i = i + 1
        return self.ways

