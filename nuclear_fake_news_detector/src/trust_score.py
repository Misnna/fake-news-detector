"""
UK Nuclear Power Safety Information - Trust Verification Engine

Calculates a 0-100 Trust Score for news claims by combining:
1. Domain model classification confidence
2. Known source credibility scoring
3. Fact corroboration against official logs (ONR, IAEA, EURDEP)
4. Sentiment and sensationalism analysis
5. Domain relevance validation (filtering non-nuclear news)
"""
import re
from dataclasses import dataclass, field
from typing import List

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_sentiment_analyzer = SentimentIntensityAnalyzer()

# High credibility sources focusing on UK nuclear regulatory and major publishers
HIGH_CREDIBILITY_SOURCES = {
    "reuters", "reuters.com", "bbc news", "bbc.com", "bbc.co.uk", "bbc",
    "associated press", "apnews.com", "ap news",
    "iaea", "iaea.org", "iaea incident and emergency centre", "iaea iec",
    "gov.uk", "www.gov.uk", "uk government", "official government statement",
    "world nuclear association", "world-nuclear.org", "world-nuclear-news.org",
    "uk office for nuclear regulation", "onr.org.uk", "onr", "ukaea", "ukaea.uk",
    "nuclear regulatory commission", "nrc.gov", "nrc",
    "eurdep", "eurdep.jrc.ec.europa.eu", "radnet", "epa radnet",
    "snopes", "snopes.com", "politifact", "politifact.com",
    "the guardian", "theguardian.com",
    "full fact", "fullfact.org",
    "financial times", "ft.com",
    "the economist", "economist.com",
    "the telegraph", "telegraph.co.uk",
    "the times", "thetimes.co.uk",
    "daily mail", "dailymail.co.uk",
    "sky news", "news.sky.com",
    "edf energy", "edf", "edfenergy.com",
    "official press release",
}

LOW_CREDIBILITY_SOURCES = {
    "anonymous blog post", "unverified facebook page", "random telegram channel",
    "clickbait news network", "unknown twitter/x account", "conspiracy forum post",
    "secrettruthnews.biz", "viral whatsapp forward",
}

# Reference statements representing official UK & IAEA safety logs and environmental monitoring
OFFICIAL_REFERENCE_CLAIMS = [
    "radiation levels within normal background range",
    "no radiological anomalies detected",
    "plant operating within licensed safety limits",
    "routine maintenance and scheduled inspection completed",
    "no risk to public health confirmed by regulator",
    "emergency drill conducted as part of standard preparedness",
    "decontaminated water discharge meets international safety guidelines",
    "fuel assembly inspection within regulatory limits",
    "uk statement on ukraine iaea board of governors nuclear safety risk reduction",
    "iaea incident and emergency centre reports zero radioactive releases",
    "eurdep radiation monitoring network confirms normal background levels",
    "uk office for nuclear regulation confirmed routine maintenance",
    "danube river water levels nuclear power generation hungary romania cernavoda paks cooling water drought",
    "drought and heatwave cooling water management operational restrictions cernavoda paks nuclear plant",
    "environmental cooling water monitoring danube river nuclear safety",
]

# Keywords to detect if article text is related to nuclear power / energy domain
NUCLEAR_DOMAIN_KEYWORDS = re.compile(
    r"\b(nuclear|atomic|radiation|radiological|reactor|fission|fusion|uranium|"
    r"plutonium|radioactive|half-life|geiger|sievert|becquerel|cooling tower|"
    r"core meltdown|spent fuel|decommissioning|iaea|onr|ukaea|desnz|eurdep|"
    r"sizewell|hinkley|sellafield|torness|heysham|dungeness|hunterston|hartlepool|"
    r"bradwell|wylfa|oldbury|berkeley|chapelcross|springfields|capenhurst|culham|"
    r"cernavoda|cernavodă|paks|danube|cooling-water|cooling water|"
    r"edf energy|small modular reactor|smr|atomic energy)\b",
    re.IGNORECASE,
)

