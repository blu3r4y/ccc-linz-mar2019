import os

from main import main
from pprint import pprint


def parse(lines):
    # world bounds
    wx = int(lines[0].split()[0])
    wy = int(lines[0].split()[0])

    # initial position
    x = int(lines[1].split()[0])
    y = int(lines[1].split()[1])
    cmds = []

    # command / step pair
    it = iter(lines[2].split())
    for e in it:
        cmds.append((e, int(next(it))))

    # speed
    speed = float(lines[3])

    # spawn times
    nspawn = int(lines[4])
    spawns = []
    for i in range(nspawn):
        spawns.append(int(lines[4 + i + 1]))

    # queries
    nqueries = int(lines[4 + nspawn + 1])
    queries = []
    for i in range(nqueries):
        qtxt = lines[4 + nspawn + 2 + i]
        qtime = int(qtxt.split()[0])
        qid = int(qtxt.split()[1])
        queries.append((qtime, qid))

    return {
        "wx": wx, "wy": wy,
        "x": x, "y": y,
        "cmds": cmds,
        "speed": speed,
        "spawns": spawns,
        "queries": queries
    }


if __name__ == "__main__":
    level, quests = 3, 5
    for i in range(0, quests + 1):
        input_file = r'..\data\level{0}\level{0}_{1}.in'.format(level, i)
        output_file = os.path.splitext(input_file)[0] + ".out"

        with open(input_file, 'r') as fi:
            data = parse(fi.readlines())
            # pprint(data)

            print("=== Output {}".format(i))
            print("======================")

            result = main(data)
            pprint(result)

            with open(output_file, 'w+') as fo:
                fo.write(result)
