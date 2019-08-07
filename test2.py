import torch.nn as nn
import torch.nn.functional as f
import torch
from Network import brain
import random as r

mynet = brain(36,36,0)
mynet.net.cuda()
mynet.load('/root/chain.')
mynet.net.eval()