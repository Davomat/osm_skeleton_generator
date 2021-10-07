import sys

from core.parser import Parser

if __name__ == '__main__':
    if len(sys.argv) < 3:
        raise AttributeError("You need to specify an input and an output file!")
    if sys.argv[1] == sys.argv[2]:
        raise AttributeError("The input file and the output file must not be the same!")

    parser = Parser(sys.argv[1])
    door_to_door = '-dd' in sys.argv or 'dd' in sys.argv
    simplify_ways = '-sw' in sys.argv or 'sw' in sys.argv
    remove_deadends = False
    parser.find_ways(simplify_ways, door_to_door)
    parser.write_osm(sys.argv[2])
