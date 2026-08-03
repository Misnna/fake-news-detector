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
    rightMargin=40,
    leftMargin=40,
    topMargin=40,
    bottomMargin=40
)

styles = getSampleStyleSheet()

# Custom Color Palette
PRIMARY = colors.HexColor("#0f172a")      # Dark Navy
ACCENT = colors.HexColor("#0284c7")       # Vibrant Sky Blue
SECONDARY = colors.HexColor("#334155")    # Slate Gray
LIGHT_BG = colors.HexColor("#f8fafc")     # Light Slate Background
BORDER_CLR = colors.HexColor("#cbd5e1")   # Border Light Gray
SUCCESS_CLR = colors.HexColor("#15803d")  # Green
WARNING_CLR = colors.HexColor("#b91c1c")  # Red

# Custom Typography Styles
title_style = ParagraphStyle(
    'DocTitle',
    parent=styles['Heading1'],
    fontName='Helvetica-Bold',
    fontSize=22,
    leading=26,
    textColor=PRIMARY,
    spaceAfter=6
)

subtitle_style = ParagraphStyle(
    'DocSubtitle',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=13,
    leading=16,
    textColor=ACCENT,
    spaceAfter=15
)

h1_style = ParagraphStyle(
    'SectionH1',
    parent=styles['Heading2'],
    fontName='Helvetica-Bold',
    fontSize=15,
    leading=18,
    textColor=PRIMARY,
    spaceBefore=14,
    spaceAfter=8
)

h2_style = ParagraphStyle(
    'SectionH2',
    parent=styles['Heading3'],
    fontName='Helvetica-Bold',
    fontSize=12,
    leading=15,
    textColor=ACCENT,
    spaceBefore=10,
    spaceAfter=4
)

body_style = ParagraphStyle(
    'BodyTextCustom',
    parent=styles['BodyText'],
    fontName='Helvetica',
    fontSize=10,
    leading=14,
    textColor=SECONDARY,
    spaceAfter=8
)

bullet_style = ParagraphStyle(
    'BulletCustom',
    parent=body_style,
    leftIndent=15,
    firstLineIndent=-10,
    spaceAfter=4
)

table_header_style = ParagraphStyle(
    'TableHeader',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=10,
    leading=12,
    textColor=colors.white
)

table_body_style = ParagraphStyle(
    'TableBody',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=9,
    leading=12,
    textColor=PRIMARY
)

story = []

# Title Banner
story.append(Paragraph("Nuclear Power Safety — Fake News & Trust Score Detector", title_style))
story.append(Paragraph("Complete Project Explanation in Simple Terms (ML, NLP & Modalities)", subtitle_style))
story.append(HRFlowable(width="100%", thickness=2, color=ACCENT, spaceBefore=0, spaceAfter=15))

# 1. Executive Summary
story.append(Paragraph("1. Executive Summary", h1_style))
story.append(Paragraph(
    "This project is an AI-powered verification system designed to detect fake news and calculate a "
    "<b>0–100 Trust Score</b> for news articles related to nuclear power and public safety. "
    "It allows users to verify information from <b>3 input formats</b>: raw text, web links (URLs), or news screenshots/images.",
    body_style
))

# 2. What are ML and NLP? (Simple Terms)
story.append(Paragraph("2. Understanding ML & NLP in Simple Terms", h1_style))

story.append(Paragraph("What is NLP (Natural Language Processing)?", h2_style))
story.append(Paragraph(
    "<b>NLP</b> is the branch of Artificial Intelligence that teaches computers how to read, understand, "
    "and analyze human languages (words, sentences, and tone). In this project, NLP works like a digital editor "
    "that reads news text, cleans up clutter, detects sensational or emotional words, and extracts key facts.",
    body_style
))

story.append(Paragraph("What is ML (Machine Learning)?", h2_style))
story.append(Paragraph(
    "<b>ML</b> is the technology that allows computers to learn patterns from data instead of following rigid rules. "
    "We trained our ML model on thousands of real and fake news articles. By looking at these examples, the ML model "
    "learned the subtle patterns of legitimate journalism versus deceptive misinformation.",
    body_style
))

