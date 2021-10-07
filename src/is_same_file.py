import sys


if __name__ == '__main__':
    if len(sys.argv) < 3:
        raise AttributeError("You need to specify two input files!")

    lines1 = []
    with open(sys.argv[1], "r") as file:
        for line in file:
            lines1.append(line)

    lines2 = []
    with open(sys.argv[2], "r") as file:
        for line in file:
            lines2.append(line)

    are_same = True
    for i in range(max(len(lines1), len(lines2))):
        if i >= len(lines1):
            are_same = False
            print('Line ' + str(i+1) + ': \t' + 'end of file 1')
            break
        elif i >= len(lines2):
            are_same = False
            print('Line ' + str(i+1) + ': \t' + 'end of file 2')
            break
        elif lines1[i] != lines2[i]:
            are_same = False
            print('Line ' + str(i+1) + ': \t' + 'difference found')

    if are_same:
        print('Congrats, the files are similar!')
