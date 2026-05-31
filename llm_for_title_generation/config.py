from transformers import PretrainedConfig

class GPTConfig(PretrainedConfig):
    model_type = "gpt2"
    
    def __init__(
        self,
        vocab_size=50257,
        context_length=1024,
        emb_dim=1024,
        n_heads=16,
        n_layers=24,
        drop_rate=0.1,
        qkv_bias=True,
        **kwargs
    ):
        self.vocab_size = vocab_size
        self.context_length = context_length
        self.emb_dim = emb_dim
        self.n_heads = n_heads
        self.n_layers = n_layers
        self.drop_rate = drop_rate
        self.qkv_bias = qkv_bias
        
        self.n_positions = context_length
        self.n_embd = emb_dim
        self.n_head = n_heads
        self.n_layer = n_layers
        self.resid_pdrop = drop_rate
        self.embd_pdrop = drop_rate
        
        super().__init__(**kwargs)