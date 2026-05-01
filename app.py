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
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Явно указываем пути для Railway
    chrome_options.binary_location = "/usr/bin/google-chrome"
    
    driver = None
    try:
        # Указываем путь к chromedriver вручную
        service = Service(executable_path="/usr/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        driver.set_page_load_timeout(30)
        driver.get(url)
        
        # ... далее ваш код поиска title и company без изменений ...
        wait = WebDriverWait(driver, 15)
        title_el = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.top-card-layout__title, .topcard__title, h1")))
        title = title_el.text.strip()
        
        try:
            comp_el = driver.find_element(By.CSS_SELECTOR, "a.topcard__org-name-link, .topcard__flavor a")
            company = comp_el.text.strip()
        except:
            company = "Не найдена"

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
