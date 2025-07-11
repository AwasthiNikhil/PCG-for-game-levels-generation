import torch
import numpy as np
import random
import pickle
from os.path import join
from torch import nn
from ..settings import WALL_CHAR

class LevelTransformerGenerator:
    def __init__(self, grid, model_path = join('classes','transformer','model.pt'), vocab_path = join('classes','transformer','char_vocab.pkl'), device=None, width = 20, height = 20):
        # Load the model and vocab
        self.grid = grid
        self.width = width
        self.height = height
        self.device = device or torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model, self.char2idx, self.idx2char = self.load_model_and_vocab(model_path, vocab_path)

    def load_model_and_vocab(self, model_path, vocab_path):
        # Load the vocab (char2idx, idx2char)
        with open(vocab_path, 'rb') as f:
            char2idx, idx2char = pickle.load(f)

        # Load the model
        model = LevelTransformer(len(char2idx))  # Pass vocab size here
        model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu'), weights_only=False))  # Explicitly set weights_only=False
        model.to(self.device)
        model.eval()

        return model, char2idx, idx2char

    def generate(self, seed=None):
        # Generate a level using the transformer model
        prompt = '.' * self.width  # Starting sequence
        input_ids = [self.char2idx[c] for c in prompt]
        generated = input_ids[:]

        for _ in range(self.width * self.height - len(prompt)):
            x = torch.tensor([generated[-100:]], dtype=torch.long).to(self.device)  # Using last 100 tokens
            with torch.no_grad():
                logits = self.model(x)
                probs = torch.softmax(logits[0], dim=0).cpu().numpy()

            next_token = np.random.choice(len(probs), p=probs)
            generated.append(next_token)

        # Convert generated tokens back to characters
        generated_str = ''.join(self.idx2char[i] for i in generated)

        # Replace 'b' and 'B' with '1', all other characters with '2'
        transformed_str = ''.join('2' if ch in ['b', 'B'] else '1' for ch in generated_str)

        # Create a new grid with added boundaries
        new_width = self.width + 2  # Add 1 unit for the left and right boundaries
        new_height = self.height + 2  # Add 1 unit for the top and bottom boundaries
        
        # Create an empty grid with the new size
        new_grid = [['2' for _ in range(new_width)] for _ in range(new_height)]

        # Place the transformed level in the center (leaving space for the boundary)
        idx = 0
        for row in range(1, new_height - 1):
            for col in range(1, new_width - 1):
                new_grid[row][col] = transformed_str[idx]
                idx += 1

        # Add boundary (WALL_CHAR) around the grid
        for x in range(new_width):
            new_grid[0][x] = WALL_CHAR  # Top boundary
            new_grid[new_height - 1][x] = WALL_CHAR  # Bottom boundary

        for y in range(new_height):
            new_grid[y][0] = WALL_CHAR  # Left boundary
            new_grid[y][new_width - 1] = WALL_CHAR  # Right boundary

        # Update the grid to the new grid with boundaries
        self.grid.grid = new_grid
        

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
