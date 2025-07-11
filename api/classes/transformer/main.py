import torch
import numpy as np
import random
import pickle
from torch import nn

# Define the same classes for PositionalEncoding and LevelTransformer as before
class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=512):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float32).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * (-np.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)
        self.register_buffer('pe', pe)

    def forward(self, x):
        return x + self.pe[:, :x.size(1)]


class LevelTransformer(nn.Module):
    def __init__(self, vocab_size, d_model=128, nhead=4, num_layers=4, dim_feedforward=512):
        super(LevelTransformer, self).__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoder = PositionalEncoding(d_model)
        encoder_layer = nn.TransformerEncoderLayer(d_model, nhead, dim_feedforward)
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers)
        self.fc_out = nn.Linear(d_model, vocab_size)

    def forward(self, x):
        x = self.embedding(x) * (x.size(1) ** 0.5)
        x = self.pos_encoder(x)
        x = self.transformer(x)
        return self.fc_out(x[:, -1, :])  # Use last token for prediction


# Utility to generate a new level sequence
def generate_transformer(model, char2idx, idx2char, start_seq, length, seq_length=100, bias_weights=None):
    model.eval()
    input_ids = [char2idx[c] for c in start_seq]
    generated = input_ids[:]

    for _ in range(length):
        x = torch.tensor([generated[-seq_length:]], dtype=torch.long).to(device)
        with torch.no_grad():
            logits = model(x)
            probs = torch.softmax(logits[0], dim=0).cpu().numpy()

        if bias_weights:
            probs = np.array([probs[i] * bias_weights.get(idx2char[i], 1.0) for i in range(len(probs))])
            probs /= probs.sum()

        next_token = np.random.choice(len(probs), p=probs)
        generated.append(next_token)

    return ''.join(idx2char[i] for i in generated)


# Set random seed function for consistency
def set_seed(seed=None):
    if seed is None:
        seed = np.random.choice(2 ** 32)
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


# Load the model and vocabulary files
def load_model_and_vocab(model_path, vocab_path, device):
    # Load the vocab (char2idx, idx2char)
    with open(vocab_path, 'rb') as f:
        char2idx, idx2char = pickle.load(f)

    # Load the model
    model = LevelTransformer(len(char2idx))  # Pass vocab size here
    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))  # Map to CPU
    model.to(device)
    model.eval()

    return model, char2idx, idx2char


# Usage: Load model and generate level
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Paths to the saved files
model_path = 'model.pt'
vocab_path = 'char_vocab.pkl'

# Load the model and vocabulary
model, char2idx, idx2char = load_model_and_vocab(model_path, vocab_path, device=device)

# Set the seed for generation
set_seed(42)  # Or any other seed number

m = 20
n = 20
# Generate a new level
prompt = '.' * n  
generated_level = generate_transformer(model, char2idx, idx2char, prompt, length= m*n-m)

# Display the generated level
print(generated_level)

# Optionally, save the generated level to a file
with open('generated_level.txt', 'w') as f:
    f.write(generated_level)
