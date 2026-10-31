import torch.nn as nn 

class StutterCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )
        self.fc = nn.Sequential(
            nn.Flatten(),
            nn.AdaptiveAvgPool2d(1)
        )
        
        self.pool = nn.AdaptiveAvgPool2d(1)
        self.out = nn.Linear(32,1)
    
    def forward(self, x):
        x = self.conv(x)
        x = self.pool(x)
        x = x.flatten(1)
        x = self.out(x)
        