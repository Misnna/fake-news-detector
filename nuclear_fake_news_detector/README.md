# UK Nuclear Power Safety Verification Framework

An ensemble decision-support platform designed to verify news statements regarding UK nuclear power station safety (*Hinkley Point C, Sizewell B/C, Torness, Heysham 1/2, Dungeness B, Sellafield, Hunterston B, Wylfa*) into **Real**, **Fake**, **Not Related to Nuclear Power**, or **Insufficient Verification Data**.

The prediction engine pairs a fine-tuned sequence classifier with a transparent **0–100 Multi-Factor Trust Engine** combining domain model confidence, source credibility rankings, regulatory incident corroboration (UK ONR & IAEA IEC compliance), sentiment neutrality metrics, and domain relevance filtering.

The web platform accepts **3 input modalities**: raw article text, news URLs (with automated HTML parsing), and news graphics/screenshots (via deep-learning EasyOCR).

---

## 1. Core Architectural Pipeline

```
                                  ┌──────────────────────────┐
                                  │      Input Modality      │
                                  └────────────┬─────────────┘
                                               │
                       ┌───────────────────────┼───────────────────────┐
                       ▼                       ▼                       ▼
                [ Raw Text ]            [ Article URL ]        [ News Image / Graphic ]
                       │                       │                       │
                       │             Scraper / Headless HTML           │
                       │                       │                EasyOCR (PyTorch)
                       │                       │                       │
                       └───────────────────────┼───────────────────────┘
                                               │
                                               ▼
                                   ┌───────────────────────┐
                                   │  Domain Relevance     │
                                   │  & Text Preprocessing │
                                   └───────────┬───────────┘
                                               │
                       ┌───────────────────────┴───────────────────────┐
                       ▼                                               ▼
     ┌───────────────────────────────────┐           ┌───────────────────────────────────┐
     │  Transformer Sequence Classifier  │           │   Multi-Factor Trust Score Engine │
     │    (RoBERTa / DeBERTa Fine-tuned) │           │    (Source, Corroboration, Tone) │
     └─────────────────┬─────────────────┘           └─────────────────┬─────────────────┘
                       │                                               │
                       └───────────────────────┬───────────────────────┘
                                               │
                                               ▼
                                ┌─────────────────────────────┐
                                │   Multi-Factor Ensemble     │
                                │   Classification & Scoring  │
                                └─────────────────────────────┘
```

---

## 2. Key Technical Features

1. **Domain Relevance & Non-Nuclear Filtering**: Detects whether incoming news text concerns nuclear power/energy. Out-of-domain articles (such as general sports or politics) are labeled **"Not Related to Nuclear Power"**.
2. **UK Nuclear UI Emblem**: The web interface features an emblem combining the UK Union Jack badge and atomic reactor trefoil.
3. **Domain Adaptation Transfer Learning**: Sequence classifiers fine-tuned on UK nuclear safety claims (Hinkley Point C, Sizewell B/C, Torness, Heysham, Sellafield).
4. **Deep OCR Image Extraction**: Uses EasyOCR (PyTorch + OpenCV) for text extraction from social media infographics and screenshot graphics.
5. **Honest Uncertainty Handling**: Prevents false positives on uncorroborated safety news by flagging non-alarmist unverified statements as **"Insufficient Verification Data"** (Trust Score 50–65/100).
6. **Regulatory Compliance Scope**:
   - **IAEA Incident and Emergency Centre (IEC)** bulletins
   - **UK & International Regulators**: UK Office for Nuclear Regulation (ONR), UKAEA, DESNZ, US NRC
   - **Radiation Monitoring Networks**: EURDEP, EPA RadNet
   - **Fact-Checking Archives**: Full Fact UK, Snopes, PolitiFact

---

## 3. Project Structure

```
nuclear_fake_news_detector/
├── app.py                      # Flask Web UI (UK Nuclear Power Station Emblem Branding)
├── config.yaml                 # System Hyperparameters & Model Configuration
├── requirements.txt            # Python Dependencies
├── data/
│   ├── sample_dataset.csv      # Fine-tuning dataset (670+ UK & IAEA nuclear safety claims)
│   └── holdout_test.csv        # Independent generalization test dataset
├── scripts/
│   ├── generate_sample_dataset.py # Synthetic & template data generation script
│   └── test_integration.py     # End-to-end integration tests
├── src/
│   ├── preprocess.py           # Text normalization and token sanitization
│   ├── dataset.py              # PyTorch Dataset construction and stratified splits
│   ├── train.py                # Fine-tuning script with WeightedTrainer & early stopping
│   ├── evaluate.py             # Classification evaluation & metrics summary
│   ├── evaluate_holdout.py     # Independent holdout generalization evaluation
│   ├── trust_score.py          # Multi-Factor Trust Score Calculation Engine
│   ├── image_extractor.py      # EasyOCR image text extraction module
│   ├── url_extractor.py        # Web scraping & headless Chrome HTML extractor
│   └── inference.py            # End-to-end prediction library & CLI
└── saved_model/                # Model checkpoint directory
```

---

## 4. Installation & Environment Setup

```bash
# 1. Create and activate Python virtual environment
python3 -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt
```

---

## 5. Model Training & Evaluation

To fine-tune the classifier on the nuclear dataset:

```bash
python -m src.train --config config.yaml
```

To evaluate the fine-tuned model on the independent holdout set:

```bash
python -m src.evaluate_holdout --model_dir saved_model/final
```

---

## 6. Running the Web Platform

Start the Flask application:

```bash
python app.py
```

Navigate to `http://localhost:5000` in your web browser to test verification across text, URL links, and uploaded image screenshots.
