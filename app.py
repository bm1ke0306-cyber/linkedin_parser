import os
from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

def get_linkedin_data(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Railway/Docker специфичная настройка
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 15)
        
        # Поиск заголовка
        title_el = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.top-card-layout__title, .topcard__title, h1")))
        
        # Поиск компании
        try:
            comp_el = driver.find_element(By.CSS_SELECTOR, "a.topcard__org-name-link, [data-tracking-control-name='public_jobs_topcard_org_name'], .topcard__flavor a")
            company = comp_el.text.strip()
        except:
            company = "Не найдена"

        return {"title": title_el.text.strip(), "company": company}
    except Exception as e:
        return {"error": str(e)}
    finally:
        driver.quit()

@app.route('/parse')
def parse():
    job_url = request.args.get('url')
    if not job_url:
        return jsonify({"error": "No URL provided"}), 400
    result = get_linkedin_data(job_url)
    return jsonify(result)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)