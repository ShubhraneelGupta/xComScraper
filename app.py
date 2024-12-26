import os
from flask import Flask, jsonify, request
import time
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from dotenv import load_dotenv
import pymongo
from uuid import uuid4

load_dotenv('./.env')

# MongoDB connection setup
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")
client = pymongo.MongoClient(
    f"mongodb+srv://neel2002:{MONGODB_PASSWORD}@xcomscraper.nxbme.mongodb.net/?retryWrites=true&w=majority&appName=xcomscraper",
)
db = client["xcomscraper"]
collection = db["trending_data"]

app = Flask(__name__)
CORS(app)
PROXYMESH_USER_NAME = os.getenv("PROXYMESH_USER_NAME")
PROXYMESH_PASSWORD = os.getenv("PROXYMESH_PASSWORD")
PROXYMESH_URL = f"http://{PROXYMESH_USER_NAME}:{PROXYMESH_PASSWORD}@sg.proxymesh.com:31280"
XCOM_USERNAME = os.getenv("XCOM_USERNAME")
XCOM_PASSWORD = os.getenv("XCOM_PASSWORD")

# Configure Chrome options
options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--headless")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=2560,1440")
# Set up proxy for Selenium WebDriver
# options.add_argument('--proxy-server=%s' % PROXYMESH_URL)


# Start Selenium WebDriver with Proxy
service = Service("/usr/bin/chromedriver")


@app.route("/api/my-ip")
def my_ip():
    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://www.whatismyip.net/")
    time.sleep(1)
    ip_addr = driver.find_element(By.ID, "userip").text
    return ip_addr


@app.route("/api/scrape")
def home():
    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://x.com")

    time.sleep(3)
    driver.find_element(By.CSS_SELECTOR, '[data-testid="loginButton"]').click()

    time.sleep(5)
    driver.find_element(By.TAG_NAME, "input").send_keys(f"{XCOM_USERNAME}\n")

    time.sleep(5)
    driver.find_element(By.CSS_SELECTOR, '[autocomplete="current-password"]').send_keys(F"{XCOM_PASSWORD}\n")

    show_more = WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[href="/explore/tabs/for-you"]')))
    show_more = driver.find_element(By.CSS_SELECTOR, '[href="/explore/tabs/for-you"]')
    show_more.click()

    trends = WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[data-testid="trend"]')))
    trends = driver.find_elements(By.CSS_SELECTOR, '[data-testid="trend"]')
    return [trend.text for trend in trends[:5]]


@app.route("/api/save", methods=['POST'])
def save_data():
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ["id", "trend1", "trend2", "trend3", "trend4", "trend5", "ip", "datetime"]
        missing_fields = [field for field in required_fields if field not in data or not data[field]]

        if missing_fields:
            return jsonify({"error": f"Missing or empty fields: {', '.join(missing_fields)}"}), 400

        # Prepare document for insertion
        document = {
            "id": data["id"],
            "trend1": data["trend1"],
            "trend2": data["trend2"],
            "trend3": data["trend3"],
            "trend4": data["trend4"],
            "trend5": data["trend5"],
            "ip": data["ip"],
            "datetime": data["datetime"],
        }

        # Insert document into MongoDB
        collection.insert_one(document)

        return jsonify({"message": "Data saved successfully"}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

# Bind to Railway's dynamic port
PORT = int(os.environ.get("PORT", 8000))
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
