import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)

pdf_filename = "Nuclear_Fake_News_Detector_Explanation.pdf"
pdf_path = os.path.abspath(pdf_filename)

doc = SimpleDocTemplate(
    pdf_path,
    pagesize=letter,
    rightMargin=36,
    leftMargin=36,
    topMargin=36,
    bottomMargin=36
)

styles = getSampleStyleSheet()

# Custom Color Palette
PRIMARY = colors.HexColor("#0f172a")      # Dark Navy
ACCENT = colors.HexColor("#0284c7")       # Sky Blue
SECONDARY = colors.HexColor("#334155")    # Slate Gray
LIGHT_BG = colors.HexColor("#f8fafc")     # Light Slate Background
BORDER_CLR = colors.HexColor("#cbd5e1")   # Border Gray
SUCCESS_CLR = colors.HexColor("#15803d")  # Green
WARNING_CLR = colors.HexColor("#b91c1c")  # Red

title_style = ParagraphStyle(
    'DocTitle',
    parent=styles['Heading1'],
    fontName='Helvetica-Bold',
    fontSize=20,
    leading=24,
    textColor=PRIMARY,
    spaceAfter=4
)

subtitle_style = ParagraphStyle(
    'DocSubtitle',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=11,
    leading=14,
    textColor=ACCENT,
    spaceAfter=12
)

h1_style = ParagraphStyle(
    'SectionH1',
    parent=styles['Heading2'],
    fontName='Helvetica-Bold',
    fontSize=13,
    leading=16,
    textColor=PRIMARY,
    spaceBefore=12,
    spaceAfter=6
)

h2_style = ParagraphStyle(
    'SectionH2',
    parent=styles['Heading3'],
    fontName='Helvetica-Bold',
    fontSize=10,
    leading=13,
    textColor=ACCENT,
    spaceBefore=8,
    spaceAfter=3
)

body_style = ParagraphStyle(
    'BodyTextCustom',
    parent=styles['BodyText'],
    fontName='Helvetica',
    fontSize=9,
    leading=13,
    textColor=SECONDARY,
    spaceAfter=6
)

bullet_style = ParagraphStyle(
    'BulletCustom',
    parent=body_style,
    leftIndent=12,
    firstLineIndent=-8,
    spaceAfter=3
)

table_header_style = ParagraphStyle(
    'TableHeader',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=9,
    leading=11,
    textColor=colors.white
)

table_body_style = ParagraphStyle(
    'TableBody',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=8,
    leading=11,
    textColor=PRIMARY
)

story = []

# Title Banner
story.append(Paragraph("UK NUCLEAR POWER SAFETY VERIFICATION FRAMEWORK", title_style))
story.append(Paragraph("MSc Research Technical Report & System Architecture Document (UK ONR & IAEA Scope)", subtitle_style))
story.append(HRFlowable(width="100%", thickness=1.5, color=ACCENT, spaceBefore=0, spaceAfter=10))

# 1. Executive Summary
story.append(Paragraph("1. Executive Summary", h1_style))
story.append(Paragraph(
    "This research framework presents a multi-modal decision support platform for verifying statements "
    "concerning UK nuclear power safety (covering Hinkley Point C, Sizewell B/C, Torness, Heysham, Dungeness B, and Sellafield). "
    "Operating under UK Office for Nuclear Regulation (ONR) guidelines and IAEA international standards, the system combines "
    "deep transformer sequence classification with a transparent <b>0–100 Multi-Factor Trust Engine</b> across <b>3 input modalities</b> "
    "(raw text, direct article URLs, and news graphics/screenshots via deep-learning OCR).",
    body_style
))

# 2. Core Methodological Architecture
story.append(Paragraph("2. System Methodology & Core Components", h1_style))
story.append(Paragraph("• <b>Natural Language Processing (NLP):</b> Fine-tuned transformer models evaluate subtle contextual syntactic markers distinguishing authentic technical reporting from deceptive claims.", bullet_style))
story.append(Paragraph("• <b>Supervised Transfer Learning:</b> Sequence classifiers are initialized from domain-specific checkpoints and tuned using class-weighted cross-entropy loss and label smoothing.", bullet_style))
story.append(Paragraph("• <b>Computer Vision OCR:</b> Deep-learning Optical Character Recognition (EasyOCR) extracts text from social media graphics and article screenshots.", bullet_style))

# 3. All Models Used in the System
story.append(Paragraph("3. Models & Decision Components in the System", h1_style))

