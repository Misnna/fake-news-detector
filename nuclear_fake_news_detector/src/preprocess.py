"""
Text cleaning / preprocessing utilities for the fake-news classifier.

RoBERTa's tokenizer handles most raw text well, so we deliberately keep
preprocessing LIGHT — aggressive cleaning (stopword removal, stemming,
lowercasing) actually HURTS transformer models because it destroys
information the pretrained model relies on (casing, punctuation cues
like "!!!", etc., which are themselves fake-news signals).
"""
import re
import html


URL_RE = re.compile(r"https?://\S+|www\.\S+")
MENTION_RE = re.compile(r"@\w+")
MULTI_SPACE_RE = re.compile(r"\s+")
MULTI_PUNCT_RE = re.compile(r"([!?.]){3,}")


def clean_text(text: str) -> str:
    """Light cleaning: unescape HTML entities, strip URLs/mentions,
    collapse whitespace, cap repeated punctuation (keeps the signal
    that repeated '!!!' is a red flag, without letting it blow up
    tokenization)."""
    if not isinstance(text, str):
        return ""
    text = html.unescape(text)
    text = URL_RE.sub(" [URL] ", text)
    text = MENTION_RE.sub(" [MENTION] ", text)
    text = MULTI_PUNCT_RE.sub(r"\1\1\1", text)  # cap at 3 repeats
    text = MULTI_SPACE_RE.sub(" ", text).strip()
    return text


def clean_dataframe(df, text_column: str):
    df = df.copy()
    df[text_column] = df[text_column].apply(clean_text)
    df = df[df[text_column].str.len() > 0]
    df = df.drop_duplicates(subset=[text_column])
    return df.reset_index(drop=True)


NUCLEAR_KEYWORDS = {
    "nuclear", "reactor", "radiation", "radiological", "sievert", "becquerel",
    "leak", "meltdown", "criticality", "fukushima", "chernobyl", "iaea",
    "nrc", "onr", "safety", "contamination", "enrichment", "uranium", "plutonium",
    "cooling", "generator", "waste", "plant", "fission", "millisievert", 
    "microsievert", "hinkley", "sizewell", "torness", "heysham", "dungeness",
    "vogtle", "diablo", "bruce", "kashiwazaki", "cattenom", "wylfa", "hunterston",
    "oldbury", "sellafield", "paks", "tepco", "edf"
}

def extract_nuclear_content(text: str) -> str:
    """
    Filters the text to keep only sentences/paragraphs that contain nuclear-safety
    specific domain terms. Discards menus, ads, cookie banners, and OCR page headers.
    """
    if not isinstance(text, str) or not text.strip():
        return ""
        
    # Split text into sentences
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
    filtered = []
    
    for sent in sentences:
        sent_clean = sent.strip()
        if not sent_clean:
            continue
        words = set(re.findall(r'[a-z]+', sent_clean.lower()))
        if words & NUCLEAR_KEYWORDS:
            filtered.append(sent_clean)
            
    if filtered:
        return " ".join(filtered)
    
    # Fallback to the first three sentences if no keyword matches found
    return " ".join([s.strip() for s in sentences[:3] if s.strip()])