# 3. The 3 Input Modalities
story.append(Paragraph("3. How the 3 Input Modalities Work", h1_style))

story.append(Paragraph("📝 1. Text Input (Direct Articles)", h2_style))
story.append(Paragraph(
    "The user pastes news text directly into the application. The system cleans the text (removing extra spacing, "
    "special symbols, and formatting) and passes it directly to the NLP models for fake news detection.",
    body_style
))

story.append(Paragraph("🔗 2. Link / URL Input (Web Articles)", h2_style))
story.append(Paragraph(
    "The user provides a website link (e.g., Reuters, BBC, or an unverified blog). The system automatically fetches "
    "and extracts the full article text while also assessing the <b>reputation of the domain</b> (e.g., trusted news agency vs. unknown site).",
    body_style
))

story.append(Paragraph("🖼️ 3. Image Input (Screenshots & Social Media Posts)", h2_style))
story.append(Paragraph(
    "The user uploads a screenshot of a news headline or social media graphic. An <b>OCR (Optical Character Recognition)</b> "
    "model reads the pixels in the image and converts the text into digital words, which are then passed to the NLP model.",
    body_style
))

# 4. AI & ML Models Used in the System
story.append(Paragraph("4. All Models Used in the System (Simplified)", h1_style))

models_data = [
    [Paragraph("Model Name", table_header_style), Paragraph("Type", table_header_style), Paragraph("Role in Simple Terms", table_header_style)],
    [
        Paragraph("<b>RoBERTa / DeBERTa</b>", table_body_style),
        Paragraph("Deep Learning (Transformer NLP)", table_body_style),
        Paragraph("Main Classifier: Reads text context & classifies it as <b>Real</b> or <b>Fake</b> based on learned news patterns.", table_body_style)
    ],
    [
        Paragraph("<b>EasyOCR</b>", table_body_style),
        Paragraph("Computer Vision + OCR Model", table_body_style),
        Paragraph("Image Reader: Extracts printed/written text from uploaded news screenshots.", table_body_style)
    ],
    [
        Paragraph("<b>VADER & TextBlob</b>", table_body_style),
        Paragraph("Rule-based NLP Sentiment Models", table_body_style),
        Paragraph("Tone Analyzer: Measures whether the text is calm/neutral (credible) or overly emotional/dramatic (suspicious).", table_body_style)
    ],
    [
        Paragraph("<b>Domain Credibility Scorer</b>", table_body_style),
        Paragraph("Heuristic Rule Engine", table_body_style),
        Paragraph("Source Check: Assigns trust scores based on official domain reputation (e.g. government, news wire vs. clickbait blogs).", table_body_style)
    ],
    [
        Paragraph("<b>Multi-Factor Trust Engine</b>", table_body_style),
        Paragraph("Ensemble Scoring Engine", table_body_style),
        Paragraph("Score Calculator: Combines 4 signals into a final <b>0–100 Trust Score</b>.", table_body_style)
    ]
]

t = Table(models_data, colWidths=[1.8*inch, 1.8*inch, 3.4*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), PRIMARY),
    ('ALIGN', (0,0), (-1,-1), 'LEFT'),
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ('GRID', (0,0), (-1,-1), 0.5, BORDER_CLR),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG]),
    ('TOPPADDING', (0,0), (-1,-1), 6),
    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
]))
story.append(t)

# 5. Trust Score Formula
story.append(Paragraph("5. How the 0–100 Trust Score is Computed", h1_style))
story.append(Paragraph(
    "The system does not rely on a single score. It calculates 4 individual weights into a final score:",
    body_style
))
story.append(Paragraph("• <b>45% ML Model Confidence:</b> Output probability from the RoBERTa classifier.", bullet_style))
story.append(Paragraph("• <b>25% Source Credibility:</b> Reputation ranking of the news source/domain.", bullet_style))
story.append(Paragraph("• <b>20% Fact Corroboration:</b> Match against verified official nuclear databases.", bullet_style))
story.append(Paragraph("• <b>10% Tone Neutrality:</b> Absence of clickbait / sensational emotional language.", bullet_style))

# Build Document
doc.build(story)
print(f"PDF generated successfully at: {pdf_path}")
