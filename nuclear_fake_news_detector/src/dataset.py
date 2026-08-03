"""
Loads the CSV, cleans it, splits into train/val/test, and wraps it in a
torch Dataset compatible with HuggingFace's Trainer.
"""
import pandas as pd
import torch
from torch.utils.data import Dataset
from sklearn.model_selection import train_test_split

from .preprocess import clean_dataframe


class NewsDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=256):
        self.texts = list(texts)
        self.labels = list(labels)
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        encoding = self.tokenizer(
            self.texts[idx],
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt",
        )
        item = {k: v.squeeze(0) for k, v in encoding.items()}
        item["labels"] = torch.tensor(self.labels[idx], dtype=torch.long)
        return item


def load_and_split(config):
    df = pd.read_csv(config["data"]["raw_csv"])
    text_col = config["data"]["text_column"]
    label_col = config["data"]["label_column"]

    df = clean_dataframe(df, text_col)

    train_df, temp_df = train_test_split(
        df,
        test_size=config["data"]["test_size"] + config["data"]["val_size"],
        stratify=df[label_col],
        random_state=config["training"]["seed"],
    )
    relative_val = config["data"]["val_size"] / (
        config["data"]["test_size"] + config["data"]["val_size"]
    )
    val_df, test_df = train_test_split(
        temp_df,
        test_size=1 - relative_val,
        stratify=temp_df[label_col],
        random_state=config["training"]["seed"],
    )

    return train_df.reset_index(drop=True), val_df.reset_index(drop=True), test_df.reset_index(drop=True)
