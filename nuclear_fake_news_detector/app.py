"""
Flask UI for the Nuclear Power Safety Fake News & Trust Score Detector.
Clean, clutter-free single-column design focusing on core verification.
"""
import io
import re
import urllib.parse

from flask import Flask, render_template_string, request

from src.inference import FakeNewsDetector
from src.url_extractor import extract_article_text, URLExtractionError
from src.image_extractor import extract_text_from_image, ImageExtractionError

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(BASE_DIR, "config.yaml")
model_dir = os.path.join(BASE_DIR, "saved_model", "final")

app = Flask(__name__)
detector = FakeNewsDetector(model_dir, config_path)

STYLE = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
  
  * { box-sizing: border-box; }
  body {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    max-width: 860px;
    margin: 0 auto;
    padding: 36px 20px;
    background: #f1f5f9;
    color: #0f172a;
    line-height: 1.5;
  }
  
  .header-card {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    color: white;
    padding: 24px 30px;
    border-radius: 18px;
    margin-bottom: 24px;
    box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.15);
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .brand-logo {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 22px;
    font-weight: 800;
    color: white;
    letter-spacing: -0.5px;
  }
  .brand-icon {
    width: 38px;
    height: 38px;
    background: #0284c7;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
  }

  .input-card {
    background: white;
    border-radius: 20px;
    padding: 28px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 20px rgba(0,0,0,0.03);
  }

  .tabs-bar {
    display: flex;
    gap: 8px;
    margin-bottom: 20px;
    background: #f8fafc;
    padding: 6px;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
  }
  .tab-item {
    flex: 1;
    text-align: center;
    padding: 12px 14px;
    border-radius: 8px;
    font-weight: 700;
    font-size: 14px;
    color: #64748b;
    cursor: pointer;
    transition: all 0.2s ease;
    border: none;
    background: transparent;
  }
  .tab-item:hover { color: #0f172a; }
  .tab-item.active {
    background: white;
    color: #0284c7;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  }

  .tab-panel {
    display: none;
  }
  .tab-panel.active { display: block; }

  label {
    display: block;
    font-weight: 700;
    font-size: 14px;
    color: #334155;
    margin-bottom: 8px;
  }
  
  .input-box {
    width: 100%;
    padding: 14px 18px;
    border-radius: 12px;
    border: 1px solid #cbd5e1;
    font-size: 14px;
    font-family: inherit;
    background: #f8fafc;
    transition: all 0.2s ease;
    color: #0f172a;
  }
  .input-box:focus {
    outline: none;
    background: white;
    border-color: #0284c7;
    box-shadow: 0 0 0 4px rgba(2, 132, 199, 0.15);
  }
  textarea.input-box {
    height: 130px;
    resize: vertical;
  }

  .scan-btn {
    background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
    color: white;
    font-weight: 700;
    font-size: 16px;
    padding: 14px 28px;
    border-radius: 12px;
    border: none;
    cursor: pointer;
    width: 100%;
    margin-top: 18px;
    box-shadow: 0 4px 14px rgba(2, 132, 199, 0.3);
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    letter-spacing: 0.5px;
  }
  .scan-btn:hover {
    background: linear-gradient(135deg, #0369a1 0%, #075985 100%);
    transform: translateY(-1px);
    box-shadow: 0 6px 18px rgba(2, 132, 199, 0.4);
  }

  /* Result Card */
  .verity-result {
    background: white;
    border-radius: 20px;
    padding: 26px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 20px rgba(0,0,0,0.04);
    margin-top: 24px;
  }
  .result-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
  }
  .verity-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 16px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 13px;
  }
  .v-badge-green { background: #dcfce7; color: #15803d; border: 1px solid #bbf7d0; }
  .v-badge-red { background: #fee2e2; color: #b91c1c; border: 1px solid #fecaca; }

  .verity-score-pill {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 18px;
    border-radius: 12px;
    font-weight: 800;
    font-size: 18px;
  }
  .pill-green { color: #16a34a; border: 1px solid #bbf7d0; background: #f0fdf4; }
  .pill-red { color: #dc2626; border: 1px solid #fecaca; background: #fef2f2; }
  .pill-yellow { color: #d97706; border: 1px solid #fde68a; background: #fffbeb; }

  .check-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-top: 18px;
    padding-top: 18px;
    border-top: 1px solid #f1f5f9;
  }
  .check-item {
    background: #f8fafc;
    padding: 14px 18px;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    font-size: 13px;
    color: #334155;
  }

  .extracted-preview {
    background: #f8fafc;
    padding: 14px 18px;
    border-radius: 12px;
    font-size: 13px;
    color: #475569;
    border: 1px solid #e2e8f0;
    margin-top: 8px;
    max-height: 140px;
    overflow-y: auto;
  }

  .error-box {
    color: #b91c1c;
    background: #fee2e2;
    padding: 16px 20px;
    border-radius: 14px;
    border: 1px solid #fecaca;
    margin-top: 20px;
    font-size: 14px;
    font-weight: 600;
  }
</style>
"""

INDEX_PAGE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>NUCLEAR REBUILD — Real / Fake News Detector</title>
  """ + STYLE + """
</head>
<body>
  <div class="header-card">
    <div class="brand-logo">
      <div class="brand-icon">☢️</div>
      NUCLEAR REBUILD — Real / Fake News Detector
    </div>
  </div>

  <div class="input-card">
    <div class="tabs-bar">
      <button class="tab-item active" onclick="switchTab('text')">📝 Paste News Text</button>
      <button class="tab-item" onclick="switchTab('url')">🔗 News Link</button>
      <button class="tab-item" onclick="switchTab('image')">🖼️ Upload Image</button>
    </div>

    <!-- TAB 1: PASTE NEWS TEXT -->
    <div id="tab-text" class="tab-panel active">
      <form method="POST" action="/">
        <input type="hidden" name="mode" value="text">
        <label>Paste News Article Text:</label>
        <textarea name="text" class="input-box" placeholder="Paste news article content or claim here...">{{ input_text if mode == 'text' else '' }}</textarea>
        
        <div style="margin-top: 14px;">
          <label>Source Name (optional):</label>
          <input type="text" name="source" class="input-box" value="{{ input_source if mode == 'text' else '' }}" placeholder="e.g. BBC News, Reuters, or leave blank">
        </div>
        
        <button type="submit" class="scan-btn">Predict ⚡</button>
      </form>
    </div>

    <!-- TAB 2: NEWS LINK -->
    <div id="tab-url" class="tab-panel">
      <form method="POST" action="/">
        <input type="hidden" name="mode" value="url">
        <label>Paste News Article Link / URL:</label>
        <input type="url" name="article_url" class="input-box" placeholder="https://example.com/news/article-headline" value="{{ input_url if mode == 'url' else '' }}">
        
        <div style="margin-top: 14px;">
          <label>Source Name (optional — auto-detected from domain if blank):</label>
          <input type="text" name="source" class="input-box" value="{{ input_source if mode == 'url' else '' }}" placeholder="e.g. BBC News, The Guardian, Reuters">
        </div>
        
        <button type="submit" class="scan-btn">Predict ⚡</button>
      </form>
    </div>

    <!-- TAB 3: UPLOAD IMAGE -->
    <div id="tab-image" class="tab-panel">
      <form method="POST" action="/" enctype="multipart/form-data">
        <input type="hidden" name="mode" value="image">
        <label>Upload Screenshot / News Image (OCR):</label>
        <input type="file" name="image_file" class="input-box" accept="image/*">
        
        <div style="margin-top: 14px;">
          <label>Source Name (optional):</label>
          <input type="text" name="source" class="input-box" value="{{ input_source if mode == 'image' else '' }}" placeholder="e.g. Social Media Screenshot">
        </div>
        
        <button type="submit" class="scan-btn">Predict ⚡</button>
      </form>
    </div>
  </div>

  {% if error %}
  <div class="error-box">
    ⚠️ {{ error }}
  </div>
  {% endif %}

  {% if extracted_text %}
  <div style="margin-top: 18px;">
    <label style="color:#64748b; font-size:13px;">Extracted Text Used For Scan:</label>
    <div class="extracted-preview">{{ extracted_text }}</div>
  </div>
  {% endif %}

  {% if result %}
  <div class="verity-result">
    <div class="result-top">
      <div>
        {% if result.classifier_prediction == "Real" %}
          <div style="font-size:32px; font-weight:900; color:#15803d; letter-spacing:1px;">REAL</div>
        {% else %}
          <div style="font-size:32px; font-weight:900; color:#b91c1c; letter-spacing:1px;">FAKE</div>
        {% endif %}
      </div>

      <div class="verity-score-pill {{ 'pill-green' if result.trust_score_result.trust_score >= 70 else ('pill-yellow' if result.trust_score_result.trust_score >= 40 else 'pill-red') }}">
        <span>Trust Score</span>
        <span>{{ result.trust_score_result.trust_score }}/100</span>
        {% if result.trust_score_result.trust_score >= 70 %}
          <span>✓</span>
        {% elif result.trust_score_result.trust_score >= 40 %}
          <span>ℹ️</span>
        {% else %}
          <span>⚠️</span>
        {% endif %}
      </div>
    </div>

    <div class="check-grid">
      <div class="check-item">
        <b>AI Writing Check:</b> {{ simplified.ai_check }}
      </div>
      <div class="check-item">
        <b>Source Reputation:</b> {{ simplified.src_check }}
      </div>
      <div class="check-item">
        <b>Official Fact Match:</b> {{ simplified.fact_check }}
      </div>
      <div class="check-item">
        <b>Article Language:</b> {{ simplified.tone_check }}
      </div>
    </div>
  </div>
  {% endif %}

  <script>
    function switchTab(modeName) {
      document.querySelectorAll('.tab-panel').forEach(panel => panel.classList.remove('active'));
      document.querySelectorAll('.tab-item').forEach(btn => btn.classList.remove('active'));
      
      document.getElementById('tab-' + modeName).classList.add('active');
      event.currentTarget.classList.add('active');
    }

    // Preserve active tab after form submission
    const currentMode = "{{ mode }}";
    if (currentMode) {
      document.querySelectorAll('.tab-panel').forEach(panel => panel.classList.remove('active'));
      document.querySelectorAll('.tab-item').forEach(btn => btn.classList.remove('active'));
      
      const tabTarget = document.getElementById('tab-' + currentMode);
      if (tabTarget) tabTarget.classList.add('active');
      
      const modeIdx = {text: 0, url: 1, image: 2}[currentMode];
      const btnTarget = document.querySelectorAll('.tab-item')[modeIdx];
      if (btnTarget) btnTarget.classList.add('active');
    }
  </script>
</body>
</html>
"""


def _guess_source_from_url(url: str) -> str:
    """Very light heuristic: pull the domain name as a fallback source label."""
    try:
        domain = url.split("//")[-1].split("/")[0].lower()
        domain = domain.replace("www.", "")
        if "reuters" in domain:
            return "Reuters"
        if "bbc" in domain:
            return "BBC News"
        if "theguardian" in domain:
            return "The Guardian"
        return domain
    except Exception:
        return ""


def _format_simplified_breakdown(components: dict) -> dict:
    """Formats scores into simple everyday terms for any non-technical reader."""
    conf = float(components.get("model_confidence", 0))
    src = float(components.get("source_credibility", 0))
    corr = float(components.get("corroboration_score", 0))
    neut = float(components.get("sentiment_neutrality", 0))
    
    ai_check = "🟢 Authentic Writing" if conf >= 0.6 else "🔴 Suspicious Writing"
    src_check = "🟢 Trusted Publisher" if src >= 0.7 else ("🟡 Known Source" if src >= 0.4 else "🔴 Unverified Source")
    fact_check = "🟢 Confirmed Claims" if corr >= 0.6 else "🔴 Needs Fact-Check"
    tone_check = "🟢 Calm & Neutral" if neut >= 0.6 else "🔴 Emotional / Biased"
    
    return {
        "ai_check": ai_check,
        "src_check": src_check,
        "fact_check": fact_check,
        "tone_check": tone_check,
    }


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    extracted_text = None
    mode = "text"
    input_text = ""
    input_url = ""
    input_source = ""
    simplified = {}

    if request.method == "POST":
        mode = request.form.get("mode", "text")
        input_source = request.form.get("source", "").strip()

        try:
            if mode == "text":
                input_text = request.form.get("text", "").strip()
                if not input_text:
                    raise Exception("Please enter or paste news article text to analyze.")
                text_to_analyze = input_text

            elif mode == "url":
                input_url = request.form.get("article_url", "").strip()
                if not input_url:
                    raise Exception("Please enter a news article link.")
                if not re.match(r"^(https?://|file://)", input_url, re.IGNORECASE):
                    input_url = "https://" + input_url
                    
                scraper_key = detector.config.get("scraping", {}).get("scraperapi_key", "")
                article = extract_article_text(input_url, scraperapi_key=scraper_key)
                text_to_analyze = article["text"]
                extracted_text = text_to_analyze
                if not input_source:
                    input_source = _guess_source_from_url(input_url)

            elif mode == "image":
                file = request.files.get("image_file")
                if not file or not file.filename:
                    raise Exception("Please choose an image file to upload.")
                text_to_analyze = extract_text_from_image(file.read())
                extracted_text = text_to_analyze

            else:
                text_to_analyze = ""

            if text_to_analyze and text_to_analyze.strip():
                result = detector.predict(text_to_analyze, input_source)
                components = result["trust_score_result"]["components"]
                simplified = _format_simplified_breakdown(components)

        except Exception as e:
            error = str(e)

    return render_template_string(
        INDEX_PAGE,
        result=result,
        error=error,
        extracted_text=extracted_text,
        mode=mode,
        input_text=input_text,
        input_url=input_url,
        input_source=input_source,
        simplified=simplified,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
