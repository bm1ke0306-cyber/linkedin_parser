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
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    chrome_options.binary_location = "/usr/bin/google-chrome"
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(20)
        driver.get(url)
        
        wait = WebDriverWait(driver, 15)
        
        # --- ПОИСК ЗАГОЛОВКА ---
        title = "Не найдено"
        try:
            title_el = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
            title = title_el.text.strip()
        except:
            pass

        # --- ПОИСК КОМПАНИИ (ПЕРЕБОРОМ СЕЛЕКТОРОВ) ---
        company = "Не найдена"
        company_selectors = [
            "span.topcard__flavor", 
            "a.topcard__org-name-link",
            "a[data-tracking-control-name='public_jobs_topcard_org_name']",
            ".top-card-layout__first-subline a",
            ".base-main-card__subtitle",
            "span.top-card-layout__first-subline"
        ]
        
        for selector in company_selectors:
            try:
                el = driver.find_element(By.CSS_SELECTOR, selector)
                text = el.text.strip()
                if text:
                    # Чистим текст от лишних слов (например, если там "Company Name • Location")
                    company = text.split('\n')[0].split(' • ')[0]
                    break
            except:
                continue
        
        return {"title": title, "company": company, "status": "success"}

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
