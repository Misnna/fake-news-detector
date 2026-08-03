"""
Extracts text from an uploaded image (e.g. a screenshot of a news article
or social media post) using EasyOCR — a deep-learning-based OCR engine.

WHY EasyOCR INSTEAD OF TESSERACT: Tesseract is a traditional (non-neural)
OCR engine, tuned mainly for scanned documents with plain black text on a
white background. Real-world screenshots (news app cards, social media
posts) usually have small, colored, stylized text overlaid on busy photo
backgrounds — Tesseract struggles badly with this even after image
preprocessing. EasyOCR uses a neural network (CRAFT for text detection +
a CRNN for recognition) trained on natural scene text, so it handles
this kind of "text on a photo" image far more reliably.

BONUS: EasyOCR is pure Python (installs via pip only) — no separate
system binary to install and configure, unlike Tesseract. Simpler setup.

First run will download the recognition model (~65MB) automatically.
"""
import io

import easyocr
import numpy as np
from PIL import Image

# Loading the model is slow (a few seconds), so we do it once at import
# time and reuse the same reader for every request instead of reloading
# it on every image.
_reader = easyocr.Reader(["en"], gpu=False)


class ImageExtractionError(Exception):
    pass


def extract_text_from_image(file_bytes: bytes) -> str:
    """
    Takes raw image bytes (from an uploaded file) and returns extracted text.
    """
    from .preprocess import extract_nuclear_content

    try:
        image = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    except Exception as e:
        raise ImageExtractionError(f"Could not read image file: {e}")

    try:
        image_array = np.array(image)
        # detail=0 returns just the recognized strings (no bounding boxes);
        # paragraph=True groups nearby text into readable lines/paragraphs
        results = _reader.readtext(image_array, detail=0, paragraph=True)
    except Exception as e:
        raise ImageExtractionError(f"OCR failed: {e}")

    # Join the OCR text blocks with a period and space so that they are treated as separate sentences
    text = ". ".join(results).strip()
    if not text:
        raise ImageExtractionError(
            "No readable text was found in this image. Try a clearer or "
            "higher-resolution screenshot, or paste the text directly instead."
        )

    # Filter out browser bar / phone UI screenshot elements
    filtered = extract_nuclear_content(text)
    if not filtered:
        raise ImageExtractionError(
            "No nuclear safety-related text was found in this image. "
            "Please upload a clearer screenshot of the article, or paste the text directly."
        )
    return filtered
