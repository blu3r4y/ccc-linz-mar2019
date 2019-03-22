import os
import json

from main import main
from pprint import pprint


def parse(lines):
    x = int(lines[0].split()[0])
    y = int(lines[0].split()[1])
    cmds = []

    it = iter(lines[1].split())
    for e in it:
        cmds.append((e, int(next(it))))

    return {"x": x, "y": y, "cmds": cmds}


if __name__ == "__main__":
    level, quests = 1, 6
    for i in range(1, quests):
        input_file = r'..\data\level{0}\level{0}_{1}.in'.format(level, i)
        output_file = os.path.splitext(input_file)[0] + ".out"

        with open(input_file, 'r') as fi:
            data = parse(fi.readlines())
            # pprint(data)

            print("=== Input {}".format(i))
            print("======================")

            result = main(data)
            pprint(result)

            with open(output_file, 'w+') as fo:
                fo.write(result)
