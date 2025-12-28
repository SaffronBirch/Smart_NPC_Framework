import pandas as pd
import itertools

import torch
import torch.nn as nn
import torch.optim
from torch.utils.data import TensorDataset, DataLoader, random_split
from torch.nn.utils.rnn import pad_sequence

import torchtext.data
from torchtext.vocab import build_vocab_from_iterator

from lightning.pytorch import LightningModule, Trainer
from torchmetrics import Accuracy


path = '/mnt/c/Users/Saffron/Documents/Ontario Tech Class Notes/Thesis/AI_Powered_Game/Datasets/emotions.csv'
text_column = "text"
label_column = "label"

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load the data as a data frame and map labels to unique IDs.
def load_dataframe(path):
    with open(path, 'r') as f:
        df = pd.read_csv(f)

    df = df[[text_column, label_column]].dropna()
    unique_labels = sorted(df[label_column].unique().tolist())
    label_id = {lab: i for i, lab in enumerate(unique_labels)}
    df[label_column] = df[label_column].map(label_id).astype(int)
    
    return df, label_id

df, label_id = load_dataframe(path)

# DEBUGGING PURPOSES --> REMOVE
num_classes = len(label_id)
print("Num Classes:", num_classes)
print("Label mapping (dataset -> class index):", label_id)


# Tokenize sequences
tokenizer = torchtext.data.get_tokenizer('basic_english')

def iterate_tokens(df):
    for text in df[text_column]:
        yield tokenizer(str(text))

vocab = build_vocab_from_iterator(
    iterate_tokens(df),
    min_freq=5,
    specials=['<unk>', '<s>', '<eos>'])

vocab.set_default_index(0)

# DEBUGGING PURPOSES --> REMOVE
print("Vocab size:", len(vocab))

# Dataset preparation
def get_dataloaders(df, vocab, max_length=250, batch_size=32):
    sequences = [
        torch.tensor(
            vocab.lookup_indices(tokenizer(text), ), 
            dtype=torch.int64)
        for text in df[text_column]]
    
    padded_sequences= pad_sequence(sequences, batch_first=True)[:, :max_length]
    targets = torch.tensor(df[label_column].values, dtype=torch.int64)
    
    dataset = TensorDataset(padded_sequences, targets)
    
    (train_dataset, val_dataset) = random_split(dataset, (0.7, 0.3))

    train_dataloader = DataLoader(train_dataset, shuffle=True, batch_size=batch_size)
    val_dataloader = DataLoader(val_dataset, shuffle=True, batch_size=batch_size)

    return (train_dataloader, val_dataloader)



