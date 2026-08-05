"""
Fine-tunes a transformer (default: roberta-base) on the nuclear-safety
fake news dataset.

Usage:
    python -m src.train --config config.yaml

To try a different backbone for higher accuracy, just change
`model.name` in config.yaml to e.g. "roberta-large" or
"microsoft/deberta-v3-base" — no code changes needed.
"""
import argparse
import os
import random

import numpy as np
import torch
import yaml
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.utils.class_weight import compute_class_weight
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
    EarlyStoppingCallback,
)

from src.dataset import NewsDataset, load_and_split


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    acc = accuracy_score(labels, preds)
    precision, recall, f1, _ = precision_recall_fscore_support(
        labels, preds, average="binary", zero_division=0
    )
    return {"accuracy": acc, "precision": precision, "recall": recall, "f1": f1}


class WeightedTrainer(Trainer):
    """Trainer with class-weighted loss — helps a lot if your real dataset
    ends up imbalanced (fake news datasets often are)."""

    def __init__(self, *args, class_weights=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.class_weights = class_weights

    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs.logits
        weight = self.class_weights.to(logits.device) if self.class_weights is not None else None
        loss_fct = torch.nn.CrossEntropyLoss(
            weight=weight,
            label_smoothing=self.args.label_smoothing_factor or 0.0,
        )
        loss = loss_fct(logits.view(-1, model.config.num_labels), labels.view(-1))
        return (loss, outputs) if return_outputs else loss


def main(config_path: str):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    set_seed(config["training"]["seed"])

    print("Loading and splitting data...")
    train_df, val_df, test_df = load_and_split(config)
    print(f"Train: {len(train_df)} | Val: {len(val_df)} | Test: {len(test_df)}")

    text_col = config["data"]["text_column"]
    label_col = config["data"]["label_column"]

    print(f"Loading tokenizer/model: {config['model']['name']}")
    try:
        tokenizer = AutoTokenizer.from_pretrained(config["model"]["name"], use_fast=False)
    except Exception:
        from transformers import DebertaV2Tokenizer
        tokenizer = DebertaV2Tokenizer.from_pretrained(config["model"]["name"])
    model = AutoModelForSequenceClassification.from_pretrained(
        config["model"]["name"], num_labels=config["model"]["num_labels"]
    )
    if not torch.cuda.is_available():
        model = model.float()

    # Freeze/unfreeze backbone encoder parameters to prevent overfitting while allowing domain adaptation
    unfreeze_layers = config["model"].get("unfreeze_top_layers", 0)

    if hasattr(model, "roberta"):
        print("Freezing RoBERTa encoder backbone layers...")
        for param in model.roberta.parameters():
            param.requires_grad = False
        if unfreeze_layers > 0:
            print(f"Unfreezing top {unfreeze_layers} RoBERTa encoder layers + pooler...")
            if hasattr(model.roberta, "pooler") and model.roberta.pooler is not None:
                for param in model.roberta.pooler.parameters():
                    param.requires_grad = True
            for layer in model.roberta.encoder.layer[-unfreeze_layers:]:
                for param in layer.parameters():
                    param.requires_grad = True
    elif hasattr(model, "deberta"):
        print("Freezing DeBERTa encoder backbone layers...")
        for param in model.deberta.parameters():
            param.requires_grad = False
        if unfreeze_layers > 0:
            print(f"Unfreezing top {unfreeze_layers} DeBERTa encoder layers...")
            if hasattr(model.deberta, "pooler") and model.deberta.pooler is not None:
                for param in model.deberta.pooler.parameters():
                    param.requires_grad = True
            encoder_layers = getattr(model.deberta.encoder, "layer", getattr(model.deberta.encoder, "layers", []))
            for layer in encoder_layers[-unfreeze_layers:]:
                for param in layer.parameters():
                    param.requires_grad = True
    elif hasattr(model, "bert"):
        print("Freezing BERT encoder backbone layers...")
        for param in model.bert.parameters():
            param.requires_grad = False
        if unfreeze_layers > 0:
            print(f"Unfreezing top {unfreeze_layers} BERT encoder layers + pooler...")
            if hasattr(model.bert, "pooler") and model.bert.pooler is not None:
                for param in model.bert.pooler.parameters():
                    param.requires_grad = True
            for layer in model.bert.encoder.layer[-unfreeze_layers:]:
                for param in layer.parameters():
                    param.requires_grad = True

    train_ds = NewsDataset(train_df[text_col], train_df[label_col], tokenizer, config["model"]["max_length"])
    val_ds = NewsDataset(val_df[text_col], val_df[label_col], tokenizer, config["model"]["max_length"])
    test_ds = NewsDataset(test_df[text_col], test_df[label_col], tokenizer, config["model"]["max_length"])

    class_weights = compute_class_weight(
        class_weight="balanced",
        classes=np.unique(train_df[label_col]),
        y=train_df[label_col],
    )
    class_weights = torch.tensor(class_weights, dtype=torch.float)
    print(f"Class weights: {class_weights.tolist()}")

    args = TrainingArguments(
        output_dir=config["training"]["output_dir"],
        num_train_epochs=config["training"]["num_train_epochs"],
        per_device_train_batch_size=config["training"]["train_batch_size"],
        per_device_eval_batch_size=config["training"]["eval_batch_size"],
        learning_rate=float(config["training"]["learning_rate"]),
        weight_decay=config["training"]["weight_decay"],
        warmup_ratio=config["training"]["warmup_ratio"],
        label_smoothing_factor=config["training"]["label_smoothing_factor"],
        fp16=config["training"]["fp16"] and torch.cuda.is_available(),
        eval_strategy="epoch",
        save_strategy="epoch",
        logging_steps=10,
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        greater_is_better=True,
        save_total_limit=2,
        report_to="none",
        seed=config["training"]["seed"],
    )

    trainer = WeightedTrainer(
        model=model,
        args=args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        compute_metrics=compute_metrics,
        class_weights=class_weights,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=config["training"]["early_stopping_patience"])],
    )

    print("Starting training...")
    trainer.train()

    print("\nEvaluating on held-out test set...")
    test_results = trainer.evaluate(test_ds)
    print(test_results)

    final_dir = os.path.join(config["training"]["output_dir"], "final")
    os.makedirs(final_dir, exist_ok=True)
    trainer.save_model(final_dir)
    tokenizer.save_pretrained(final_dir)
    print(f"\nModel saved to {final_dir}")

    with open(os.path.join(final_dir, "test_metrics.txt"), "w") as f:
        f.write(str(test_results))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="config.yaml")
    args = parser.parse_args()
    main(args.config)
