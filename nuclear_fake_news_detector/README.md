# NUCLEAR REBUILD

Fine-tunes a **RoBERTa-based classifier** to classify nuclear-safety-related
statements as **Real** or **Fake**, and combines the model's prediction
with a **Dynamic Trust Score** (source credibility + corroboration +
sentiment neutrality + model confidence) — matching the two modules
described in the project abstract. Supports 3 input methods: pasted text,
a news article URL, or an uploaded image (screenshot).

## Key fixes applied for real-world accuracy (changelog)

Earlier versions of this project scored 100% on their own train/test split
but made real-world mistakes (e.g. flagging genuine celebratory news
headlines as fake, failing to read stylized screenshot images). These were
diagnosed and fixed:

1. **Base model upgraded**: now starts from `jy46604790/Fake-News-Bert-Detect`
   (RoBERTa already fine-tuned on 40,000+ real news articles) instead of
   plain `roberta-base`, then further fine-tunes on our nuclear-specific
   data. This gives it a much stronger starting point on real-world
   writing-style diversity before it ever sees our smaller dataset.
2. **Training data expanded** (570 rows, up from the original 260) with
   more varied phrasing, randomized details, and a new category of
   genuine "milestone/achievement" real-news headlines (e.g. "Historic
   milestone: plant achieves first criticality") — specifically to teach
   the model that exciting phrasing doesn't automatically mean fake.
3. **OCR engine switched**: Tesseract → **EasyOCR** (deep-learning based).
   Tesseract failed on stylized screenshots (text over photo backgrounds,
   varying colors); EasyOCR handles this reliably.
4. **URL extractor upgraded**: added a **headless-Chrome fallback**
   (Selenium) for JavaScript-heavy sites that return an empty page to a
   plain HTTP request, plus clearer error messages for sites that
   actively block bots (403) vs. sites that need JS rendering.
5. **Trust Score source-matching bug fixed**: previously `"iaea.org"`
   (auto-detected from a URL) didn't match `"IAEA"` (name-style entry) in
   the credibility list due to exact-string matching — now uses substring
   matching so both styles are recognized correctly.

## 1. Project Structure

```
nuclear_fake_news_detector/
├── app.py                      # Flask demo web UI
├── config.yaml                 # All hyperparameters / weights in one place
├── requirements.txt
├── data/
│   └── sample_dataset.csv      # STARTER dataset (see note below)
├── scripts/
│   └── generate_sample_dataset.py
├── src/
│   ├── preprocess.py           # Light text cleaning
│   ├── dataset.py              # Load, clean, split, PyTorch Dataset
│   ├── train.py                # Fine-tunes RoBERTa (or any HF model)
│   ├── evaluate.py             # Classification report + confusion matrix
│   ├── trust_score.py          # Trust Score module (module 2 of the abstract)
│   └── inference.py            # End-to-end prediction (CLI + library)
└── saved_model/                # Created after training
```

## 2. Setup

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

If you have a CUDA GPU, install the matching PyTorch build from
https://pytorch.org/get-started/locally/ for a large speedup (CPU training
works but is slow for RoBERTa).

## 3. Data — IMPORTANT for hitting >90% accuracy

`data/sample_dataset.csv` is a small, **template-generated** starter set
(260 rows) so the whole pipeline runs end-to-end immediately. Template text
is repetitive, so a model trained only on it will report very high accuracy
on its own test split but **won't generalize to real-world text**. To get a
genuinely strong, defensible >90% result:

1. **Add real data.** Good free sources:
   - Fact-checks: Reuters Fact Check, Full Fact, Snopes (search "nuclear")
   - Official statements: IAEA press releases, UK ONR bulletins, US NRC
     event reports, World Nuclear Association news
   - Known misinformation: documented viral hoaxes about Fukushima,
     Chernobyl anniversaries, etc. (many are catalogued by fact-checkers)
   - General fake-news base rate: combine with a public dataset like
     **LIAR** or **FakeNewsNet** and filter/oversample nuclear-related rows,
     so the model learns general deception patterns, not just nuclear
     vocabulary.
2. Keep the same CSV schema: `statement,source,label` (label: 0=Fake, 1=Real).
3. Aim for at least a few thousand rows, reasonably balanced between
   classes, before trusting the accuracy number.
4. Regenerate/replace `data/sample_dataset.csv` (or point `config.yaml ->
   data.raw_csv` at your new file) and re-run training.

