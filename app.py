import os
import shutil
from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)

def get_linkedin_data(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    # В этом Docker-образе пути всегда такие:
    chrome_options.binary_location = "/usr/bin/google-chrome"
    
    driver = None
    try:
        # Selenium сам найдет chromedriver, установленный в систему
        driver = webdriver.Chrome(options=chrome_options)
        
        driver.set_page_load_timeout(20)
        driver.get(url)
        
        wait = WebDriverWait(driver, 10)
        title_el = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        
        return {"title": title_el.text.strip(), "status": "success"}

    except Exception as e:
        return {"error": str(e), "status": "error"}
    finally:
        if driver:
            driver.quit()

@app.route('/parse')
def parse():
    job_url = request.args.get('url')
    if not job_url: return jsonify({"error": "No URL"}), 400
    return jsonify(get_linkedin_data(job_url))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
