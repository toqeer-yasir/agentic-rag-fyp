from transformers import PreTrainedTokenizer
import tiktoken
import json
import os

class TiktokenTokenizer(PreTrainedTokenizer):
    def __init__(self, encoding_name="gpt2", **kwargs):
        # Initialize the encoder first
        self.encoder = tiktoken.get_encoding(encoding_name)
        self._vocab_size = self.encoder.n_vocab
        self.encoding_name = encoding_name
        
        # Set special tokens
        kwargs.update({
            "bos_token": "<|endoftext|>",
            "eos_token": "<|endoftext|>", 
            "pad_token": "<|endoftext|>",
            "unk_token": "<|endoftext|>",
        })
        
        # Call parent initialization
        super().__init__(**kwargs)
        
        # Set token IDs
        try:
            self.bos_token_id = self.encoder.encode_single_token("<|endoftext|>")
            self.eos_token_id = self.encoder.encode_single_token("<|endoftext|>")
            self.pad_token_id = self.encoder.encode_single_token("<|endoftext|>")
            self.unk_token_id = self.encoder.encode_single_token("<|endoftext|>")
        except:
            # Fallback for GPT-2 tokenizer
            self.bos_token_id = 50256
            self.eos_token_id = 50256
            self.pad_token_id = 50256
            self.unk_token_id = 50256

    def get_vocab(self):
        vocab = {}
        for i in range(self._vocab_size):
            try:
                token_bytes = self.encoder.decode_single_token_bytes(i)
                token_str = token_bytes.decode('utf-8', errors='replace')
                vocab[token_str] = i
            except:
                vocab[str(i)] = i
        return vocab

    @property
    def vocab_size(self):
        return self._vocab_size

    def _tokenize(self, text):
        tokens = self.encoder.encode(text)
        token_strings = []
        for token in tokens:
            try:
                token_bytes = self.encoder.decode_single_token_bytes(token)
                token_str = token_bytes.decode('utf-8', errors='replace')
                token_strings.append(token_str)
            except:
                token_strings.append(str(token))
        return token_strings

    def _convert_token_to_id(self, token):
        try:
            if token.isdigit():
                return int(token)
            else:
                return self.encoder.encode_single_token(token)
        except:
            return self.unk_token_id

    def _convert_id_to_token(self, index):
        try:
            token_bytes = self.encoder.decode_single_token_bytes(index)
            return token_bytes.decode('utf-8', errors='replace')
        except:
            return str(index)

    def encode(self, text, **kwargs):
        return self.encoder.encode(text)

    def decode(self, token_ids, **kwargs):
        if isinstance(token_ids, list):
            return self.encoder.decode(token_ids)
        else:
            return self.encoder.decode(token_ids.tolist())

    def save_vocabulary(self, save_directory, filename_prefix=None):
        vocab_file = os.path.join(save_directory, "vocab.json")
        with open(vocab_file, "w") as f:
            json.dump({"encoding_name": self.encoding_name}, f)
        return (vocab_file,)