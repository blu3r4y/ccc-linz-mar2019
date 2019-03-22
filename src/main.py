import enum


class Direction(enum.Enum):
    Right = 0
    Down = 1
    Left = 2
    Up = 3

    def turn(self, ntimes=1):
        return Direction((self.value + ntimes) % 4)

    def move(self, x, y, ntimes=1):
        if self == Direction.Right:
            return x + ntimes, y
        elif self == Direction.Down:
            return x, y + ntimes
        elif self == Direction.Left:
            return x - ntimes, y
        elif self == Direction.Up:
            return x, y - ntimes


def main(data):
    x, y, d = data["x"], data["y"], Direction.Right

    visited = [(x, y)]

    for command, ntimes in data["cmds"]:
        for i in range(ntimes):
            if command == "F":
                x, y = d.move(x, y)
                visited.append((x, y))
            elif command == "T":
                d = d.turn()

    return "\n".join(["{} {}".format(x, y) for x, y in visited])
