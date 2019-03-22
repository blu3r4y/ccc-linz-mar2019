import math
import enum
from collections import defaultdict
from abc import abstractmethod
from pprint import pprint
import itertools
import numpy as np

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


class TowerState(enum.Enum):
    Seeking = 0
    Locked = 1

    def switch(self):
        return TowerState.Seeking if self == TowerState.Locked else TowerState.Locked


class Tower(Cell):

    def __init__(self, maze, x, y, damage, towerrange):
        super().__init__(maze, x, y)
        self.damage = damage
        self.towerrange = towerrange
        self.state = TowerState.Seeking
        self.target = None

    def lock_on_new_alien(self):
        distances = [(a, self.position_to_alien(a))
                     for a in self.maze.aliens.values()
                     if a.alive()]

        # filter out of range targets away
        distances = [e for e in distances if e[1] <= self.towerrange]

        if len(distances) > 0:
            ordered = sorted(distances, key=lambda e: (e[1], e[0].identifier))
            self.target = ordered[0][0]
            self.state = TowerState.Locked
            print("Tower #{}: Locked on target in range {}".format(hash(self), ordered[0][1]))
        else:
            # nothing to lock
            self.target = None
            self.state = TowerState.Seeking
            print("Tower #{}: No target found".format(hash(self)))

    def calculate_shot(self):
        if self.target:
            # target dead or out of range?
            target_out_of_range = self.position_to_alien(self.target) > self.towerrange
            if not self.target.alive() or target_out_of_range:
                self.state = TowerState.Seeking
                print("Tower #{}: Target dead or out of range, removed.".format(hash(self)))

        if self.state == TowerState.Seeking:
            self.lock_on_new_alien()

        if self.state == TowerState.Locked:
            return self.target

        return None

    def shot_for_real(self, target):
        target.get_shot_by(self)

    def position_to_alien(self, alien):
        a = np.array([self.x, self.y])
        # b = np.array([alien.x, alien.y])
        b = np.array([alien.xexact, alien.yexact])
        norm = np.linalg.norm(a - b)
        return norm


class Alien(Cell):

    def __init__(self, maze, x, y, identifier, health, speed, sequence, direction=Direction.Right):
        super().__init__(maze, x, y)
        self.identifier = identifier
        self.direction = direction
        self.sequence = sequence
        self.health = health
        self.speed = speed

        # internal offset
        # self.dx = 0.0
        # self.dy = 0.0

        # sequence position and internal sequence position
        self.si = 0
        self.sii = 0
        self.seq_old = 0.0

    @property
    def xexact(self):
        return self.exact_position()[0]

    @property
    def yexact(self):
        return self.exact_position()[1]

    def alive(self):
        return self.health > 0

    def get_shot_by(self, tower):
        self.health -= tower.damage
        print("Alien {} got damage {}. New health {}".format(self.identifier, tower.damage, self.health))

    def exact_position(self):
        return self.direction.move(self.x, self.y, speed=self.seq_old)

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

    def reached_base(self):
        return self.si == len(self.sequence)

    def move(self):
        xnew, ynew = self.direction.move(self.x, self.y, speed=1)

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
        self.towers = []
        self.grid = [[[] for _ in range(width)] for _ in range(height)]
        self.tick = 0

    def add_alien(self, alien: Alien):
        self.aliens[alien.identifier] = alien
        self.grid[alien.x][alien.y].append(alien)

    def add_tower(self, tower: Tower):
        self.towers.append(tower)
        self.grid[tower.x][tower.y].append(tower)

    def update_aliens(self):
        for alien in self.aliens.values():
            alien.step()

        self.tick += 1

    def update_towers(self):
        targets = []
        for tower in self.towers:
            target = tower.calculate_shot()
            if target:
                targets.append((target, tower))

        # finally ..
        for target, tower in targets:
            tower.shot_for_real(target)

    def any_alien_reached_base(self):
        # check if any alien reached the base
        reached_base = False

        for alien in self.aliens.values():
            # any alien reached the base?
            if alien.reached_base():
                reached_base = True
                break

        return reached_base

    def all_aliens_dead(self):
        # check if all aliens are dead
        num_alive = 0

        for alien in self.aliens.values():
            # alien still alive?
            if alien.alive():
                num_alive += 1

        return num_alive == 0

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
    health = data["health"]

    sequence = data["cmds"]

    damage = data["damage"]
    towerrange = data["range"]

    # build aliens
    num_aliens = len(data["spawns"])
    aliens = defaultdict(list)
    for i, spawn_tick in enumerate(data["spawns"]):
        alien = Alien(maze, x, y, identifier=i, health=health, speed=speed, sequence=sequence)
        aliens[spawn_tick].append(alien)

    # build and towers
    for towerx, towery in data["towers"]:
        tower = Tower(maze, towerx, towery, damage, towerrange)
        maze.add_tower(tower)

    result = "TIE"
    tick = 0

    # simulate game
    while True:

        # 1) update all alien positions
        maze.update_aliens()

        # 2) check if any alien has reached the end?
        reached_base = maze.any_alien_reached_base()
        if reached_base:
            result = "LOSS"
            print("Alien reached the base at tick {}".format(tick))
            break

        # 3) spawn new aliens
        if tick in aliens.keys():
            for alien in aliens[tick]:
                maze.add_alien(alien)

        # 4) simulate tower shots
        if tick > 0:
            maze.update_towers()

        # 5) check for dead aliens
        all_dead = maze.all_aliens_dead()

        # 6) check if all aliens are dead and no more will be spawning
        no_more_spawning = len(maze.aliens) == num_aliens
        if no_more_spawning and all_dead:
            result = "WIN"
            print("All aliens are dead at tick {}".format(tick))
            break

        tick += 1

    return "\n".join([str(tick), result])
