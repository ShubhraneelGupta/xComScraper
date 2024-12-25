import os
from flask import Flask, jsonify, request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.proxy import Proxy, ProxyType

app = Flask(__name__)

PROXYMESH_USER_NAME = os.getenv("PROXYMESH_USER_NAME")
PROXYMESH_PASSWORD = os.getenv("PROXYMESH_PASSWORD")
PROXYMESH_URL = f"http://{PROXYMESH_USER_NAME}:{PROXYMESH_PASSWORD}in.proxymesh.com:31280"

# Configure Chrome options
options = Options()
options.add_argument("--headless")  # Run in headless mode
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920x1080")

# Set up proxy for Selenium WebDriver
options.add_argument('--proxy-server=http://%s' % PROXYMESH_URL)


# Start Selenium WebDriver with Proxy
service = Service("/usr/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=options)


@app.route("/")
def home():
    url_used = driver.get("https://whatismyipaddress.com").title
    return url_used


@app.route("/scrape", methods=["POST"])
def scrape():
    # Get the URL from the request
    data = request.json
    url = data.get("url")
    if not url:
        return jsonify({"error": "URL is required"}), 400

    try:
        driver.get(url)
        title = driver.title
        driver.quit()
        return jsonify({"title": title})
    except Exception as e:
        driver.quit()
        return jsonify({"error": str(e)}), 500


# Bind to Railway's dynamic port
PORT = int(os.environ.get("PORT", 8000))
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