SENSATIONAL_MARKERS = re.compile(
    r"\b(breaking|secret|urgent|cover.?up|shocking|won.?t believe|leaked|"
    r"insider|anonymous source|mainstream media|they don.?t want you to know|"
    r"accident|meltdown|evacuat\w*|emergency|disaster|catastrophe|leak\w*|"
    r"radiation spread|radiation leak|contamination|contaminat\w*|spreading|"
    r"drinking water|poison\w*|toxic|radioactive|cancer|tumor|die|dying|"
    r"deaths|fatal|illness|geiger|glowing|baffled|tripled|quadrupled|fire|explosion)\b",
    re.IGNORECASE,
)

UNVERIFIED_MILESTONE_MARKERS = re.compile(
    r"\b(ahead of schedule|started generating electricity|connected to (the )?national grid|"
    r"first criticality|full power generation|infinite energy|zero-radiation|cold-fusion|"
    r"commercial operation ahead|secretly operational)\b",
    re.IGNORECASE,
)

REASSURING_CONTEXT = re.compile(
    r"\b(within (licensed )?(safety )?limits|no risk|contained|below (the )?"
    r"(regulatory )?threshold|confirmed by|verified|routine|no anomal|"
    r"posed no|well below|regulatory standards|normal background|"
    r"board of governors|uk statement|director general|diplomatic statement|statement to|reduce nuclear risk|"
    r"incident and emergency centre|eurdep|danube|cooling.?water|cernavod[aă]|paks|river levels|drought)\b",
    re.IGNORECASE,
)


def is_nuclear_domain_related(text: str) -> bool:
    """Checks whether text contains nuclear energy or power plant safety terms."""
    if not text or len(text.strip()) < 10:
        return True  # Avoid false rejection on very short inputs
    return bool(NUCLEAR_DOMAIN_KEYWORDS.search(text))


def _sensational_hit_is_contextual(text: str) -> bool:
    """Returns True if alarmist words appear alongside factual reassuring context."""
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
    """Matches publisher name or domain against curated high/low credibility sets."""
    if not source:
        return 0.5
    s = source.strip().lower()
    s_clean = re.sub(r"^(https?://)?(www\.)?", "", s)
    
    if s_clean in HIGH_CREDIBILITY_SOURCES:
        return 1.0
    if s_clean in LOW_CREDIBILITY_SOURCES:
        return 0.0

    for h in HIGH_CREDIBILITY_SOURCES:
        if h == s_clean:
            return 1.0
        if "." in h and "." in s_clean:
            if s_clean.endswith("." + h) or h.endswith("." + s_clean):
                return 1.0
        if len(s_clean) > 2:
            if re.search(r"\b" + re.escape(s_clean) + r"\b", h) or re.search(r"\b" + re.escape(h) + r"\b", s_clean):
                return 1.0

    for l in LOW_CREDIBILITY_SOURCES:
        if l == s_clean:
            return 0.0
        if len(s_clean) > 2:
            if re.search(r"\b" + re.escape(s_clean) + r"\b", l) or re.search(r"\b" + re.escape(l) + r"\b", s_clean):
                return 0.0

    return 0.5


def check_corroboration(text: str) -> float:
    """Calculates claim overlap against known official safety reports."""
    text_lower = text.lower()
    words = set(re.findall(r"[a-z]+", text_lower))
    best = 0.0
    for ref in OFFICIAL_REFERENCE_CLAIMS:
        ref_words = set(re.findall(r"[a-z]+", ref.lower()))
        overlap = len(words & ref_words) / max(len(ref_words), 1)
        best = max(best, overlap)
    return min(best, 1.0)


def auto_detect_source_from_text(text: str, source: str) -> str:
    """Auto-detects major news sources from domain links or explicit header lines."""
    if source and source.strip().lower() not in {"social media screenshot", "unknown", "none", "", "news report", "news", "unverified news"}:
        return source
    text_lower = text.lower()
    
    publisher_patterns = [
        (r"^(reported by|source:|published by|official press release from)\s+iaea\b", "IAEA Incident and Emergency Centre"),
        (r"^(reported by|source:|published by)\s+(bbc|bbc news)\b", "BBC News"),
        (r"^(reported by|source:|published by)\s+reuters\b", "Reuters"),
        (r"^(reported by|source:|published by)\s+(the guardian|guardian)\b", "The Guardian"),
        (r"^(reported by|source:|published by)\s+(uk office for nuclear regulation|onr)\b", "UK Office for Nuclear Regulation"),
        (r"\bhttps?://([a-z0-9\-]+\.)*iaea\.org\b", "IAEA Incident and Emergency Centre"),
        (r"\bhttps?://([a-z0-9\-]+\.)*bbc\.(co\.uk|com)\b", "BBC News"),
        (r"\bhttps?://([a-z0-9\-]+\.)*reuters\.com\b", "Reuters"),
        (r"\bhttps?://([a-z0-9\-]+\.)*theguardian\.com\b", "The Guardian"),
        (r"\bhttps?://([a-z0-9\-]+\.)*onr\.org\.uk\b", "UK Office for Nuclear Regulation"),
        (r"\bhttps?://([a-z0-9\-]+\.)*gov\.uk\b", "GOV.UK (Official UK Government)"),
    ]
    
    for pat, label in publisher_patterns:
        if re.search(pat, text_lower):
            return label
            
    return source


