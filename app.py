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
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    # Автоматический поиск путей к бинарникам в системе
    chrome_path = shutil.which("google-chrome") or shutil.which("chrome") or "/usr/bin/google-chrome"
    driver_path = shutil.which("chromedriver") or "/usr/bin/chromedriver"
    
    chrome_options.binary_location = chrome_path
    
    driver = None
    try:
        # Используем найденный системный путь к драйверу
        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        driver.set_page_load_timeout(30)
        driver.get(url)
        
        wait = WebDriverWait(driver, 15)
        title_el = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.top-card-layout__title, .topcard__title, h1")))
        
        title = title_el.text.strip()
        company = "Не найдена"
        try:
            comp_el = driver.find_element(By.CSS_SELECTOR, "a.topcard__org-name-link, .topcard__flavor a")
            company = comp_el.text.strip()
        except:
            pass

        return {"title": title, "company": company, "status": "success"}

    except Exception as e:
        # Выводим подробности ошибки в логи для отладки
        print(f"DEBUG: Chrome path: {chrome_path}")
        print(f"DEBUG: Driver path: {driver_path}")
        return {"error": str(e), "status": "error"}
    finally:
        if driver:
            driver.quit()

@app.route('/')
def index():
    return "Parser is Active"

@app.route('/parse')
def parse():
    job_url = request.args.get('url')
    if not job_url:
        return jsonify({"error": "No URL"}), 400
    return jsonify(get_linkedin_data(job_url))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
