"""
Dynamic Trust Score Calculation module (per the project abstract).

Combines four signals into one 0-100 Trust Score:
  1. Model confidence      — RoBERTa classifier's predicted probability of "Real"
  2. Source credibility    — lookup table of known credible/non-credible outlets
  3. Corroboration         — simple keyword overlap against a small set of
                              "official" reference statements (stand-in for a
                              real fact-database / IAEA-ONR API integration)
  4. Sentiment neutrality  — penalizes highly emotional/sensational language,
                              which correlates with misinformation

This is intentionally modular: swap `check_corroboration()` for a real call
to an official nuclear safety authority API/database, and swap the source
list for a maintained credibility database, without touching the rest of
the pipeline.
"""
import re
from dataclasses import dataclass, field
from typing import List

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_sentiment_analyzer = SentimentIntensityAnalyzer()

# --- Source credibility lookup (extend this with a real, maintained list) ---
# Includes both display names (from manual "Source" field entries) and raw
# domains (auto-detected from URLs, e.g. "iaea.org", "reuters.com") so both
# input styles get matched correctly.
HIGH_CREDIBILITY_SOURCES = {
    "reuters", "reuters.com", "bbc news", "bbc.com", "bbc.co.uk",
    "associated press", "apnews.com", "ap news",
    "iaea", "iaea.org",
    "world nuclear association", "world-nuclear.org", "world-nuclear-news.org",
    "uk office for nuclear regulation", "onr.org.uk",
    "nuclear regulatory commission", "nrc.gov",
    "the guardian", "theguardian.com",
    "full fact", "fullfact.org",
    "financial times", "ft.com",
    "the economist", "economist.com",
    "official press release",
}
LOW_CREDIBILITY_SOURCES = {
    "anonymous blog post", "unverified facebook page", "random telegram channel",
    "clickbait news network", "unknown twitter/x account", "conspiracy forum post",
    "secrettruthnews.biz", "viral whatsapp forward",
}

# --- Reference statements standing in for an official fact database -------
OFFICIAL_REFERENCE_CLAIMS = [
    "radiation levels within normal background range",
    "no radiological anomalies detected",
    "plant operating within licensed safety limits",
    "routine maintenance and scheduled inspection completed",
    "no risk to public health confirmed by regulator",
    "emergency drill conducted as part of standard preparedness",
]

SENSATIONAL_MARKERS = re.compile(
    r"\b(breaking|secret|urgent|cover.?up|shocking|won.?t believe|leaked|"
    r"insider|anonymous source|mainstream media|they don.?t want you to know)\b",
    re.IGNORECASE,
)

# Words/phrases that indicate a reassuring, factual context. If a sensational
# marker appears close to one of these, it's likely a safe/legitimate use
# (e.g. "a small leak was contained within safety limits") rather than
# sensationalism, so we don't penalize it as heavily.
REASSURING_CONTEXT = re.compile(
    r"\b(within (licensed )?(safety )?limits|no risk|contained|below (the )?"
    r"(regulatory )?threshold|confirmed by|verified|routine|no anomal|"
    r"posed no|well below|regulatory standards|normal background)\b",
    re.IGNORECASE,
)


def _sensational_hit_is_contextual(text: str) -> bool:
    """Returns True if a sensational marker is found AND there's reassuring,
    factual context nearby in the same sentence — treated as a soft signal
    rather than a hard misinformation flag."""
    if not SENSATIONAL_MARKERS.search(text):
        return False
    return bool(REASSURING_CONTEXT.search(text))


@dataclass
class TrustScoreResult:
    trust_score: float
    label: str
    model_confidence: float
    source_credibility: float
    corroboration_score: float
    sentiment_neutrality: float
    flags: List[str] = field(default_factory=list)

    def to_dict(self):
        return {
            "trust_score": round(self.trust_score, 1),
            "label": self.label,
            "components": {
                "model_confidence": round(self.model_confidence, 3),
                "source_credibility": round(self.source_credibility, 3),
                "corroboration_score": round(self.corroboration_score, 3),
                "sentiment_neutrality": round(self.sentiment_neutrality, 3),
            },
            "flags": self.flags,
        }


