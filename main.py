import pyxel
from random import randint
import numpy as np
from time import sleep, time
import keyboard
########## DEBUG ############

counter, beg, end=0,0,0

# на 50 строчке функция pyxel.run(...) сбоит
# должна работать так: UPDATE DRAW UPDATE DRAW UPDATE DRAW UPDATE DRAW
# работает так: UPDATE DRAW UPDATE DRAW UPDATE UPDATE UPDATE UPDATE UPDATE DRAW UPDATE UPDATE UPDATE...

##############################


def swap_rows(arr, k, r):
    for i in range(len(arr[k])):
        arr[k][i], arr[r][i] = arr[r][i], arr[k][i]

ACCELERATION = 0.99

COLOR = {0: 0, 1: 8, 2: 11} # обозначение на карте: обозначение цвета

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
        pyxel.init(10, 20, caption="Tetris")
        self.map=[[0 for j in range(10)] for i in range(23)] # 3 rows in the top are hidden
        self.timing=0.6
        self.init_pos=4
        self.score=0
        self.death=False
        self.pause=False
        self.reset()
        pyxel.run(self.update, self.draw) # эта функция описана в ./Lib/site-packages/pyxel/__init__.py на ~560 строке
        """while True:
            try:
                self.update()
            except:
                print("ERROR UPDATE")
            try:
                self.draw()
            except:
                print("ERROR DRAW")""" # эквивалентно ли? Смущает блок core.run(...)

    def reset(self):
        print("(RESET)", end=" ")
        self.is_pull=False
        self.is_fast=False
        ready_rows=0
        self.timing*=ACCELERATION
        self.dir = UP
        self.kind=list(FIGURES.keys())[randint(0,6)]
        self.obj = FIGURES[self.kind]
        self.obj = [[self.obj[i][j] + RIGHT[j]*self.init_pos for j in range(2)] for i in range(4)]
        if self.kind!="I":
            self.obj = [[self.obj[i][j] + DOWN[j] * 2 for j in range(2)] for i in range(4)]
        for i in range(len(self.obj)):
            self.map[-self.obj[i][1]][self.obj[i][0]]=2
        for k in range(3,len(self.map),1):
            if sum(self.map[i])>=10:
                self.map[k]=[0 for i in range(len(self.map[k]))]
                ready_rows+=1
                for i in range(k,0,-1):
                    swap_rows(self.map, i, i-1)
        self.score+=100*(2*ready_rows-1)
        if sum([1 if self.map[3][k]==1 else 0 for k in range(len(self.map[3]))]):
            self.death=True


    def update(self):
        print("UPDATE",end=" = ")
        beg=time()
        if pyxel.btnp(pyxel.KEY_Q): # кнопки не отдебажены! Дебаг после разрешения проблемы с 50 строчкой
            pyxel.quit()
        if pyxel.btnp(pyxel.KEY_P):
            self.pause=True # keyboard.wait("p") в отрисовке экрана паузы
        if pyxel.btnp(pyxel.KEY_RIGHT):
            self.obj = [[self.obj[i][j] + RIGHT[j] for j in range(len(self.obj[i]))] for i in range(len(self.obj))]
        if pyxel.btnp(pyxel.KEY_LEFT):
            self.obj = [[self.obj[i][j] + LEFT[j] for j in range(len(self.obj[i]))] for i in range(len(self.obj))]
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.is_pull=True
        if pyxel.btnp(pyxel.KEY_UP):
            shift = (self.obj[0][0],self.obj[0][1])
            shift[0]-=1 if self.kind=="S" else 0
            backup = ((self.obj[i][j] for j in range(len(self.obj[i]))) for i in range(len(self.obj)))
            for i in range(len(self.obj)):
                self.map[-self.obj[i][1]][self.obj[i][0]] = 0
            for i in range(len(self.obj)):
                self.obj[i][0]-=shift[0]
                self.obj[i][1]-=shift[1]
            if self.dir==UP: self.dir=RIGHT
            elif self.dir==RIGHT: self.dir=DOWN
            elif self.dir==DOWN: self.dir=LEFT
            elif self.dir==LEFT: self.dir=UP
            self.obj = tuple(map(lambda x: tuple(x), (np.array(self.obj) @ np.array(TURNING)).tolist()))
            for i in range(len(self.obj)):
                self.obj[i][0]+=shift[0]
                self.obj[i][1]+=shift[1]
            for k in range(len(self.obj)):
                if self.obj[k][0]<0:
                    for i in range(len(self.obj)):
                        self.obj[i][0]-=self.obj[k][0]
                elif self.obj[k][0]>9:
                    for i in range(len(self.obj)):
                        self.obj[i][0]-=(self.obj[k][0]-9)
                if self.obj[k][1]<0:
                    for i in range(len(self.obj)):
                        self.obj[i][1]-=self.obj[k][1]
                elif self.obj[k][1]>22:
                    for i in range(len(self.obj)):
                        self.obj[i][1]-=(self.obj[k][1]-22)
            for k in range(len(self.obj)):
                if self.map[-self.obj[k][1]][self.obj[k][0]]==1:
                    self.obj=((backup[i][j] for j in range(len(backup[i]))) for i in range(len(backup)))
                    break
            for i in range(len(self.obj)):
                self.map[-self.obj[i][1]][self.obj[i][0]] = 2
        if pyxel.btnp(pyxel.KEY_DOWN):
            self.is_fast=True
        if pyxel.btnr(pyxel.KEY_DOWN):
            self.is_fast=False
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
        end = time()
        print(end-beg,"s")


    def draw(self):
        print("DRAW")
        pyxel.cls(0)
        if self.death:
            # Тут должен был быть экран смерти
            keyboard.wait("q")
            pyxel.quit()
        elif self.pause:
            # Тут должен был быть экран паузы
            keyboard.wait("p")
            self.pause=False
        else:
            pyxel.clip() # в перспективе можно где-нибудь внизу записать очки, цифры 3*5рx
            for i in range(3,len(self.map),1):
                for j in range(len(self.map[i])):
                    pyxel.pset(j,i-3,COLOR[self.map[i][j]])
        if self.is_pull:
            sleep(0.034)
        elif self.is_fast:
            sleep(self.timing*0.7)
        else:
            sleep(self.timing)

Tetris()
# отрисовка на карте с минусом в игрике, т.к. у фигуры ось игрик вверх, у карты - вниз
# upd оси походу тоже попутаны, ахах, итого map[-obj.y][obj.x] <- map.x & map.y
