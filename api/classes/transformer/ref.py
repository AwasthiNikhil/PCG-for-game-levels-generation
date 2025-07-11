import os
import numpy as np
path = '/content/drive/MyDrive/TheVGLC-master/Lode Runner/Processed'
# Load level files
levels = []
for filename in os.listdir(path):
    if filename.endswith(".txt"):
        with open(os.path.join(path, filename)) as f:
            grid = [line.strip() for line in f.readlines()]
            levels.append(grid)

# Flatten grid into a sequence
flattened_levels = [''.join(row for row in level) for level in levels]


from collections import Counter

# Create character vocabulary
all_text = ''.join(flattened_levels)
chars = sorted(set(all_text))
char2idx = {c: i for i, c in enumerate(chars)}
idx2char = {i: c for c, i in char2idx.items()}
vocab_size = len(chars)

seq_length = 100  

sequences = []
targets = []

for text in flattened_levels:
    for i in range(len(text) - seq_length):
        seq = [char2idx[c] for c in text[i:i + seq_length]]
        tgt = char2idx[text[i + seq_length]]
        sequences.append(seq)
        targets.append(tgt)

import torch
import torch.nn as nn

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
from torch.utils.data import DataLoader, Dataset

class LevelDataset(Dataset):
    def __init__(self, sequences, targets):
        self.x = torch.tensor(sequences, dtype=torch.long)
        self.y = torch.tensor(targets, dtype=torch.long)

    def __len__(self):
        return len(self.x)

    def __getitem__(self, idx):
        return self.x[idx], self.y[idx]

train_dataset = LevelDataset(sequences, targets)
train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)

model = LevelTransformer(vocab_size)

import torch.optim as optim

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = model.to(device)
# optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)
# optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
optimizer = torch.optim.Adam(model.parameters(), lr=5e-5)

criterion = nn.CrossEntropyLoss()

for epoch in range(10):
    total_loss = 0
    model.train()
    for x, y in train_loader:
        x, y = x.to(device), y.to(device)
        optimizer.zero_grad()
        out = model(x)
        loss = criterion(out, y)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    print(f"Epoch {epoch+1} Loss: {total_loss:.4f}")



def generate_transformer(model, start_seq, length, bias_weights=None):
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

import random
import numpy as np
import torch

def set_seed(seed = None):
    if seed is None:
        seed = np.random.choice(2 ** 32)
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

# Convert seed number into a tile string pattern
def seed_to_prompt(seed, length=38):
    rng = random.Random(seed)
    tiles = list(char2idx.keys())
    return ('.'*length)


#lode runner
set_seed()
prompt = seed_to_prompt(2)
generated_level = generate_transformer(model, prompt, length=760-38)
generated_level
# Save weights only (recommended)
torch.save(model.state_dict(), "transformer_levelgen_loderunner.pt")
import pickle

# Save
with open("char_vocab.pkl", "wb") as f:
    pickle.dump((char2idx, idx2char), f)

### here
