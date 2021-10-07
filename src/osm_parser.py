import logging
import sys

from core.parser import Parser


if __name__ == '__main__':
    log = logging.getLogger("__name__")
    if len(sys.argv) < 3:
        log("You need to specify an input and an output file!")

    if sys.argv[1] == sys.argv[2]:
        log("the input file and the output file must not be the same!")
    else:
        parser = Parser(sys.argv[1])
        door_to_door = False
        simplify_ways = False
        remove_deadends = False
        if '-dd' in sys.argv or 'dd' in sys.argv:
            door_to_door = True
        if '-sw' in sys.argv or 'sw' in sys.argv:
            simplify_ways = True
        parser.find_ways(simplify_ways, door_to_door)
        parser.write_osm(sys.argv[2])
