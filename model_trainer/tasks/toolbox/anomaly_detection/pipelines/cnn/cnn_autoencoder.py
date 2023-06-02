from torch import nn 
import torch.nn.functional as F

class Encoder(nn.Module):
    def __init__(self, latent_dims):
        super().__init__()
        self.conv1 = nn.Conv1d(1, 16, 7, stride=3) # Size of each channel: (205-7)/3+1=67
        self.conv2 = nn.Conv1d(16, 32, 7, stride=3)# Size of each channel: (67-7)/3+1=21
        
        self.fc1 = nn.Linear(672, latent_dims)
        
        self.dropout = nn.Dropout(p=0.6)

    def forward(self, x):
        x = x.view(-1,1,205)
        x = F.relu(self.dropout(self.conv1(x)))
        x = F.relu(self.dropout(self.conv2(x)))
        
        x = x.view(-1,672)
        
        x = self.fc1(x)
        
        return x

class Decoder(nn.Module):
    def __init__(self, latent_dims):
        super().__init__()
        self.fc1 = nn.Linear(latent_dims, 672)
        self.convt1 = nn.ConvTranspose1d(32, 16, kernel_size=7, stride=3)
        self.convt2 = nn.ConvTranspose1d(16, 1, kernel_size=7, stride=3)
        
        self.dropout = nn.Dropout(p=0.4)
        

    def forward(self, z):
        z = F.relu(self.dropout(self.fc1(z)))
        
        z = z.view(-1,32,21)
        z = F.relu(self.convt1(z))
        z = self.convt2(z)
        z = z.view(-1,205)
        return z

class Autoencoder(nn.Module):
    def __init__(self, latent_dims):
        super().__init__()
        self.encoder = Encoder(latent_dims)
        self.decoder = Decoder(latent_dims)

    def forward(self, x):
        z = self.encoder(x)
        return self.decoder(z)