def score_source_credibility(source: str) -> float:
    if not source:
        return 0.5
    s = source.strip().lower()
    # Exact match first, then clean domain / word boundary matches
    # Remove common prefixes like 'www.', 'http://', 'https://'
    s_clean = re.sub(r"^(https?://)?(www\.)?", "", s)
    
    if s_clean in HIGH_CREDIBILITY_SOURCES:
        return 1.0
    if s_clean in LOW_CREDIBILITY_SOURCES:
        return 0.0

    # For substring matching, ensure we match on word boundaries or domain components
    # to avoid short inputs like "a" or "the" matching high/low credibility lists.
    for h in HIGH_CREDIBILITY_SOURCES:
        if h == s_clean:
            return 1.0
        # Domain name match
        if "." in h and "." in s_clean:
            if s_clean.endswith("." + h) or h.endswith("." + s_clean):
                return 1.0
        # Word boundary matching (minimum 3 characters to prevent accidental matches)
        if len(s_clean) > 2:
            if re.search(r"\b" + re.escape(s_clean) + r"\b", h) or re.search(r"\b" + re.escape(h) + r"\b", s_clean):
                return 1.0

    for l in LOW_CREDIBILITY_SOURCES:
        if l == s_clean:
            return 0.0
        # Word boundary matching (minimum 3 characters)
        if len(s_clean) > 2:
            if re.search(r"\b" + re.escape(s_clean) + r"\b", l) or re.search(r"\b" + re.escape(l) + r"\b", s_clean):
                return 0.0

    return 0.5  # unknown source: neutral


def check_corroboration(text: str) -> float:
    """Very simple keyword-overlap proxy for cross-referencing against an
    official database. Replace with a real semantic-similarity search
    (e.g. embeddings + cosine similarity against a live IAEA/ONR feed)
    for production use."""
    text_lower = text.lower()
    words = set(re.findall(r"[a-z]+", text_lower))
    best = 0.0
    for ref in OFFICIAL_REFERENCE_CLAIMS:
        ref_words = set(re.findall(r"[a-z]+", ref.lower()))
        overlap = len(words & ref_words) / max(len(ref_words), 1)
        best = max(best, overlap)
    return min(best, 1.0)


def score_sentiment_neutrality(text: str) -> float:
    """High absolute sentiment / sensational markers -> lower neutrality score."""
    compound = _sentiment_analyzer.polarity_scores(text)["compound"]
    neutrality = 1.0 - abs(compound)  # 1.0 = perfectly neutral, 0.0 = extreme
    if SENSATIONAL_MARKERS.search(text):
        # Softer penalty if the sensational word appears in a reassuring,
        # factual context (e.g. "leak... contained within safety limits")
        neutrality *= 0.85 if _sensational_hit_is_contextual(text) else 0.5
    return max(0.0, min(1.0, neutrality))


def compute_trust_score(
    text: str,
    model_confidence_real: float,
    source: str,
    weights: dict,
) -> TrustScoreResult:
    """
    model_confidence_real: probability the classifier assigns to the "Real"
    class (0-1). Comes from src/inference.py.
    """
    source_cred = score_source_credibility(source)
    corroboration = check_corroboration(text)
    sentiment_neutral = score_sentiment_neutrality(text)

    trust_score = 100 * (
        weights["weight_model_confidence"] * model_confidence_real
        + weights["weight_source_credibility"] * source_cred
        + weights["weight_corroboration"] * corroboration
        + weights["weight_sentiment_neutrality"] * sentiment_neutral
    )

    flags = []
    if source_cred == 0.0:
        flags.append("Source is on the known low-credibility list")
    if SENSATIONAL_MARKERS.search(text) and not _sensational_hit_is_contextual(text):
        flags.append("Sensationalized / clickbait language detected")
    if corroboration < 0.1:
        flags.append("No corroboration found against official reference claims")
    if model_confidence_real < 0.5:
        flags.append("Classifier predicts this is likely misinformation")

    if trust_score >= 70:
        label = "Likely Credible"
    elif trust_score >= 40:
        label = "Uncertain / Needs Review"
    else:
        label = "Likely Misinformation"

    return TrustScoreResult(
        trust_score=trust_score,
        label=label,
        model_confidence=model_confidence_real,
        source_credibility=source_cred,
        corroboration_score=corroboration,
        sentiment_neutrality=sentiment_neutral,
        flags=flags,
    )
