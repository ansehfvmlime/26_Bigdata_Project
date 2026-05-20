import torch
from torch import nn

class MyLinear(nn.Module):
    def __init__(self, in_features, out_features):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.weight = nn.Parameter(torch.randn(out_features, in_features))
        self.bias = nn.Parameter(torch.randn(out_features))

    def forward(self, x):
        # x의 shape = (N, in_features)
        N = x.shape[0]
        x_col = x.reshape(N, self.in_features, 1) # (N, in_features, 1)
        y = torch.manual(self.weight, x_col) # (N, out_features, 1)
        y = y.reshape(N, self.out_features)
        return y + self.bias # (N, out_features)