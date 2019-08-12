import queue
import tkMessageBox
import sys
import time
from Network import *
import os

sys.setrecursionlimit(100000)

def get_random_choice():
    choices = []
    global player
    for box in range(36):
        if grid_memory[box][1] == player or grid_memory[box][1] is None:
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
    global player,games,dif,score
    for box in range(36):
        grid_memory[box][0] = 0
        grid_memory[box][1] = None
    games += 1
    if player==1:
        dif -= 1
    else:
        dif +=1
    score = Prediction_Network.scores.get_score()
    if games>100:
        print("Evaluation Stats:")
        if dif > 0:
            AI = (games-dif)/2+dif
        else:
            AI = (games-dif)/2
        print("AI:{}   Bot(Random):{}".format(str(AI), str(games-AI)))
        os._exit(0)

def start_fission(box,player,flag = False):
    if flag:
        global ended
        if game_ended() and ended == 0:
            ended = 1
            time.sleep(0.01)
            return None
    if grid_memory[box][1] is None:
        grid_memory[box][0] += 1
        grid_memory[box][1] = player
        return None

    if grid_memory[box][0] >= 3:
        get_neighbours(box)
        while not q.empty():
            nbox = q.get()
            grid_memory[box][0] = 0
            grid_memory[box][1] = None
            start_fission(nbox,player,flag = True)

    else:
        if not flag and grid_memory[box][1] != player:
            return None
        grid_memory[box][0] += 1
        grid_memory[box][1] = player
        if ended == 1:
            return None
        if box in [0, 5, 30, 35] and grid_memory[box][0] > 1:
            get_neighbours(box)
            while not q.empty():
                nbox = q.get()
                grid_memory[box][0] = 0
                grid_memory[box][1] = None
                start_fission(nbox, player, flag=True)

        elif (box % 6 == 0 or box % 6 == 5 or box in range(6) or box in range(30, 36)) and grid_memory[box][0] > 2:
            get_neighbours(box)
            while not q.empty():
                nbox = q.get()
                grid_memory[box][0] = 0
                grid_memory[box][1] = None
                start_fission(nbox, player, flag=True)



grid_memory = [[0,None] for i in range(36)]
player = 0
color = [(0,255,0),(0,0,255)]
q = queue.Queue()
games = 0
ended = 0
dif = 0
score = 0
Prediction_Network = brain(36,36,10000)
Prediction_Network.net.to('cuda')
size = 6

def get_st():
    game_state = []
    for box in range(36):
        if grid_memory[box][1] == 0:
            game_state.append(float(grid_memory[box][0]))
        elif grid_memory[box][0] == 1:
            game_state.append(float(-1*grid_memory[box][0]))
        else:
            game_state.append(0.0)
    return game_state

def get_valid():
    valid = []
    for box in range(36):
        if grid_memory[box][1] in [player,None]:
            valid.append(box)
    return valid

def captured(st,St):
    sum = 0
    for b1,b2 in zip(st,St):
        if b1*b2 < 0:
            sum += np.sign(b2-b1)
    return sum


Prediction_Network.load('weights/chain')
every = 100
i = 0
size = Prediction_Network.mem.size
first = True
st = []
St = []
while True:
    player = 0
    reward = 0
    i +=1
    if first:
        st = get_st()
        first = False
    box1 = Prediction_Network.next_action(st,get_valid(),True)
    start_fission(box1, player)
    if ended == 1:
        clear_board()
        first = True
        ended = 0
        continue
    player = 1
    box2 = get_random_choice()
    start_fission(box2, player)
    St = get_st()
    if ended == 1:
        clear_board()
        ended = 0
        first = True
        continue
    st = St


