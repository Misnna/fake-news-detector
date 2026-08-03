"""
End-to-end inference: text (+ optional source) -> classification + Trust Score.

Usage as a library:
    from src.inference import FakeNewsDetector
    detector = FakeNewsDetector("saved_model/final", "config.yaml")
    result = detector.predict("Some nuclear safety claim...", source="Reuters")
    print(result)

Usage as a CLI:
    python -m src.inference --text "..." --source "Reuters"
"""
import argparse

import torch
import yaml
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from src.preprocess import clean_text
from src.trust_score import compute_trust_score


class FakeNewsDetector:
    def __init__(self, model_dir: str = "saved_model/final", config_path: str = "config.yaml"):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        # Restrict PyTorch to 1 CPU thread to preserve RAM on 512MB environments (like Render Free)
        torch.set_num_threads(1)
        self.device = "cpu"
        self.max_length = self.config["model"].get("max_length", 128)
        self.weights = self.config["trust_score"]
        self.model = None
        self.tokenizer = None
        self.use_fallback = False

        import os
        target_dir = model_dir if os.path.exists(model_dir) else self.config["model"]["name"]

        try:
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(target_dir, use_fast=True)
            except Exception:
                from transformers import DebertaV2Tokenizer
                self.tokenizer = DebertaV2Tokenizer.from_pretrained(target_dir)

            self.model = AutoModelForSequenceClassification.from_pretrained(
                target_dir, low_cpu_mem_usage=True
            ).to(self.device)
            self.model.eval()
        except Exception as e:
            print(f"[Warning] Could not load Transformer model ({e}). Using lightweight Trust-Score fallback.")
            self.use_fallback = True

    def predict(self, text: str, source: str = ""):
        cleaned = clean_text(text)
        prob_real = 0.5
        prob_fake = 0.5

        if not self.use_fallback and self.model is not None and self.tokenizer is not None:
            try:
                inputs = self.tokenizer(
                    cleaned, truncation=True, padding=True,
                    max_length=self.max_length, return_tensors="pt"
                ).to(self.device)

                with torch.no_grad():
                    logits = self.model(**inputs).logits
                    probs = torch.softmax(logits, dim=-1).cpu().numpy()[0]
                    prob_fake = float(probs[0])
                    prob_real = float(probs[1])
            except Exception as e:
                print(f"[Warning] Model prediction failed: {e}. Falling back to trust score heuristics.")

        predicted_label = "Real" if prob_real >= prob_fake else "Fake"

        trust_result = compute_trust_score(
            text=cleaned,
            model_confidence_real=prob_real,
            source=source,
            weights=self.weights,
        )

        return {
            "text": text,
            "source": source,
            "classifier_prediction": predicted_label,
            "classifier_confidence": {"real": round(prob_real, 4), "fake": round(prob_fake, 4)},
            "trust_score_result": trust_result.to_dict(),
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", type=str, required=True)
    parser.add_argument("--source", type=str, default="")
    parser.add_argument("--model_dir", type=str, default="saved_model/final")
    parser.add_argument("--config", type=str, default="config.yaml")
    args = parser.parse_args()

    detector = FakeNewsDetector(args.model_dir, args.config)
    result = detector.predict(args.text, args.source)

    import json
    print(json.dumps(result, indent=2))
