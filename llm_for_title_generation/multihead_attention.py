import torch
import torch.nn as nn

class MultiHeadAttention(nn.Module):
    def __init__(self, d_in: int, d_out: int, context_length: int, dropout: int, num_heads: int, qkv_bias=False):
        super().__init__()
        assert d_out % num_heads == 0 # to strictly check number of output dimentins should be divisible by heads for their equal distribution in all the heads without floating pionts that is not acdeptable.
        self.d_out = d_out
        self.head_dim = d_out // num_heads # to divide output into all heads.
        self.dropout = nn.Dropout(dropout)
        self.context_length = context_length
        self.W_query = nn.Linear(d_in, d_out, bias=qkv_bias)
        self.W_key= nn.Linear(d_in, d_out, bias=qkv_bias)
        self.W_value = nn.Linear(d_in, d_out, bias=qkv_bias)
        self.out_proj = nn.Linear(d_out, d_out) # to save the shape dimentins.
        self.num_heads = num_heads

        self.register_buffer(
            'mask',
            torch.triu(torch.ones(context_length, context_length), diagonal=1)
        )


    def forward(self, x):
        # here x is our input torch tensor batch(embedding of a sentence tokens):
        b, num_tokens, d_in = x.shape
        keys = self.W_key(x)
        queries = self.W_query(x)
        values = self.W_value(x)

        # dividing each matrics into small metrices for splitting into heads:
        keys = keys.view(b, num_tokens, self.num_heads, self.head_dim)
        queries = queries.view(b, num_tokens, self.num_heads, self.head_dim)
        values = values.view(b, num_tokens, self.num_heads, self.head_dim)

        # taking transpose to convert [Batch, Tokens, Heads, Dims] into [Batch, Heads, Tokens, Dims] shape:
        keys = keys.transpose(1, 2)
        queries = queries.transpose(1, 2)
        values = values.transpose(1, 2)

        attn_scores = queries @ keys.transpose(2, 3)
        mask_bool = self.mask.bool()[:num_tokens, :num_tokens]
        attn_scores = attn_scores.masked_fill_(mask_bool, -torch.inf)

        # normalizing each and taking softmax to convert into attn weights:
        attn_weights = torch.softmax(attn_scores / keys.shape[-1]**0.5, dim=-1)
        # droping out:
        attn_weights = self.dropout(attn_weights)

        # transpose back to [batch, tokens, heads, dims]:
        context_vec = (attn_weights @ values).transpose(1, 2)
        context_vec = context_vec.contiguous().view(b, num_tokens, self.d_out) # .contiguous() rearranges it in memory for efficiency before the next .view(). and .view() combine all the small metrices into al large matric back. 2, 6, 4 .
        context_vec = self.out_proj(context_vec) # final check and if needed convert to original shape.
        return context_vec