from flask import Flask, request, jsonify
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import langid
import logging

app = Flask(__name__)
CORS(app, origins=["chrome-extension://bimmfidddgmilcgmmefgbpfjbkjefeeg"])

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def fetch_content(url):
    """Fetch JavaScript-rendered content using Selenium + BeautifulSoup."""
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--log-level=3")

        # Automatically download and use the latest ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        driver.get(url)  # Open the URL
        driver.implicitly_wait(5)  # Wait for JavaScript to load

        soup = BeautifulSoup(driver.page_source, "html.parser")  # Parse the page
        driver.quit()  # Close the browser

        return soup.get_text()
    except Exception as e:
        raise RuntimeError(f"Failed to fetch URL: {str(e)}")

@app.route('/detect-language', methods=['POST'])
def detect_language_from_url():
    try:
        # Get URL from the request
        data = request.json
        logging.debug(f"Received request: {data}")
        url = data.get('url', '')
        target_language = data.get('target_language')

        if not url:
            return jsonify({'error': 'No URL provided'}), 400

        # Fetch and process text
        try:
            text = fetch_content(url)
            logging.debug(f"Fetched content from URL: {url}")
        except Exception as e:
            return jsonify({'error': str(e)}), 500

        # Process text and detect languages
        language_counts = {}
        language_words = []

        for sentence in text.split('.'):
            sentence = sentence.strip()
            if not sentence:
                continue

            for word in sentence.split():
                if word.isdigit() or len(word) == 1:
                    continue

                try:
                    lang = langid.classify(word)[0]
                    language_counts[lang] = language_counts.get(lang, 0) + 1
                    if lang == target_language:
                        language_words.append(word + " ")
                except Exception:
                    pass

        return jsonify({'language_counts': language_counts, 'language_words': language_words})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000)
