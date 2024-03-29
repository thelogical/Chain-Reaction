import pygame
import queue
from Tkinter import *
import tkMessageBox
import sys
from threading import Thread
import time
from Network import *

sys.setrecursionlimit(100000)

def is_done():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return True

def get_random_choice():
    choices = []
    global player
    for box in range(36):
        if grid_memory[box][1] != (player + 1) % 2:
            choices.append(box)
    return random.choice(choices)


def get_neighbours(box):
    if box - 6 >= 0:
        q.put(box - 6)
    if box + 6 < 36:
        q.put(box + 6)
    if (box - 1) % 6 < 5:
        q.put(box - 1)
    if (box + 1) % 6 > 0:
        q.put(box + 1)


def game_ended():
    p = (player + 1) % 2
    for box in range(36):
        if grid_memory[box][1] == p:
            return False
    return True

def clear_board():
    global player,games,dif
    for box in range(36):
        pygame.draw.rect(screen,(0,0,0),(grid[box][0]+1 ,grid[box][1]+1 ,98,98),0)
        grid_memory[box][0] = 0
        grid_memory[box][1] = None
    text = f2.render(str(games), True, (0, 0, 0))
    textRect = text.get_rect()
    textRect.center = (45, 25)
    screen.blit(text, textRect)
    games += 1
    text = f2.render(str(games), True, (255, 255, 0))
    textRect = text.get_rect()
    textRect.center = (45, 25)
    screen.blit(text, textRect)
    text = f2.render(str(dif), True, (0, 0, 0))
    textRect = text.get_rect()
    textRect.center = (175, 25)
    screen.blit(text, textRect)
    if player==1:
        dif -= 1
    else:
        dif +=1
    text = f2.render(str(dif), True, (255, 150, 75))
    textRect = text.get_rect()
    textRect.center = (175, 25)
    screen.blit(text, textRect)
    pygame.display.update()

def start_fission(box,player,flag = False):
    if flag:
        global k
        if game_ended() and k == 0:
            k = 1
            time.sleep(0.01)
            return None
    if grid_memory[box][1] is None:
        grid_memory[box][0] += 1
        grid_memory[box][1] = player
        text = font.render(str(grid_memory[box][0]), True, color[player])
        textRect = text.get_rect()
        textRect.center = (grid[box][0] + 50, grid[box][1] + 50)
        screen.blit(text, textRect)
        pygame.display.update(textRect)
        return None

    if grid_memory[box][0] >= 3:
        get_neighbours(box)
        while not q.empty():
            nbox = q.get()
            text = font.render(str(grid_memory[box][0]), True, (0, 0, 0))
            textRect = text.get_rect()
            textRect.center = (grid[box][0] + 50, grid[box][1] + 50)
            screen.blit(text, textRect)
            pygame.display.update(textRect)
            grid_memory[box][0] = 0
            grid_memory[box][1] = None
            start_fission(nbox,player,flag = True)

    else:
        if not flag and grid_memory[box][1] != player:
            window = Tk()
            window.withdraw()
            tkMessageBox.showerror("Error", "Invalid move!")
            window.mainloop()
            return None
        text = font.render(str(grid_memory[box][0]), True, (0,0,0))
        textRect = text.get_rect()
        textRect.center = (grid[box][0] + 50, grid[box][1] + 50)
        screen.blit(text, textRect)
        grid_memory[box][0] += 1
        grid_memory[box][1] = player
        text = font.render(str(grid_memory[box][0]), True, color[player])
        textRect = text.get_rect()
        textRect.center = (grid[box][0] + 50, grid[box][1] + 50)
        screen.blit(text, textRect)
        pygame.display.update(textRect)
        if k == 1:
            return None
        if box in [0, 5, 30, 35] and grid_memory[box][0] > 1:
            get_neighbours(box)
            c = 0
            while not q.empty():
                c += 1
                nbox = q.get()
                text = font.render(str(grid_memory[box][0]), True, (0, 0, 0))
                textRect = text.get_rect()
                textRect.center = (grid[box][0] + 50, grid[box][1] + 50)
                screen.blit(text, textRect)
                pygame.display.update(textRect)
                grid_memory[box][0] = 0
                grid_memory[box][1] = None
                start_fission(nbox, player, flag=True)

        elif (box % 6 == 0 or box % 6 == 5 or box in range(6) or box in range(30, 36)) and grid_memory[box][0] > 2:
            get_neighbours(box)
            while not q.empty():
                nbox = q.get()
                text = font.render(str(grid_memory[box][0]), True, (0, 0, 0))
                textRect = text.get_rect()
                textRect.center = (grid[box][0] + 50, grid[box][1] + 50)
                screen.blit(text, textRect)
                pygame.display.update(textRect)
                grid_memory[box][0] = 0
                grid_memory[box][1] = None
                start_fission(nbox, player, flag=True)


pygame.init()
screen = pygame.display.set_mode((700, 700))
start = (50,50)
grid = []
grid_memory = [[0,None] for i in range(36)]
player = 0
color = [(0,255,0),(0,0,255)]
q = queue.Queue()
font = pygame.font.Font('freesansbold.ttf', 32)
f2 = pygame.font.Font('freesansbold.ttf', 15)
games = 0
k = 0
dif = 0
Prediction_Network = brain(2,36,10000,True)
Prediction_Network.net.to('cuda')

size = 6
for i in range(6):
    for j in range(6):
        grid.append((start[0] + j *100,start[1] + i * 100))

for i in range(6*6):
        pygame.draw.rect(screen, (255,255,255), (grid[i][0], grid[i][1], 100, 100), 1)
pygame.display.flip()

def get_st(player):
    s1 = 0
    s2 = 0
    for b in range(36):
        if grid_memory[b][1] == player:
            s1+=1
        elif grid_memory[b][1] == (player + 1) % 2:
            s2+=1
    if s2 > 0:
        return [float(s1)/float(36),float(s1)/float(s2)]
    else:
        return [float(s1)/float(36),0]

def valid(box):
    if grid_memory[box][1] not in [0,None]:
        return False
    return True

every = 100
i = 0
size = Prediction_Network.mem.size
first = True
st = []
St = []
while not is_done():
    player = 0
    reward = 0
    i +=1
    if first:
        st = get_st(0)
        first = False
    box1 = Prediction_Network.net.next_action(st)
    if not valid(box1):
        reward-=0.5
    else:
        start_fission(box1, player)
    if k == 1:
        clear_board()
        St = get_st(0)
        Prediction_Network.mem.save([st, St, 1, box1])
        first = True
        k = 0
        continue
    player = 1
    box2 = get_random_choice()
    start_fission(box2, player)
    if k == 1:
        clear_board()
        k = 0
        Prediction_Network.mem.save([st, St, -1, box1])
        first = True
        continue
    St = get_st(0)
    if st[0] < St[0]:
        reward -=0.1
    else:
        reward +=0.1
    Prediction_Network.mem.save([st,St,reward,box1])
    if i > size/10:
        sam = Prediction_Network.mem.sample(64)
        Prediction_Network.learn(sam)
        i = size/10 + 1
    st = St


