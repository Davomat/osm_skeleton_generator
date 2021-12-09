import sys

from core.parser import Parser


if __name__ == '__main__':
    print()

    # check for correct input
    if len(sys.argv) < 2:
        raise AttributeError("You need to specify an input file!")

    # settings and file names
    input_file_name = sys.argv[1]
    output_file_name = input_file_name[:-4] + '__routes' + input_file_name[-4:]
    beautify_xml = '-2l' not in sys.argv
    door_to_door = '-dd' in sys.argv
    simplify_ways = '-sw' in sys.argv
    remove_dead_ends = False

    # parsing
    print("##### Parsing file data ...", end=' ', flush=True)
    parser = Parser(input_file_name)
    print("completed.\n")

    # building
    print("##### Calculating routes ...")
    parser.find_ways(simplify_ways, door_to_door)
    print()  # print("completed.\n")

    # saving
    print("##### Writing data to new file ...", end=' ', flush=True)
    parser.write_osm(output_file_name, beautify_xml)
    print("completed.\n")

    print("--- finished successful ---\n")