models_data = [
    [Paragraph("Component Name", table_header_style), Paragraph("Type & Framework", table_header_style), Paragraph("Role & Technical Explanation", table_header_style), Paragraph("Data Consumed", table_header_style)],
    [
        Paragraph("<b>Domain Relevance Filter</b>", table_body_style),
        Paragraph("Regex Keyword Matching Engine", table_body_style),
        Paragraph("Nuclear Topic Checker: Verifies if incoming text concerns nuclear power/energy. Out-of-domain news is labeled 'Not Related to Nuclear Power'.", table_body_style),
        Paragraph("Input article text & headline tokens.", table_body_style)
    ],
    [
        Paragraph("<b>RoBERTa / DeBERTa</b>", table_body_style),
        Paragraph("Transformer Deep Learning (PyTorch)", table_body_style),
        Paragraph("Main Text Classifier: Evaluates linguistic context to detect subtle fake news patterns versus authentic technical reporting.", table_body_style),
        Paragraph("Fine-tuned on UK & IAEA nuclear safety dataset.", table_body_style)
    ],
    [
        Paragraph("<b>EasyOCR Engine</b>", table_body_style),
        Paragraph("Computer Vision OCR (PyTorch + OpenCV)", table_body_style),
        Paragraph("Image Text Extractor: Reads printed text from uploaded news screenshots and social media graphics.", table_body_style),
        Paragraph("Raw image pixels (PNG, JPG, WebP screenshots).", table_body_style)
    ],
    [
        Paragraph("<b>VADER Sentiment Analyzer</b>", table_body_style),
        Paragraph("NLP Sentiment & Tone Evaluator", table_body_style),
        Paragraph("Emotional Tone Checker: Measures whether article phrasing is calm and objective or overly sensational/alarmist.", table_body_style),
        Paragraph("Parsed article text & headline tokens.", table_body_style)
    ],
    [
        Paragraph("<b>Publisher Credibility Evaluator</b>", table_body_style),
        Paragraph("Heuristic Rule Engine", table_body_style),
        Paragraph("Publisher Verifier: Assigns credibility rankings based on domain authority (e.g., GOV.UK, BBC News, ONR vs clickbait blogs).", table_body_style),
        Paragraph("URL domain names & publisher headers.", table_body_style)
    ],
    [
        Paragraph("<b>Official Corroboration Engine</b>", table_body_style),
        Paragraph("Keyword Overlap Matcher", table_body_style),
        Paragraph("Official Log Cross-Checker: Verifies statements against authenticated UK ONR and IAEA nuclear safety incident databases.", table_body_style),
        Paragraph("IAEA IEC, UK ONR & EURDEP safety claims.", table_body_style)
    ],
    [
        Paragraph("<b>Multi-Factor Trust Engine</b>", table_body_style),
        Paragraph("Ensemble Decision Engine", table_body_style),
        Paragraph("Score Calculator: Combines model confidence, publisher trust, corroboration, and tone into a final 0–100 Trust Score.", table_body_style),
        Paragraph("Outputs from all sub-models above.", table_body_style)
    ]
]

t = Table(models_data, colWidths=[1.4*inch, 1.4*inch, 2.7*inch, 1.7*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), PRIMARY),
    ('ALIGN', (0,0), (-1,-1), 'LEFT'),
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ('GRID', (0,0), (-1,-1), 0.5, BORDER_CLR),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG]),
    ('TOPPADDING', (0,0), (-1,-1), 4),
    ('BOTTOMPADDING', (0,0), (-1,-1), 4),
]))
story.append(t)

# 4. Datasets Used in the Project
story.append(Paragraph("4. Datasets & Domain Scope", h1_style))
story.append(Paragraph("• <b>Primary Fine-Tuning Dataset (data/sample_dataset.csv):</b> 654 unique rows focusing on UK nuclear power stations (<i>Hinkley Point C, Sizewell B/C, Torness, Heysham 1/2, Dungeness B, Sellafield, Hunterston B, Wylfa</i>) and IAEA standards.", bullet_style))
story.append(Paragraph("• <b>Held-Out Test Dataset (data/holdout_test.csv):</b> 30 hand-crafted test statements never seen during training to evaluate real-world generalization (achieving 93% accuracy).", bullet_style))
story.append(Paragraph("• <b>Data Specificity:</b> Pure UK and IAEA scope with zero non-UK or Indian data included.", bullet_style))
story.append(Paragraph("• <b>Out-of-Domain Handling:</b> Non-nuclear articles (e.g. general sports, politics) are safely identified as 'Not Related to Nuclear Power'.", bullet_style))

# 5. Data Sources Specific to Nuclear Fact-Checking
story.append(Paragraph("5. Data Sources Specific to Nuclear Fact-Checking", h1_style))
story.append(Paragraph("1. <b>IAEA Incident and Emergency Centre (IEC) Reports:</b> Official international bulletins for radiological incidents.", bullet_style))
story.append(Paragraph("2. <b>National Regulators:</b> UK Office for Nuclear Regulation (ONR), UKAEA, DESNZ / GOV.UK, and US NRC declarations.", bullet_style))
story.append(Paragraph("3. <b>Radiation Monitoring Networks:</b> EURDEP (European Radiological Data Exchange Platform) & EPA RadNet.", bullet_style))
story.append(Paragraph("4. <b>Nuclear Fact-Checking Archives:</b> Verified tagged archives from Full Fact UK, Snopes, and PolitiFact.", bullet_style))

# 6. Honest Uncertainty Handling Policy
story.append(Paragraph("6. Handle Uncertainty Honestly (Section 7 Policy)", h1_style))
story.append(Paragraph(
    "For high-consequence topics like nuclear safety, when a statement has no corroborating match in official logs "
    "and lacks clickbait/alarmist markers, the system <b>does not force a fake score</b>. It flags the item as "
    "<b>'Insufficient Verification Data'</b> (Trust Score 50–65/100) to prevent dangerous false positives on genuine safety information.",
    body_style
))

# 7. Trust Score Breakdown Formula
story.append(Paragraph("7. Trust Score Calculation Weights", h1_style))
story.append(Paragraph("• <b>35% Model Confidence:</b> Transformer classifier prediction probability.", bullet_style))
story.append(Paragraph("• <b>25% Source Credibility:</b> Reputation ranking of the news domain/source.", bullet_style))
story.append(Paragraph("• <b>25% Fact Corroboration:</b> Match against verified IAEA IEC and UK ONR safety logs.", bullet_style))
story.append(Paragraph("• <b>15% Tone Neutrality:</b> Absence of clickbait / sensational emotional language.", bullet_style))

# Build Document
doc.build(story)
print(f"PDF generated successfully at: {pdf_path}")
