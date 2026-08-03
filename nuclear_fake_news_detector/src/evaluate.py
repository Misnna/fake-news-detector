"""
Standalone evaluation: loads a fine-tuned model + test split, prints a
classification report, and saves a confusion matrix plot.

Usage:
    python -m src.evaluate --config config.yaml --model_dir saved_model/final
"""
import argparse

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import torch
import yaml
from sklearn.metrics import classification_report, confusion_matrix
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from src.dataset import load_and_split


def main(config_path: str, model_dir: str):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_dir, use_fast=False)
    except Exception:
        from transformers import DebertaV2Tokenizer
        tokenizer = DebertaV2Tokenizer.from_pretrained(model_dir)
    model = AutoModelForSequenceClassification.from_pretrained(model_dir).to(device)
    model.eval()

    _, _, test_df = load_and_split(config)
    text_col = config["data"]["text_column"]
    label_col = config["data"]["label_column"]

    all_preds, all_probs = [], []
    with torch.no_grad():
        for text in test_df[text_col].tolist():
            inputs = tokenizer(
                text, truncation=True, padding="max_length",
                max_length=config["model"]["max_length"], return_tensors="pt"
            ).to(device)
            logits = model(**inputs).logits
            probs = torch.softmax(logits, dim=-1).cpu().numpy()[0]
            all_probs.append(probs)
            all_preds.append(int(np.argmax(probs)))

    y_true = test_df[label_col].tolist()
    print(classification_report(y_true, all_preds, target_names=["Fake", "Real"]))

    cm = confusion_matrix(y_true, all_preds)
    plt.figure(figsize=(5, 4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=["Fake", "Real"], yticklabels=["Fake", "Real"])
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title("Confusion Matrix - Test Set")
    plt.tight_layout()
    plt.savefig("confusion_matrix.png", dpi=150)
    print("Saved confusion_matrix.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="config.yaml")
    parser.add_argument("--model_dir", type=str, default="saved_model/final")
    args = parser.parse_args()
    main(args.config, args.model_dir)
