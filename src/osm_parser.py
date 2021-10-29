import sys

from core.parser import Parser


if __name__ == '__main__':

    if len(sys.argv) < 3:
        raise AttributeError("You need to specify an input and an output file_name!")
    if sys.argv[1] == sys.argv[2]:
        raise AttributeError("The input file_name and the output file_name must not be the same!")

    beautify_xml = '-2l' not in sys.argv
    door_to_door = '-dd' in sys.argv
    simplify_ways = '-sw' in sys.argv
    remove_dead_ends = False

    print("Parsing file data ...", end=' ', flush=True)
    parser = Parser(sys.argv[1])
    print("completed.")

    print("Calculating ways ...", end=' ', flush=True)
    parser.find_ways(simplify_ways, door_to_door)
    print("completed.")

    print("Writing data to new file ...", end=' ', flush=True)
    parser.write_osm(sys.argv[2], beautify_xml)
    print("completed.")
