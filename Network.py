import torch
import torch.nn.functional as f
import torch.nn as nn
import numpy as np
import torch.optim as optim
from torch.autograd import Variable
import random
import os


class Network(nn.Module):

    def __init__(self,input_size,actions):
        super(Network,self).__init__()
        self.input_size = input_size
        self.actions = actions
        self.fc1 = nn.Linear(input_size,1000)
        self.bn1 = nn.BatchNorm1d(1000)
        self.fc2 = nn.Linear(1000,719)
        self.drop1 = nn.Dropout(0.5)
        self.bn2 = nn.BatchNorm1d(719)
        self.fc3 = nn.Linear(719, 885)
        self.bn3 = nn.BatchNorm1d(885)
        self.fc4 = nn.Linear(885,400)
        self.drop2 = nn.Dropout(0.7)
        self.bn4 = nn.BatchNorm1d(400)
        self.fc5 = nn.Linear(400,211)
        self.bn5 = nn.BatchNorm1d(211)
        self.fc6 = nn.Linear(211,actions)

    def forward(self, input_batch):
        x = self.fc1(input_batch)
        x = self.bn1(x)
        x = self.drop1(x)
        x = f.leaky_relu(x)
        x = self.fc2(x)
        x = self.bn2(x)
        x = f.relu(x)
        x = self.fc3(x)
        x = self.bn3(x)
        x = f.leaky_relu(x)
        x = self.fc4(x)
        x = self.bn4(x)
        x = f.relu(x)
        x = self.fc5(x)
        x = self.drop2(x)
        x = self.bn5(x)
        x = f.leaky_relu(x)
        out = self.fc6(x)
        return out

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

    def push(self,sc):
        if len(self.window) > self.size:
            self.window.pop(0)
        self.window.append(sc)

    def get_score(self):
        if not self.window:
            return 0
        else:
            return sum(self.window)/float(len(self.window))


class brain:
    def __init__(self,input_size,actions,size,gamma=0.95):
        self.net = Network(input_size,actions)
        self.target_net = Network(input_size,actions)
        self.mem = Memory(size)
        self.optimizer = optim.Adam(self.net.parameters(),lr=0.0001)
        self.gamma = gamma
        self.moves = 0
        self.scores = score(10000)
        self.target_net.load_state_dict(self.net.state_dict())
        self.net.to('cuda')
        self.target_net.to('cuda')

    def next_action(self,input_batch,valid,test=True):
        input_batch = torch.tensor(input_batch).unsqueeze(0).type('torch.FloatTensor').cuda()
        self.net.eval()
        valid = torch.tensor(valid).cuda()
        q_values = self.net.forward(input_batch).squeeze(0).gather(0,valid)
        probs = 7 * q_values.softmax(0)
        q_values = q_values.cpu().detach().tolist()
        qval_action = dict(zip(q_values,valid.cpu().tolist()))
        if test:
            mval = max(q_values)
            self.net.train()
            return qval_action[mval]
        ind = probs.multinomial(1)                                #index of selected probability
        value = q_values[ind]                                     #qvalue corrsponding to probability
        action = qval_action[value]                               #action corrsponding to qvalue
        self.net.train()
        return action


    def learn(self,memory_batch):
        self.moves += 1
        mem_batch = np.array(memory_batch)
        st = torch.tensor(mem_batch[:,0].tolist()).type('torch.FloatTensor').cuda()
        actions = torch.tensor(mem_batch[:,3].tolist())
        actions = actions.unsqueeze(0).view(len(actions),1).cuda()
        out = self.net.forward(st).gather(1,actions)
        St = torch.tensor(mem_batch[:,1].tolist()).type('torch.FloatTensor').cuda()
        next_max_out = self.target_net.forward(St).max(1)[0]
        reward = torch.tensor(mem_batch[:,2].tolist()).type('torch.FloatTensor').cuda()
        target = reward + self.gamma*next_max_out.detach()
        td_loss = f.smooth_l1_loss(torch.squeeze(out,1),target)
        self.optimizer.zero_grad()
        td_loss.backward()
        self.optimizer.step()
        if self.moves % 100 == 0:
            #print list(x.grad for x in  self.net.parameters())
            #print "\n"
            print(self.scores.get_score(),td_loss.item())
            #for p in self.net.parameters():
                #p.data.clamp_(-1,1)
            #with open("/root/Desktop/loss.txt",'a+') as F:
             #   F.write(str(td_loss.item())+'\n')
            #print "\n"
        if self.moves >= 400:
            self.moves = 0
            self.target_net.load_state_dict(self.net.state_dict())
            print("target Updated!")


    def save(self,path):
        torch.save(self.net.state_dict(),path)

    def load(self,path):
        self.net.load_state_dict(torch.load(path))





