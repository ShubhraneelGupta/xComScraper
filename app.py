import os
from flask import Flask, jsonify, request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from flask_cors import CORS
from selenium.webdriver.common.proxy import Proxy, ProxyType

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "Scraper API is up and running!"

@app.route("/scrape", methods=["POST"])
def scrape():
    # Get the URL from the request
    data = request.json
    url = data.get("url")
    if not url:
        return jsonify({"error": "URL is required"}), 400

    # Get ProxyMesh credentials from environment variables
    PROXYMESH_USER_NAME = os.getenv("PROXYMESH_USER_NAME")
    PROXYMESH_PASSWORD = os.getenv("PROXYMESH_PASSWORD")

    if not PROXYMESH_USER_NAME or not PROXYMESH_PASSWORD:
        return jsonify({"error": "ProxyMesh credentials are missing"}), 400

    # Create ProxyMesh URL using the credentials
    PROXYMESH_URL = f"http://{PROXYMESH_USER_NAME}:{PROXYMESH_PASSWORD}@in.proxymesh.com:31280"

    # Configure Chrome options
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")

    # Set up proxy for Selenium WebDriver
    proxy = Proxy()
    proxy.proxy_type = ProxyType.MANUAL
    proxy.http_proxy = PROXYMESH_URL
    proxy.ssl_proxy = PROXYMESH_URL

    capabilities = webdriver.DesiredCapabilities.CHROME
    proxy.add_to_capabilities(capabilities)

    # Start Selenium WebDriver with Proxy
    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options, desired_capabilities=capabilities)

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