## 4. Train

```bash
python -m src.train --config config.yaml
```

This will:
- Split data into train/val/test (stratified)
- Fine-tune RoBERTa-base with class-weighted loss, label smoothing, warmup,
  and early stopping on F1
- Save the best checkpoint to `saved_model/final/`
- Print/save test-set metrics (accuracy, precision, recall, F1)

**To try a different backbone** (often higher accuracy than RoBERTa-base on
classification benchmarks), just edit one line in `config.yaml`:
```yaml
model:
  name: "microsoft/deberta-v3-base"   # or "roberta-large"
```

## 5. Evaluate

```bash
python -m src.evaluate --config config.yaml --model_dir saved_model/final
```
Prints a full classification report and saves `confusion_matrix.png`.

## 6. Run inference

CLI:
```bash
python -m src.inference --text "BREAKING: plant leak covered up!!!" --source "Anonymous Blog Post"
```

As a library:
```python
from src.inference import FakeNewsDetector
detector = FakeNewsDetector("saved_model/final", "config.yaml")
result = detector.predict("...", source="Reuters")
```

Output includes the classifier's Real/Fake prediction **and** a 0-100 Trust
Score with a breakdown of the four contributing signals and any red flags.

## 7. Web demo

```bash
python app.py
```
Open http://localhost:5000 — the Analyzer page has **3 input modes** (tabs):
- **Paste Text** — paste a statement directly
- **News URL** — paste a link to a news article; the app fetches and extracts
  the article text automatically before analyzing it
- **Upload Image** — upload a screenshot of an article or social media post;
  the app runs OCR (text recognition) to extract the text, then analyzes it

All three modes feed into the same RoBERTa classifier + Trust Score pipeline.

Open http://localhost:5000/batch for the **Batch Accuracy Checker** — upload
a CSV (`statement,source,label` columns) and get an accuracy/precision/
recall/F1 report plus a row-by-row breakdown, right in the browser.

### OCR setup (required for the Upload Image feature)

`pytesseract` is only a Python wrapper — it needs the actual Tesseract OCR
engine installed separately as a system program:

- **Windows**: download and run the installer from
  https://github.com/UB-Mannheim/tesseract/wiki, then either add the
  install folder to your PATH, or set the path explicitly at the top of
  `src/image_extractor.py`:
  ```python
  pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
  ```
- **Mac**: `brew install tesseract`
- **Linux**: `sudo apt-get install tesseract-ocr`

If Tesseract isn't installed, the Upload Image tab shows a clear error
message rather than crashing.

### Note on the URL extractor

`src/url_extractor.py` uses a simple heuristic (grabs all `<p>` tag text)
that works on most standard news sites, but can fail on pages that load
content via JavaScript or actively block automated requests. If a URL
fails to extract, the app shows an error — in that case, copy the article
text manually into the Paste Text tab instead.

## 8. Genuine generalization check (hold-out test)

The automatic train/test split accuracy can look artificially high (close
to 100%) because it's drawn from the same template family as training.
For a more honest check, `data/holdout_test.csv` contains hand-written
examples with completely different phrasing. Run:

```bash
python -m src.evaluate_holdout --model_dir saved_model/final
```

This reports accuracy specifically on unseen phrasing — a much better
signal of real-world generalization.

## 9. Tips for pushing accuracy above 90%

- **More, cleaner, more diverse data** matters far more than model choice.
- Try `roberta-large` or `microsoft/deberta-v3-base` if you have GPU budget.
- Increase `max_length` if your real articles are longer than short claims.
- Use k-fold cross-validation to get a more reliable accuracy estimate than
  a single train/test split.
- Watch for **source leakage**: if "source" strongly predicts the label in
  training data, the model may just memorize source names instead of
  learning language patterns — make sure your source list isn't the same
  in train and test in a way that trivializes the task.
- Log `saved_model/final/test_metrics.txt` after every run so you can track
  what changes actually improved accuracy.

## Notes

- `trust_score.py`'s `check_corroboration()` currently does simple keyword
  overlap against a hardcoded list of reference claims — a stand-in for a
  real corroboration step. For production, replace it with a semantic
  search (sentence-embedding similarity) against a live feed from IAEA/ONR/
  NRC official statements.
- The source credibility list in `trust_score.py` is a small starter
  lookup table — extend it with a maintained media-credibility database
  (e.g. NewsGuard, MediaBiasFactCheck-style ratings) for real use.
