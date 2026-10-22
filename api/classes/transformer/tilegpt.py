"""A small GPT-style model over level tiles, and constrained generation.

This replaces the first transformer (leveltransformergenerator.py) for new
models. That one was built without batch_first=True, so attention ran across
the samples in a batch instead of along the level, and each prediction
depended only on the previous tile. Here:

- attention runs along the sequence, with a causal mask;
- levels are serialised one slice at a time (rows for Lode Runner, columns for
  Super Mario Bros) with an end-of-slice token, so "the next slice" is learnable;
- every tile also gets an embedding for its place in its slice (which row of
  a column, or which column of a row). Without it the model has to count back
  to the last end-of-slice token to know where it is, and with this little
  data it never learns to: it predicted sky where Mario's ground belongs;
- generation forces the end-of-slice token at the right places, so every slice
  has the right length.

Sequences fed to the model always start at a slice boundary, so a tile's place
in its slice is simply its position modulo (slice_len + 1).
"""
import json
import math

import torch
from torch import nn

EOS = '\n'  # end of a row (or column)


class TileGPT(nn.Module):
    def __init__(self, vocab_size, slice_len, context=256, d_model=128, nhead=4, num_layers=4, dim_feedforward=512, dropout=0.1):
        super().__init__()
        self.period = slice_len + 1                       # tiles + end-of-slice token
        self.context = context - context % self.period    # whole slices only
        self.d_model = d_model
        self.tok = nn.Embedding(vocab_size, d_model)
        self.pos = nn.Embedding(self.context, d_model)
        self.slot = nn.Embedding(self.period, d_model)    # place within the slice
        layer = nn.TransformerEncoderLayer(d_model, nhead, dim_feedforward, dropout, batch_first=True, norm_first=True)
        self.blocks = nn.TransformerEncoder(layer, num_layers, enable_nested_tensor=False)
        self.norm = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model, vocab_size)
        self.register_buffer('mask', nn.Transformer.generate_square_subsequent_mask(self.context), persistent=False)

    def forward(self, x):
        """x: (batch, length) token ids, starting at a slice boundary → logits
        (batch, length, vocab) for the next token at every position."""
        n = x.size(1)
        at = torch.arange(n, device=x.device)
        h = self.tok(x) * math.sqrt(self.d_model) + self.pos(at) + self.slot(at % self.period)
        h = self.blocks(h, mask=self.mask[:n, :n], is_causal=True)
        return self.head(self.norm(h))


def load(path_prefix, device='cpu'):
    """Load '<prefix>.pt' and '<prefix>.json' saved by algo/transformer/train_tilegpt.py."""
    with open(path_prefix + '.json') as f:
        cfg = json.load(f)
    model = TileGPT(len(cfg['vocab']), cfg['slice_len'], **cfg['model'])
    model.load_state_dict(torch.load(path_prefix + '.pt', map_location=device, weights_only=True))
    model.to(device).eval()
    return model, cfg


@torch.no_grad()
def sample_slices(model, cfg, count, seed, prompt_slices, temperature=1.0, device='cpu'):
    """Generate `count` slices (rows or columns) after the prompt slices.

    The end-of-slice token is forced every `slice_len` tiles and forbidden
    elsewhere, so every slice comes out exactly `slice_len` long.
    """
    vocab = cfg['vocab']
    idx = {c: i for i, c in enumerate(vocab)}
    eos, length = idx[EOS], cfg['slice_len']
    gen = torch.Generator().manual_seed(seed)
    ids = [idx[c] for s in prompt_slices for c in s + EOS]
    out = []
    while len(out) < count:
        tiles = []
        for _ in range(length):
            # the window must start at a slice boundary: drop whole slices from the front
            start = max(0, len(ids) - model.context)
            start += -start % model.period
            x = torch.tensor([ids[start:]], device=device)
            logits = model(x)[0, -1].float().cpu() / temperature
            logits[eos] = -float('inf')
            nxt = int(torch.multinomial(torch.softmax(logits, -1), 1, generator=gen))
            ids.append(nxt)
            tiles.append(vocab[nxt])
        ids.append(eos)
        out.append(''.join(tiles))
    return out
