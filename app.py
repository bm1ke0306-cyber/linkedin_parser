import os
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
    # Базовые настройки для работы в Docker/Railway
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    # Имитируем реального пользователя
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Явно указываем путь к Chrome для Nixpacks (Railway)
    chrome_options.binary_location = "/usr/bin/google-chrome"
    
    driver = None
    try:
        # В Nixpacks chromedriver уже в PATH, поэтому Service указывать не обязательно
        driver = webdriver.Chrome(options=chrome_options)
        
        # Устанавливаем таймаут загрузки страницы
        driver.set_page_load_timeout(30)
        driver.get(url)
        
        wait = WebDriverWait(driver, 15)
        
        # 1. Ищем название вакансии (несколько вариантов селекторов)
        title_selectors = [
            "h1.top-card-layout__title", 
            ".topcard__title", 
            "h1", 
            "h2.top-card-layout__title"
        ]
        title = "Не найдено"
        for selector in title_selectors:
            try:
                el = driver.find_element(By.CSS_SELECTOR, selector)
                if el.text.strip():
                    title = el.text.strip()
                    break
            except:
                continue
        
        # 2. Ищем название компании
        company_selectors = [
            "a.topcard__org-name-link", 
            ".topcard__flavor a", 
            ".top-card-layout__first-subline a",
            "[data-tracking-control-name='public_jobs_topcard_org_name']"
        ]
        company = "Не найдена"
        for selector in company_selectors:
            try:
                el = driver.find_element(By.CSS_SELECTOR, selector)
                if el.text.strip():
                    company = el.text.strip()
                    break
            except:
                continue

        return {"title": title, "company": company, "status": "success"}

    except Exception as e:
        return {"error": str(e), "status": "error"}
    
    finally:
        if driver:
            driver.quit()

@app.route('/')
def health_check():
    return "Server is running!", 200

@app.route('/parse')
def parse():
    job_url = request.args.get('url')
    if not job_url:
        return jsonify({"error": "No URL provided", "status": "error"}), 400
    
    # Небольшая проверка корректности URL
    if "linkedin.com" not in job_url:
        return jsonify({"error": "Not a LinkedIn URL", "status": "error"}), 400
        
    result = get_linkedin_data(job_url)
    return jsonify(result)

if __name__ == "__main__":
    # Читаем порт из переменной окружения (Railway ставит его сам)
    # По умолчанию используем 8080, как вы и просили
    port = int(os.environ.get("PORT", 8080))
    # host='0.0.0.0' критически важен для доступа извне
    app.run(host='0.0.0.0', port=port, debug=False)
