import torch
import torch.nn.functional as f
import torch.nn as nn
import numpy as np
import torch.optim as optim
from torch.autograd import Variable
import random
<<<<<<< HEAD
import os
=======
>>>>>>> 72427f0df644fafb7ccb8b52ba875d5a93e03f39


class Network(nn.Module):

    def __init__(self,input_size,actions):
        super(Network,self).__init__()
        torch.manual_seed(random.randint(0,10))
        self.input_size = input_size
        self.actions = actions
<<<<<<< HEAD
        self.fc1 = nn.Linear(input_size,400)
        self.bn1 = nn.BatchNorm1d(400)
        self.fc2 = nn.Linear(400,228)
        self.bn2 = nn.BatchNorm1d(228)
        self.fc3 = nn.Linear(228, 128)
        self.bn3 = nn.BatchNorm1d(128)
        self.fc4 = nn.Linear(128,64)
        self.bn4 = nn.BatchNorm1d(64)
        self.fc5 = nn.Linear(64,36)

    def forward(self, input_batch,eval=False):
        inpt = torch.tensor(input_batch).type('torch.FloatTensor').cuda()
        x = self.fc1(inpt)
        if not eval:
            x = self.bn1(x)
        x = f.relu(x)
        x = self.fc2(x)
        if not eval:
            x = self.bn2(x)
        x = f.relu(x)
        x = self.fc3(x)
        if not eval:
            x = self.bn3(x)
        x = f.relu(x)
        x = self.fc4(x)
        if not eval:
            x = self.bn4(x)
        x = f.relu(x)
        out = self.fc5(x)
        return out

    def get_probs(self,values,invalid):
        rnd = random.uniform(0,1)
        ind = values.index(max(values))
        if rnd > 0.7 and ind not in invalid:
            probs = [1 if x==ind else 0 for x in range(36)]
        else:
            inv = len(invalid)
            p = float(1)/(36-inv)
            probs = [0 if x in invalid else p for x in range(36)]
        return probs

    def next_action(self,input_batch,invalid):
        q_values = self.forward(input_batch,True)
        Qs = q_values.cpu().detach().numpy().tolist()
        ps = self.get_probs(Qs,invalid)
        selected_value = np.random.choice(Qs,p=ps)
        action = Qs.index(selected_value)
=======
        self.fc1 = nn.Linear(input_size,200)
        self.fc2 = nn.Linear(200,128)
        self.fc3 = nn.Linear(128, 64)
        self.fc4 = nn.Linear(64,36)

    def forward(self, input_batch):
        inpt = torch.tensor(input_batch).type('torch.FloatTensor').cuda()
        x = self.fc1(inpt)
        x = f.relu(x)
        x = self.fc2(x)
        x = f.dropout(x,0.4)
        x = self.fc3(x)
        x = f.relu(x)
        out = self.fc4(x)
        return out

    def next_action(self,input_batch):
        q_values = self.forward(input_batch)
        q_values = q_values.detach()
        probs = f.softmax(q_values * 10,0) #T = 7
        action = probs.multinomial(1)
>>>>>>> 72427f0df644fafb7ccb8b52ba875d5a93e03f39
        return action

class Memory:
    def __init__(self,size):
        self.memory = []
        self.size = size

    def save(self,transition):
        if len(self.memory) > self.size:
            self.memory.pop(0)
        self.memory.append(transition)

    def sample(self,batch_size):
        return random.sample(self.memory,batch_size)

class score:
    def __init__(self,size):
        self.size = size
        self.window = []

<<<<<<< HEAD
    def push(self,sc):
        if len(self.window) > self.size:
            self.window.pop(0)
        self.window.append(sc)

    def get_score(self):
        return float(sum(self.window))/len(self.window)

class brain:
    def __init__(self,input_size,actions,size,gamma=0.99):
=======
    def get_score(self):
        return float(sum(self.window))/float(len(self.window)+1)

class brain:
    def __init__(self,input_size,actions,size,gamma=0.7):
>>>>>>> 72427f0df644fafb7ccb8b52ba875d5a93e03f39
        self.net = Network(input_size,actions)
        self.mem = Memory(size)
        self.optimizer = optim.Adam(self.net.parameters(),lr=0.001)
        self.gamma = gamma
        self.moves = 0
        self.scores = score(10000)


    def learn(self,memory_batch):
        self.moves += 1
<<<<<<< HEAD
=======
        self.optimizer.zero_grad()
>>>>>>> 72427f0df644fafb7ccb8b52ba875d5a93e03f39
        mem_batch = np.array(memory_batch)
        st = mem_batch[:,0].tolist()
        actions = torch.tensor(mem_batch[:,3].tolist())
        actions = torch.unsqueeze(actions,0).view(len(actions),1).cuda()
        out = self.net.forward(st).gather(1,actions)
        St = mem_batch[:,1].tolist()
        next_max_out = self.net.forward(St).max(1)[0]
        reward = torch.tensor(mem_batch[:,2].tolist()).type('torch.FloatTensor').cuda()
        target = reward + self.gamma*next_max_out.detach()
        td_loss = f.smooth_l1_loss(torch.squeeze(out,1),target)
<<<<<<< HEAD
        self.optimizer.zero_grad()
        td_loss.backward()
        self.optimizer.step()
        if self.moves >= 100:
            #print list(x.grad for x in  self.net.parameters())
            #print "\n"
            print td_loss.item(),self.scores.get_score()
            #with open("/root/Desktop/loss.txt",'a+') as F:
             #   F.write(str(td_loss.item())+'\n')
            #print "\n"
=======
        td_loss.backward()
        self.optimizer.step()
        if self.moves >= 100:
            print td_loss.item()
>>>>>>> 72427f0df644fafb7ccb8b52ba875d5a93e03f39
            self.moves = 0





