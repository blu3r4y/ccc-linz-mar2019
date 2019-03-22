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

    # health and speed
    health = float(lines[3].split()[0])
    speed = float(lines[3].split()[1])

    # spawn times
    nspawn = int(lines[4])
    spawns = []
    for i in range(nspawn):
        spawns.append(int(lines[4 + i + 1]))

    # damage and range
    damage = float(lines[4 + nspawn + 1].split()[0])
    towerrange = int(lines[4 + nspawn + 1].split()[1])

    # queries
    t = int(lines[4 + nspawn + 2])
    towers = []
    for i in range(t):
        towertxt = lines[4 + nspawn + 3 + i]
        towerx = int(towertxt.split()[0])
        towery = int(towertxt.split()[1])
        towers.append((towerx, towery))

    return {
        "wx": wx, "wy": wy,
        "x": x, "y": y,
        "cmds": cmds,
        "speed": speed,
        "health": health,
        "damage": damage,
        "range": towerrange,
        "spawns": spawns,
        "towers": towers
    }


if __name__ == "__main__":
    level, quests = 4, 1
    for i in range(1, quests + 1):
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
