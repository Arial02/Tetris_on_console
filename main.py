from random import randint
import numpy as np
from time import sleep
import keyboard
import curses, sys
from threading import Thread
from functools import reduce


def prod(iterable):
    return reduce(lambda x, y: x*y, iterable, 1)

def swap_rows(arr, k, r):
    for i in range(len(arr[k])):
        arr[k][i], arr[r][i] = arr[r][i], arr[k][i]

ACCELERATION = 0.99

COLOR = {0: "◦", 1: "■", 2: "□"} # обозначение на карте: обозначение цвета

UP = (0, 1)
RIGHT = (1, 0)
DOWN = (0, -1)
LEFT = (-1, 0)

FIGURES = {"O":((0,0),(1,0),(0,-1),(1,-1)),
           "S":((1,0),(2,0),(0,-1),(1,-1)),
           "T":((0,0),(1,0),(2,0),(1,-1)),
           "Z":((0,0),(1,0),(1,-1),(2,-1)),
           "I":((0,0),(0,-1),(0,-2),(0,-3)),
           "L":((0,0),(1,0),(2,0),(0,-1)),
           "J":((0,0),(1,0),(2,0),(2,-1))}

TURNING = ((0,-1),(1,0))

class Tetris:
    def __init__(self):
        self.stdscr = curses.initscr()
        self.hook = keyboard.hook(lambda event: self.events.append(event))
        self.events=[]
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)
        self.map=[[0 for j in range(10)] for i in range(23)] # 3 rows in the top are hidden
        self.timing=0.6
        self.init_pos=4
        self.score=0
        self.death=False
        self.pause=False
        self.reset()

    def __del__(self):
        self.stdscr.clear()
        self.stdscr.refresh()
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()
        keyboard.unhook_all()

    def reborn(self):
        self.stdscr = curses.initscr()
        self.hook = keyboard.hook(lambda event: self.events.append(event))
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)

    def reset(self):
        self.is_pull=False
        self.is_fast=False
        ready_rows=0
        self.timing*=ACCELERATION
        self.kind=list(FIGURES.keys())[randint(0,6)]
        self.obj = FIGURES[self.kind]
        self.obj = [[self.obj[i][j] + RIGHT[j]*self.check_init_pos() for j in range(2)] for i in range(4)]
        if self.kind!="I":
            self.obj = [[self.obj[i][j] + DOWN[j] * 2 for j in range(2)] for i in range(4)]
        for i in range(len(self.obj)):
            self.map[-self.obj[i][1]][self.obj[i][0]]=2
        for k in range(3,len(self.map),1):
            if prod(self.map[k]):
                self.map[k]=[0 for i in range(len(self.map[k]))]
                ready_rows+=1
                for i in range(k,0,-1):
                    swap_rows(self.map, i, i-1)
        if ready_rows:
            self.score+=100*(2*ready_rows-1)
        if sum([1 if self.map[3][k]==1 else 0 for k in range(len(self.map[3]))]):
            self.death=True

    def check_init_pos(self):
        if self.kind=="O":
            return self.init_pos if self.init_pos!=9 else 8
        elif self.kind!="I":
            return self.init_pos if self.init_pos<8 else 7
        else:
            return self.init_pos

    def update(self):
        for event in self.events:
            if event.name == "q" and event.event_type == "down":
                self.__del__()
                print("You loose, man!\nYou got {} points.\n".format(self.score))
                sys.exit(0)
            if event.name == "p" and event.event_type == "down":
                self.pause = True
            if event.name == "right" and event.event_type == "down":
                if not sum([1 if self.obj[k][0]==9 or self.map[-self.obj[k][1]][self.obj[k][0]+1]==1 else 0 for k in range(len(self.obj))]):
                    for i in range(len(self.obj)):
                        self.map[-self.obj[i][1]][self.obj[i][0]] = 0
                    self.obj = [[self.obj[i][j] + RIGHT[j] for j in range(len(self.obj[i]))] for i in range(len(self.obj))]
                    for i in range(len(self.obj)):
                        self.map[-self.obj[i][1]][self.obj[i][0]] = 2
            if event.name == "left" and event.event_type == "down":
                if not sum([1 if self.obj[k][0]==0 or self.map[-self.obj[k][1]][self.obj[k][0]-1]==1 else 0 for k in range(len(self.obj))]):
                    for i in range(len(self.obj)):
                        self.map[-self.obj[i][1]][self.obj[i][0]] = 0
                    self.obj = [[self.obj[i][j] + LEFT[j] for j in range(len(self.obj[i]))] for i in range(len(self.obj))]
                    for i in range(len(self.obj)):
                        self.map[-self.obj[i][1]][self.obj[i][0]] = 2
            if event.name == "space" and event.event_type == "down":
                self.is_pull = True
            if event.name == "up" and event.event_type == "down":
                shift = [self.obj[0][0], self.obj[0][1]]
                shift[0] -= 1 if self.kind == "S" else 0
                backup = [[self.obj[i][j] for j in range(len(self.obj[i]))] for i in range(len(self.obj))]
                for i in range(len(self.obj)):
                    self.map[-self.obj[i][1]][self.obj[i][0]] = 0
                for i in range(len(self.obj)):
                    self.obj[i][0] -= shift[0]
                    self.obj[i][1] -= shift[1]
                self.obj = (np.array(self.obj) @ np.array(TURNING)).tolist()
                for i in range(len(self.obj)):
                    self.obj[i][0] += shift[0]
                    self.obj[i][1] += shift[1]
                for k in range(len(self.obj)):
                    if self.obj[k][0] < 0:
                        chg = self.obj[k][0]
                        for i in range(len(self.obj)):
                            self.obj[i][0] -= chg
                    elif self.obj[k][0] > 9:
                        chg = (self.obj[k][0] - 9)
                        for i in range(len(self.obj)):
                            self.obj[i][0] -= chg
                    if -self.obj[k][1] < 0:
                        chg = self.obj[k][1]
                        for i in range(len(self.obj)):
                            self.obj[i][1] -= chg
                    elif -self.obj[k][1] > 22:
                        chg = (self.obj[k][1] + 22)
                        for i in range(len(self.obj)):
                            self.obj[i][1] -= chg
                for k in range(len(self.obj)):
                    if self.map[-self.obj[k][1]][self.obj[k][0]] == 1:
                        self.obj = ((backup[i][j] for j in range(len(backup[i]))) for i in range(len(backup)))
                        break
                for i in range(len(self.obj)):
                    self.map[-self.obj[i][1]][self.obj[i][0]] = 2
            if event.name == "down" and event.event_type == "down":
                self.is_fast = True
            if event.name == "down" and event.event_type == "up":
                self.is_fast = False
        self.events.clear()
        if sum([1 if -self.obj[i][1]==22 else 0 for i in range(len(self.obj))]):
            for i in range(len(self.obj)):
                self.map[-self.obj[i][1]][self.obj[i][0]] = 1
            self.init_pos=self.obj[0][0] if self.kind!="S" else self.obj[0][0]-1
            self.reset()
        elif sum([0 if self.map[-(self.obj[i][1]-1)][self.obj[i][0]]!=1 else 1 for i in range(len(self.obj))]):
            for i in range(len(self.obj)):
                self.map[-self.obj[i][1]][self.obj[i][0]] = 1
            self.init_pos=self.obj[0][0] if self.kind!="S" else self.obj[0][0]-1
            self.reset()
        else:
            for i in range(len(self.obj)):
                self.map[-self.obj[i][1]][self.obj[i][0]] = 0
            self.obj = [[self.obj[i][j]+DOWN[j] for j in range(len(self.obj[i]))] for i in range(len(self.obj))]
            for i in range(len(self.obj)):
                self.map[-self.obj[i][1]][self.obj[i][0]] = 2


    def draw(self):
        if self.death:
            self.__del__()
            print("You loose, man!\nYou got {} points.\n(Press Q)\n".format(self.score))
            keyboard.wait("q")
            sys.exit(0)
        elif self.pause:
            flag = False
            self.__del__()
            t = Thread(target=self.pauser, args=(lambda: flag,))
            t.start()
            keyboard.wait("p")
            self.pause=False
            flag=True
            t.join()
            self.reborn()
        else:
            try:
                self.stdscr.addstr(" "+"_"*19+"\n")
                for i in range(3,len(self.map),1):
                    self.stdscr.addstr("|"+" ".join(list(map(lambda x: COLOR[x], self.map[i]))) + "|\n")
                self.stdscr.addstr(" "+"̅"*19+"\n")
                self.stdscr.addstr(" "*2+"You got {} points!".format(self.score))
                self.stdscr.refresh()
                self.stdscr.clear()
            except curses.error:
                self.__del__()
                print("The console must be open with at least 23 visible free lines!")
                sys.exit(1)
        if self.is_pull:
            sleep(0.034)
        elif self.is_fast:
            sleep(self.timing*0.7)
        else:
            sleep(self.timing)

    def pauser(self, stop):
        while True:
            for i in range(4):
                sys.stdout.write("\rPause" + "." * i + " " * (3-i))
                sys.stdout.flush()
                sleep(0.5)
            if stop():
                break

def game_loop(game):
    while True:
        try:
            game.update()
        except Exception:
            game.__del__()
            print("UPDATE ERROR")
            sys.exit(1)
        try:
            game.draw()
        except Exception:
            game.__del__()
            print("DRAW ERROR")
            sys.exit(1)

game_loop(Tetris())
# отрисовка на карте с минусом в игрике, т.к. у фигуры ось игрик вверх, у карты - вниз
# upd оси походу тоже попутаны, ахах, итого map[-obj.y][obj.x] <- map.x & map.y
