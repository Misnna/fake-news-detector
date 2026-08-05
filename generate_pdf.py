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
story.append(Paragraph("NUCLEAR POWER SAFETY FAKE NEWS DETECTOR", title_style))
story.append(Paragraph("Comprehensive Technical & System Explanation Report (UK & IAEA Scope)", subtitle_style))
story.append(HRFlowable(width="100%", thickness=1.5, color=ACCENT, spaceBefore=0, spaceAfter=10))

# 1. Executive Summary
story.append(Paragraph("1. Executive Summary", h1_style))
story.append(Paragraph(
    "This system is an AI-powered verification platform designed to detect fake news, prevent public panic, "
    "and compute a transparent <b>0–100 Trust Score</b> for statements regarding nuclear power safety. "
    "Operating under UK regulatory scope and IAEA international standards, it processes <b>3 input modalities</b> "
    "(raw text, article links/URLs, and news screenshots/images) to deliver defensible decision support.",
    body_style
))

# 2. Understanding ML & NLP (Simple Terms)
story.append(Paragraph("2. Core Concepts Explained in Simple Terms", h1_style))
story.append(Paragraph("• <b>Natural Language Processing (NLP):</b> AI branch that allows computers to read, clean, and analyze human language text in simple single-line steps.", bullet_style))
story.append(Paragraph("• <b>Machine Learning (ML):</b> Systems that learn predictive news patterns directly from thousands of training examples instead of relying on manual rules.", bullet_style))
story.append(Paragraph("• <b>Computer Vision (OCR):</b> Technology that scans news images and converts visual printed pixels into digital readable text.", bullet_style))

# 3. All Models Used in the System
story.append(Paragraph("3. Models Used in the Project & Their Roles", h1_style))

models_data = [
    [Paragraph("Model Name", table_header_style), Paragraph("Type & Framework", table_header_style), Paragraph("Role & Explanation in Simple Terms", table_header_style), Paragraph("Data Consumed", table_header_style)],
    [
        Paragraph("<b>RoBERTa / DeBERTa</b>", table_body_style),
        Paragraph("Transformer Deep Learning (PyTorch)", table_body_style),
        Paragraph("Main Text Classifier: Evaluates linguistic context to detect subtle fake news patterns versus authentic technical reporting.", table_body_style),
        Paragraph("Fine-tuned on 654 UK & IAEA nuclear safety claims.", table_body_style)
    ],
    [
        Paragraph("<b>EasyOCR</b>", table_body_style),
        Paragraph("Computer Vision OCR (PyTorch + OpenCV)", table_body_style),
        Paragraph("Image Text Extractor: Reads printed text from uploaded news screenshots and social media graphics.", table_body_style),
        Paragraph("Raw image pixels (PNG, JPG, WebP screenshots).", table_body_style)
    ],
    [
        Paragraph("<b>VADER & TextBlob</b>", table_body_style),
        Paragraph("NLP Sentiment & Tone Analyzer", table_body_style),
        Paragraph("Emotional Tone Checker: Measures whether article phrasing is calm/objective or overly sensational/alarmist.", table_body_style),
        Paragraph("Parsed article text & headline tokens.", table_body_style)
    ],
    [
        Paragraph("<b>Domain Reputation Engine</b>", table_body_style),
        Paragraph("Heuristic Rule Evaluator", table_body_style),
        Paragraph("Publisher Verifier: Assigns credibility rankings based on domain authority (e.g., GOV.UK, BBC News vs clickbait blogs).", table_body_style),
        Paragraph("URL domain names & publisher headers.", table_body_style)
    ],
    [
        Paragraph("<b>Fact Corroboration Engine</b>", table_body_style),
        Paragraph("Keyword Overlap & Entity Matcher", table_body_style),
        Paragraph("Official Log Cross-Checker: Verifies statements against authenticated nuclear safety incident databases.", table_body_style),
        Paragraph("IAEA IEC, UK ONR & EURDEP reference claims.", table_body_style)
    ],
    [
        Paragraph("<b>Multi-Factor Trust Engine</b>", table_body_style),
        Paragraph("Ensemble Decision Engine", table_body_style),
        Paragraph("Score Calculator: Combines model confidence, publisher trust, corroboration, and tone into a final 0–100 Trust Score.", table_body_style),
        Paragraph("Outputs from all 5 sub-models above.", table_body_style)
    ]
]

t = Table(models_data, colWidths=[1.4*inch, 1.4*inch, 2.7*inch, 1.7*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), PRIMARY),
    ('ALIGN', (0,0), (-1,-1), 'LEFT'),
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ('GRID', (0,0), (-1,-1), 0.5, BORDER_CLR),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG]),
    ('TOPPADDING', (0,0), (-1,-1), 5),
    ('BOTTOMPADDING', (0,0), (-1,-1), 5),
]))
story.append(t)

# 4. Datasets Used in the Project
story.append(Paragraph("4. Datasets & Domain Scope", h1_style))
story.append(Paragraph("• <b>Primary Fine-Tuning Dataset (data/sample_dataset.csv):</b> 654 unique rows focusing on UK nuclear power stations (<i>Hinkley Point C, Sizewell B, Torness, Heysham, Dungeness B, Sellafield, Wylfa</i>) and IAEA standards.", bullet_style))
story.append(Paragraph("• <b>Held-Out Test Dataset (data/holdout_test.csv):</b> 30 hand-crafted test statements never seen during training to evaluate real-world generalization (achieving 93% accuracy).", bullet_style))
story.append(Paragraph("• <b>Data Specificity:</b> Pure UK and IAEA scope with zero non-UK or Indian data included.", bullet_style))

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
story.append(Paragraph("• <b>45% Model Confidence:</b> Transformer classifier prediction probability.", bullet_style))
story.append(Paragraph("• <b>25% Source Credibility:</b> Reputation ranking of the news domain/source.", bullet_style))
story.append(Paragraph("• <b>20% Fact Corroboration:</b> Match against verified IAEA IEC and UK ONR safety logs.", bullet_style))
story.append(Paragraph("• <b>10% Tone Neutrality:</b> Absence of clickbait / sensational emotional language.", bullet_style))

# Build Document
doc.build(story)
print(f"PDF generated successfully at: {pdf_path}")
