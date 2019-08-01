import torch
import torch.nn.functional as f
import torch.nn as nn
import numpy as np
import torch.optim as optim
from torch.autograd import Variable
import random


class Network(nn.Module):

    def __init__(self,input_size,actions):
        super(Network,self).__init__()
        torch.manual_seed(random.randint(0,10))
        self.input_size = input_size
        self.actions = actions
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

    def get_score(self):
        return float(sum(self.window))/float(len(self.window)+1)

class brain:
    def __init__(self,input_size,actions,size,gamma=0.7):
        self.net = Network(input_size,actions)
        self.mem = Memory(size)
        self.optimizer = optim.Adam(self.net.parameters(),lr=0.001)
        self.gamma = gamma
        self.moves = 0
        self.scores = score(10000)


    def learn(self,memory_batch):
        self.moves += 1
        self.optimizer.zero_grad()
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
        td_loss.backward()
        self.optimizer.step()
        if self.moves >= 100:
            print td_loss.item()
            self.moves = 0





