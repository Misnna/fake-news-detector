import requests
import os
import sys

BASE_URL = "http://localhost:5000"

def test_paste_text_real():
    print("Testing Case 1 (Text - Real)...")
    payload = {
        "mode": "text",
        "text": "IAEA Incident and Emergency Centre reports confirm that radiation readings near Sizewell B remain unchanged after routine maintenance.",
        "source": "BBC News"
    }
    resp = requests.post(f"{BASE_URL}/", data=payload)
    assert resp.status_code == 200, f"Request failed: {resp.status_code}"
    html = resp.text
    assert "REAL" in html or "Credible" in html, "Failed to predict 'Real' or 'Credible'"
    assert "BBC News" in html, "BBC News source missing from response"
    print("  => Success: Paste Text (Real) works!")

def test_paste_text_fake():
    print("Testing Case 2 (Text - Fake)...")
    payload = {
        "mode": "text",
        "text": "BREAKING: Sizewell B is leaking massive amounts of radiation and officials are covering it up!!!",
        "source": "Random Telegram Channel"
    }
    resp = requests.post(f"{BASE_URL}/", data=payload)
    assert resp.status_code == 200, f"Request failed: {resp.status_code}"
    html = resp.text
    assert "FAKE" in html or "Misinformation" in html, "Failed to predict Fake/Misinformation"
    assert "Random Telegram Channel" in html, "Source missing from response"
    print("  => Success: Paste Text (Fake) works!")

def test_honest_uncertainty():
    print("Testing Case 3 (Honest Uncertainty - Section 7)...")
    payload = {
        "mode": "text",
        "text": "A specialized water pump gasket was replaced during routine work at an unverified workshop.",
        "source": "News Report"
    }
    resp = requests.post(f"{BASE_URL}/", data=payload)
    assert resp.status_code == 200, f"Request failed: {resp.status_code}"
    html = resp.text
    assert "INSUFFICIENT VERIFICATION DATA" in html or "Insufficient Verification Data" in html, "Failed to flag honest uncertainty"
    print("  => Success: Honest Uncertainty ('Insufficient Verification Data') works!")

def test_news_url():
    print("Testing Case 4 (News URL - Link)...")
    local_url = "file:///c:/Users/USER/Desktop/misna/nuclear_fake_news_detector/nuclear_fake_news_detector/fake_test.html"
    payload = {
        "mode": "url",
        "article_url": local_url,
        "source": "SecretTruthNews.biz"
    }
    resp = requests.post(f"{BASE_URL}/", data=payload)
    assert resp.status_code == 200, f"Request failed: {resp.status_code}"
    html = resp.text
    assert "FAKE" in html or "Misinformation" in html, "Failed to predict Fake/Misinformation"
    assert "extracted-preview" in html, "Text extraction preview missing"
    assert "SecretTruthNews.biz" in html, "Source missing from response"
    print("  => Success: News URL Link extraction and analysis works!")

def test_upload_image():
    print("Testing Case 5 (Upload Image - OCR)...")
    image_path = os.path.join(os.path.dirname(__file__), "..", "fake_news_test_image.png")
    image_path = os.path.abspath(image_path)
    
    if not os.path.exists(image_path):
        print(f"  => Skip: {image_path} not found.")
        return
        
    payload = {
        "mode": "image",
        "source": "Random Telegram Channel"
    }
    with open(image_path, "rb") as img:
        files = {"image_file": img}
        resp = requests.post(f"{BASE_URL}/", data=payload, files=files)
        
    assert resp.status_code == 200, f"Request failed: {resp.status_code}"
    html = resp.text
    assert "extracted-preview" in html, "OCR text extraction preview missing"
    assert "verity-result" in html or "verity-score-pill" in html, "Result card missing from image analysis"
    print("  => Success: Image Upload OCR extraction and analysis works!")

if __name__ == "__main__":
    try:
        test_paste_text_real()
        test_paste_text_fake()
        test_honest_uncertainty()
        test_news_url()
        test_upload_image()
        print("\nAll integration tests passed successfully!")
    except AssertionError as e:
        print(f"\nAssertion Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected Error: {e}")
        sys.exit(1)
