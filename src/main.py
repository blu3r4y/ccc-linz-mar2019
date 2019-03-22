import math
import enum
from collections import defaultdict
from abc import abstractmethod
from pprint import pprint

from colorama import Fore, Back, Style


class Direction(enum.Enum):
    Right = 0
    Down = 1
    Left = 2
    Up = 3

    def turn(self, ntimes=1):
        return Direction((self.value + ntimes) % 4)

    def move(self, x, y, speed):
        if self == Direction.Right:
            return x + speed, y
        elif self == Direction.Down:
            return x, y + speed
        elif self == Direction.Left:
            return x - speed, y
        elif self == Direction.Up:
            return x, y - speed


class Cell:

    @abstractmethod
    def __init__(self, maze, x, y):
        self.maze = maze
        self.x = x
        self.y = y


class Alien(Cell):

    def __init__(self, maze, x, y, identifier, speed, sequence, direction=Direction.Right):
        super().__init__(maze, x, y)
        self.identifier = identifier
        self.direction = direction
        self.sequence = sequence
        self.speed = speed

        # internal offset
        self.dx = 0.0
        self.dy = 0.0

        # sequence position and internal sequence position
        self.si = 0
        self.sii = 0
        self.seq_old = 0.0

    @property
    def xfloat(self):
        return self.x + self.dx

    @property
    def yfloat(self):
        return self.y + self.dy

    def step(self):
        seq_steps, seq_delta = divmod(self.speed + self.seq_old, 1.0)
        self.seq_old = seq_delta

        i = 0
        while i < int(seq_steps):

            # abort if there are no commands left
            if self.si >= len(self.sequence):
                return

            action, ntimes = self.sequence[self.si]

            # turn (doesn't cost move speed, do not increase i)
            if action == 'T':
                self.direction = self.direction.turn(ntimes)
                self.si += 1

            # move forward
            elif action == 'F':
                if self.sii < ntimes:
                    self.move()
                self.sii += 1

                # did we process this entire forward move?
                if self.sii == ntimes:
                    self.sii = 0
                    self.si += 1

                # forward move costs tick
                i += 1

    def move(self):
        xold, yold = self.xfloat, self.yfloat
        x, y = self.direction.move(self.xfloat, self.yfloat, speed=1.0)
        xnew = math.floor(x)
        ynew = math.floor(y)
        self.dx = x % 1.0
        self.dy = y % 1.0

        # let's move there ...
        if self.x != xnew or self.y != ynew:
            self.maze.move_to_new_position(self, xnew, ynew)

        # print("Moved {} from ({:.2f}, {:.2f}) -> ({:.2f}, {:.2f})"
        #      .format(self.identifier, xold, yold, self.xfloat, self.yfloat))

    def __str__(self):
        return "A"


class Maze(object):

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.aliens = {}
        self.grid = [[[] for _ in range(width)] for _ in range(height)]
        self.tick = 0

    def add_alien(self, alien: Alien):
        self.aliens[alien.identifier] = alien
        self.grid[alien.x][alien.y].append(alien)

    def step(self):
        for alien in self.aliens.values():
            alien.step()

        self.tick += 1

    def move_to_new_position(self, a: Cell, xnew, ynew):
        self.grid[a.x][a.y].remove(a)
        self.grid[xnew][ynew].append(a)
        a.x = xnew
        a.y = ynew

    def __str__(self, highlight=None):
        result = "Tick #{}".format(self.tick)
        result += '\n'
        for x in range(self.height):
            for y in range(self.width):
                cell = self.grid[x][y]

                # cell colors
                color = f'{Fore.LIGHTWHITE_EX}'
                if len(cell) == 0:
                    color = f'{Fore.LIGHTBLUE_EX}'
                elif any(isinstance(e, Alien) for e in cell):
                    color = f'{Fore.LIGHTRED_EX}'

                # possible highlight
                candidate = str(cell[0]) if len(cell) > 0 else "."
                result += color + candidate if not highlight or candidate not in highlight else f'{Back.RED}X'
                result += f'{Style.RESET_ALL}'

            result += '\n'
        return result


def main(data):
    maze = Maze(data["wx"], data["wy"])

    # initial position and speed
    x, y = data["x"], data["y"]
    speed = data["speed"]

    sequence = data["cmds"]

    # build aliens
    aliens = defaultdict(list)
    for i, spawn_tick in enumerate(data["spawns"]):
        alien = Alien(maze, x, y, identifier=i, speed=speed, sequence=sequence)
        aliens[spawn_tick].append(alien)

    # build query lookup
    queries = defaultdict(list)
    for query_pos, (tick, alien_id) in enumerate(data["queries"]):
        queries[tick].append((query_pos, alien_id))

    answers = [None] * len(data["queries"])
    max_tick = max(queries.keys())

    # simulate game
    for tick in range(max_tick + 1):
        # print(maze)

        maze.step()

        # spawn aliens
        if tick in aliens.keys():
            for alien in aliens[tick]:
                maze.add_alien(alien)

        # answer queries
        if tick in queries.keys():
            for query_pos, alien_id in queries[tick]:
                alien = maze.aliens[alien_id]
                answers[query_pos] = (tick, alien_id, alien.x, alien.y)

    # print(answers)

    return "\n".join(["{} {} {} {}".format(*vals) for vals in answers])