def score_sentiment_neutrality(text: str) -> float:
    """Measures sentiment neutrality — strong emotional/sensational phrasing scores lower."""
    compound = _sentiment_analyzer.polarity_scores(text)["compound"]
    if SENSATIONAL_MARKERS.search(text):
        base = 1.0 - abs(compound)
        return max(0.0, min(1.0, base * (0.85 if _sensational_hit_is_contextual(text) else 0.4)))
    else:
        return max(0.7, min(1.0, 1.0 - 0.2 * abs(compound)))


def compute_trust_score(
    text: str,
    model_confidence_real: float,
    source: str,
    weights: dict,
) -> TrustScoreResult:
    """Computes overall verification Trust Score and assigns classification label."""
    # Check domain relevance first
    if not is_nuclear_domain_related(text):
        return TrustScoreResult(
            trust_score=50.0,
            label="Not Related to Nuclear Power",
            model_confidence=0.5,
            source_credibility=0.5,
            corroboration_score=0.0,
            sentiment_neutrality=0.5,
            flags=["Article text is not related to nuclear power plant operations or nuclear safety topics."],
        )

    source = auto_detect_source_from_text(text, source)
    source_cred = score_source_credibility(source)
    has_sensational = SENSATIONAL_MARKERS.search(text) and not _sensational_hit_is_contextual(text)
    has_unverified_milestone = bool(UNVERIFIED_MILESTONE_MARKERS.search(text))

    if (has_sensational or has_unverified_milestone) and source_cred < 0.8:
        corroboration = 0.0
    else:
        corroboration = check_corroboration(text)

    sentiment_neutral = score_sentiment_neutrality(text)

    if source_cred >= 0.8:
        sentiment_neutral = max(0.75, sentiment_neutral)

    is_low_cred_source = (source_cred == 0.0)
    is_uncorroborated_neutral = (corroboration < 0.2) and (not is_low_cred_source) and (not has_sensational) and (not has_unverified_milestone) and (source_cred < 0.8) and (0.4 <= model_confidence_real <= 0.6)

    trust_score = 100 * (
        weights["weight_model_confidence"] * model_confidence_real
        + weights["weight_source_credibility"] * source_cred
        + weights["weight_corroboration"] * corroboration
        + weights["weight_sentiment_neutrality"] * sentiment_neutral
    )

    if has_sensational and source_cred < 0.8:
        trust_score *= 0.55
    elif has_unverified_milestone and source_cred < 0.8:
        trust_score *= 0.50

    flags = []
    if source_cred == 0.0:
        flags.append("Source is on the known low-credibility list")
    if has_sensational:
        flags.append("Sensationalized / alarmist disaster language detected without official confirmation")
    if has_unverified_milestone and source_cred < 0.8:
        flags.append("Unverified milestone or premature completion claim without verified official publisher domain")
    if corroboration < 0.1 and not has_sensational and not has_unverified_milestone:
        if is_uncorroborated_neutral:
            flags.append("Insufficient verification data (No match in official IAEA/ONR logs, but no alarmist markers detected)")
        else:
            flags.append("No corroboration found against official reference claims")
    if model_confidence_real < 0.5:
        flags.append("Classifier predicts this is likely misinformation")

    if is_uncorroborated_neutral:
        label = "Insufficient Verification Data"
        trust_score = max(50.0, min(65.0, trust_score))
    elif (has_sensational or has_unverified_milestone) and source_cred < 0.8:
        label = "Likely Misinformation"
        trust_score = min(39.9, trust_score)
    elif trust_score >= 70:
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

