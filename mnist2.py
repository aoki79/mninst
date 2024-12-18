import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
from sklearn.metrics import accuracy_score

train_dataset = torchvision.datasets.MNIST(root="data", 
                                           train=True, 
                                           transform=torchvision.transforms.ToTensor(), 
                                           download=True)
valid_dataset = torchvision.datasets.MNIST(root="data", 
                                           train=False, 
                                           transform=torchvision.transforms.ToTensor(), 
                                           download=True)

batch_size = 64
train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
valid_loader = torch.utils.data.DataLoader(valid_dataset, batch_size=batch_size, shuffle=False)

class MyModel(nn.Module): 
  def __init__(self, input_size):
    super(MyModel, self).__init__()
    self.size = input_size*input_size
    self.fc1 = nn.Linear(self.size, 1024)
    self.fc2 = nn.Linear(1024, 256)
    self.fc3 = nn.Linear(256, 10)
  def forward(self, x):
    x = x.view(-1, self.size)
    x = F.relu(self.fc1(x))
    x = F.relu(self.fc2(x))
    x = self.fc3(x)
    return x
  
device = "cuda" if torch.cuda.is_available() else "cpu"
model = MyModel(28).to(device)
model

criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

def train(model,device,loader,criterion,optimizer):
  model.train()
  tot_loss=0.0
  tot_score=0.0
  for image,label in tqdm(loader,desc="train"):
    image,label=image.to(device),label.to(device)

    optimizer.zero_grad()
    outputs=model(image)
    loss=criterion(outputs,label)
    loss.backward()
    optimizer.step()
    tot_loss+=loss.detach().item()
    tot_score+=accuracy_score(label.cpu(),outputs.argmax(dim=1).cpu())

  tot_loss/=len(loader)
  tot_score/=len(loader)
  return tot_loss,tot_score
  
def valid(model,device,loader,criterion):
  model.eval()
  tot_loss=0.0
  tot_score=0.0
  for image,label in tqdm(loader,desc="valid"):
    image,label=image.to(device),label.to(device)

    outputs=model(image)
    loss=criterion(outputs,label)
    tot_loss+=loss.detach().item()
    tot_score+=accuracy_score(label.cpu(),outputs.argmax(dim=1).cpu())

  tot_loss/=len(loader)
  tot_score/=len(loader)
  return tot_loss,tot_score
  
for epoch in range(5):
   print(f'epoch[{epoch+1}]')
   train_loss,train_acc=train(model,device,train_loader,criterion,optimizer)
   valid_loss, valid_acc = valid(model, device, valid_loader, criterion)
   print(f"--> train loss {train_loss}, train accuracy {train_acc}, valid loss {valid_loss} valid accuracy {valid_acc}")
   