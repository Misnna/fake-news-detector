"""
Evaluates the trained model against data/holdout_test.csv — a small,
HAND-WRITTEN test set that uses completely different phrasing than the
training templates. This gives a much more honest picture of real-world
generalization than the automatic train/test split (which draws from the
same template pool and will often show inflated ~100% accuracy).

Usage:
    python -m src.evaluate_holdout --model_dir saved_model/final
"""
import argparse

import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix

from src.inference import FakeNewsDetector


def main(model_dir: str, config_path: str, holdout_csv: str):
    detector = FakeNewsDetector(model_dir, config_path)
    df = pd.read_csv(holdout_csv)

    preds = []
    for _, row in df.iterrows():
        result = detector.predict(row["statement"], row.get("source", ""))
        pred_label = 0 if result["classifier_prediction"] == "Fake" else 1
        preds.append(pred_label)

    y_true = df["label"].tolist()

    print(f"\nHold-out set size: {len(df)} (statements never seen during training, "
          f"different phrasing than the training templates)\n")
    print(classification_report(y_true, preds, target_names=["Fake", "Real"]))
    print("Confusion matrix (rows=actual, cols=predicted):")
    print(confusion_matrix(y_true, preds))

    print("\nMisclassified examples:")
    for i, (t, p) in enumerate(zip(y_true, preds)):
        if t != p:
            print(f"  - Actual: {'Real' if t==1 else 'Fake'} | Predicted: {'Real' if p==1 else 'Fake'} "
                  f"| Text: {df.iloc[i]['statement'][:90]}...")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_dir", type=str, default="saved_model/final")
    parser.add_argument("--config", type=str, default="config.yaml")
    parser.add_argument("--holdout_csv", type=str, default="data/holdout_test.csv")
    args = parser.parse_args()
    main(args.model_dir, args.config, args.holdout_csv)
