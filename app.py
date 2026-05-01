import os
import shutil
from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
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
    
    # Очень важно для Railway: явно указываем, где лежит сам Chrome
    chrome_path = shutil.which("google-chrome") or shutil.which("chrome") or "/usr/bin/google-chrome"
    chrome_options.binary_location = chrome_path

    driver = None
    try:
        # В этой версии Selenium (4.11+) мы не передаем executable_path в Service, 
        # если драйвер уже есть в системном PATH (/usr/bin/chromedriver)
        driver = webdriver.Chrome(options=chrome_options)
        
        driver.set_page_load_timeout(20)
        driver.get(url)
        
        wait = WebDriverWait(driver, 10)
        # Упрощенный поиск заголовка
        title_el = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        title = title_el.text.strip()
        
        return {"title": title, "status": "success"}

    except Exception as e:
        # Если снова будет ошибка "Unable to obtain driver", 
        # мы увидим подробности в логах
        print(f"FAILED. Chrome: {chrome_path}")
        return {"error": str(e), "status": "error"}
    finally:
        if driver:
            driver.quit()

@app.route('/parse')
def parse():
    job_url = request.args.get('url')
    if not job_url:
        return jsonify({"error": "No URL"}), 400
    return jsonify(get_linkedin_data(job_url))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
