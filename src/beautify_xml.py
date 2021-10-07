import sys


if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise AttributeError("You need to specify an input file!")

    lines = []
    with open(sys.argv[1], "r") as file:
        for line in file:
            lines.append(line)

    i = 1
    while i < len(lines):
        for j in range(len(lines[i])):
            if lines[i][j] == '>':
                lines.append(lines[i][j+1:])
                lines[i] = lines[i][:j+1] + '\n'
                break
        i += 1

    with open(sys.argv[1] + '_beautified.xml', "w") as file:
        file.writelines(lines)
