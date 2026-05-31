import torch
import torch.nn as nn

class LayerNormalization(nn.Module):
    def __init__(self, emb_dim):
        super().__init__()
        self.esp = 1e-5
        self.scale = nn.Parameter(torch.ones(emb_dim))
        self.shift = nn.Parameter(torch.zeros(emb_dim))


    def forward(self, x):
        mean = x.mean(dim=-1, keepdim=True)
        var = x.var(dim=-1, keepdim=True, unbiased=False)
        norm_x = (x - mean) / torch.sqrt(var + self.esp)
        return self.scale * norm_x + self.shift