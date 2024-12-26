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

load_dotenv('./.env')

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
options.add_argument("--window-size=1920,1080")
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


# Bind to Railway's dynamic port
PORT = int(os.environ.get("PORT", 8000))
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
