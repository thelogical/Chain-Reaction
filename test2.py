import torch.nn as nn
import torch.nn.functional as f
import torch


class Net(nn.Module):
    def __init__(self,input_size,actions):
        super(Net,self).__init__()
        self.input_size = input_size
        self.actions = actions
        self.fc1 = nn.Linear(input_size,1000)
        self.bn1 = nn.BatchNorm1d(1000)
        self.fc2 = nn.Linear(1000,819)
        self.bn2 = nn.BatchNorm1d(819)
        self.fc3 = nn.Linear(819,552)
        self.bn3 = nn.BatchNorm1d(552)
        self.fc4 = nn.Linear(552,378)
        self.bn4 = nn.BatchNorm1d(378)
        self.fc5 = nn.Linear(378,128)
        self.bn5 = nn.BatchNorm1d(128)
        self.fc6 = nn.Linear(128,64)
        self.bn6 = nn.BatchNorm1d(64)
        self.fc7 = nn.Linear(64,36)

    def forward(self, input_batch):
        x = self.fc1(input_batch)
        x = self.bn1(x)
        x = f.relu(x)
        x = self.fc2(x)
        x = self.bn2(x)
        x = f.relu(x)
        x = self.fc3(x)
        x = self.bn3(x)
        x = f.relu(x)
        x = self.fc4(x)
        x = self.bn4(x)
        x = f.relu(x)
        x = self.fc5(x)
        x = self.bn5(x)
        x = f.relu(x)
        x = self.fc6(x)
        x = self.bn6(x)
        x = f.relu(x)
        out = self.fc7(x)
        return out

mynet = Net(36,36).cuda()
data = torch.randint(-3, 3, (1, 36)).type('torch.FloatTensor').cuda()
print mynet.forward(data).max(1)[1]